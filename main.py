from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
import importlib.util
from pathlib import Path
import subprocess
from urllib.parse import quote, urlparse
import json
import os
import re
import sys
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ENV = BASE_DIR / ".env"
VENV_ENV = BASE_DIR / "venv" / ".env"
LOCAL_STORAGE_ROOT = BASE_DIR / ".crewai_storage"
HOST = "127.0.0.1"
PORT = 8000
DEFAULT_GENERATION_TIMEOUT_SECONDS = 120
BACKEND_API_VERSION = 2
VENV_PYTHON = BASE_DIR / "venv" / "Scripts" / "python.exe"


def _first_non_empty_string(*values: object) -> str:
    for value in values:
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                return cleaned
    return ""


def normalize_image_briefs(raw_briefs: object) -> list[str]:
    if not isinstance(raw_briefs, list):
        return []
    return [
        item.strip()
        for item in raw_briefs
        if isinstance(item, str) and item.strip()
    ][:3]


def get_generation_timeout_seconds() -> int:
    raw_value = os.getenv("GENERATION_TIMEOUT_SECONDS", str(DEFAULT_GENERATION_TIMEOUT_SECONDS))
    try:
        timeout_seconds = int(raw_value)
    except (TypeError, ValueError):
        return DEFAULT_GENERATION_TIMEOUT_SECONDS
    return max(30, timeout_seconds)


def ensure_runtime_dependencies() -> None:
    """Always prefer the project virtualenv so the frontend talks to the expected backend."""
    current_python = Path(sys.executable).resolve()
    if VENV_PYTHON.exists():
        venv_python = VENV_PYTHON.resolve()
        if current_python != venv_python:
            os.execv(str(venv_python), [str(venv_python), *sys.argv])

    if importlib.util.find_spec("crewai") is not None:
        return

    raise RuntimeError(
        "Missing required dependency 'crewai'. Activate the project virtualenv or install dependencies there."
    )


def generate_blog_payload_via_venv(
    topic: str,
    category: str,
    tone: str,
    image_briefs: list[str] | None = None,
) -> dict:
    helper_script = BASE_DIR / "scripts" / "generate_article.py"
    python_executable = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)
    payload = {
        "topic": topic,
        "category": category,
        "tone": tone,
        "imageBriefs": image_briefs or [],
    }
    completed = subprocess.run(
        [str(python_executable), str(helper_script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
        timeout=get_generation_timeout_seconds(),
        check=False,
    )
    if completed.returncode != 0:
        error_message = completed.stderr.strip() or completed.stdout.strip() or "Unknown venv generation error."
        raise RuntimeError(error_message)

    return json.loads(completed.stdout)


def configure_environment() -> str | None:
    """Load environment variables and keep CrewAI storage inside the project."""
    if load_dotenv:
        if PROJECT_ENV.exists():
            load_dotenv(PROJECT_ENV)
        elif VENV_ENV.exists():
            load_dotenv(VENV_ENV)

    LOCAL_STORAGE_ROOT.mkdir(exist_ok=True)
    crewai_db_dir = LOCAL_STORAGE_ROOT / "db"
    crewai_db_dir.mkdir(exist_ok=True)

    # CrewAI writes SQLite and memory files under LOCALAPPDATA on Windows.
    # Point it to a local folder so the project works reliably across setups.
    os.environ["LOCALAPPDATA"] = str(LOCAL_STORAGE_ROOT)

    hf_token = (
        os.getenv("HF_TOKEN")
        or os.getenv("HUGGINGFACE_API_TOKEN")
        or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    )

    if hf_token:
        os.environ["HF_TOKEN"] = hf_token
    return hf_token


def build_crew(
    hf_token: str,
    topic: str,
    category: str,
    tone: str,
    image_briefs: list[str] | None = None,
) -> Crew:
    from crewai import Agent, Crew, LLM, Process, Task
    from crewai.memory.storage import kickoff_task_outputs_storage
    from crewai.utilities import paths as crewai_paths

    crewai_db_dir = LOCAL_STORAGE_ROOT / "db"
    crewai_paths.db_storage_path = lambda: str(crewai_db_dir)
    kickoff_task_outputs_storage.db_storage_path = lambda: str(crewai_db_dir)

    image_briefs = image_briefs or []
    image_guidance = (
        "Use these exact visual directions when creating image prompts: "
        + "; ".join(f"{index + 1}. {brief}" for index, brief in enumerate(image_briefs))
        if image_briefs
        else "Create image prompts that clearly vary in scene, composition, and storytelling angle."
    )

    llm = LLM(
        model="huggingface/Qwen/Qwen2.5-7B-Instruct",
        api_key=hf_token,
        temperature=0.6,
        max_tokens=1600,
    )

    researcher = Agent(
        role="Research Analyst",
        goal=f"Find useful, accurate information about {topic} in the {category} category.",
        backstory="An expert researcher who extracts clear, relevant insights.",
        llm=llm,
        verbose=False,
    )

    writer = Agent(
        role="Blog Writer",
        goal=f"Write an engaging, easy-to-read {tone.lower()} blog post about {topic}.",
        backstory="A creative writer who turns research into structured articles.",
        llm=llm,
        verbose=False,
    )

    editor = Agent(
        role="Editor and Visual Director",
        goal="Polish the final article, enforce structure, and suggest image prompts.",
        backstory="A professional editor focused on polished final drafts and compelling visuals.",
        llm=llm,
        verbose=False,
    )

    research_task = Task(
        description=(
            f"Research the topic '{topic}' in the {category} category. "
            "Find the most useful facts, trends, frameworks, and practical insights. "
            "Highlight points that should guide article structure and visuals. "
            f"{image_guidance}"
        ),
        expected_output="A concise research summary with key bullet points and image ideas.",
        agent=researcher,
    )

    write_task = Task(
        description=(
            f"Write a blog post on '{topic}' using the research provided. "
            f"The tone must be {tone.lower()}. Include a compelling title, introduction, "
            "two detailed sections, and a conclusion. "
            f"{image_guidance}"
        ),
        expected_output="A well-structured blog post draft.",
        agent=writer,
        context=[research_task],
    )

    edit_task = Task(
        description=(
            "Edit the draft for grammar, clarity, flow, and readability while preserving the main ideas. "
            "Return only valid JSON using this exact schema: "
            "{"
            '"title":"short dashboard label",'
            '"heading":"full article heading",'
            '"intro":"intro paragraph",'
            '"conclusion":"final concluding paragraph",'
            '"sections":[{"title":"section title","body":"section body"}, {"title":"section title","body":"section body"}],'
            '"image_prompts":[{"title":"image title","caption":"short caption","prompt":"detailed image prompt"}]'
            "} "
            "Create exactly 3 image_prompts based on the article and user topic. "
            f"{image_guidance}"
        ),
        expected_output="Valid JSON matching the requested schema.",
        agent=editor,
        context=[write_task],
    )

    return Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, write_task, edit_task],
        process=Process.sequential,
        verbose=False,
        memory=False,
    )


def strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, count=1).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned


def extract_json_candidate(text: str) -> str:
    cleaned = strip_code_fences(text)
    decoder = json.JSONDecoder()
    for index, char in enumerate(cleaned):
        if char not in "{[":
            continue
        try:
            _, end = decoder.raw_decode(cleaned[index:])
            return cleaned[index:index + end]
        except json.JSONDecodeError:
            continue
    raise json.JSONDecodeError("No JSON object found in model output.", cleaned, 0)


def parse_result_json(raw_text: str) -> dict:
    cleaned = strip_code_fences(raw_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        candidate = extract_json_candidate(cleaned)
        parsed = json.loads(candidate)
        if isinstance(parsed, list):
            if parsed and isinstance(parsed[0], dict):
                return parsed[0]
            raise ValueError("Model returned a JSON list instead of an article object.")
        if not isinstance(parsed, dict):
            raise ValueError("Model returned JSON, but not an article object.")
        return parsed


def normalize_sections(raw_sections: object) -> list[dict]:
    if not isinstance(raw_sections, list):
        return []

    normalized = []
    for index, section in enumerate(raw_sections, start=1):
        if isinstance(section, dict):
            title = _first_non_empty_string(
                section.get("title"),
                section.get("heading"),
                section.get("name"),
                f"Section {index}",
            )
            body = _first_non_empty_string(
                section.get("body"),
                section.get("content"),
                section.get("text"),
                section.get("description"),
            )
        elif isinstance(section, str):
            title = f"Section {index}"
            body = section.strip()
        else:
            continue

        if body:
            normalized.append({"title": title, "body": body})

    return normalized


def normalize_image_prompts(topic: str, raw_prompts: object) -> list[dict]:
    if not isinstance(raw_prompts, list):
        return []

    normalized = []
    for index, item in enumerate(raw_prompts, start=1):
        if isinstance(item, dict):
            prompt = _first_non_empty_string(
                item.get("prompt"),
                item.get("image_prompt"),
                item.get("description"),
                item.get("idea"),
            )
            title = _first_non_empty_string(
                item.get("title"),
                item.get("heading"),
                item.get("name"),
                f"Visual {index}",
            )
            caption = _first_non_empty_string(
                item.get("caption"),
                item.get("summary"),
                item.get("description"),
                f"Generated visual direction for {topic}",
            )
        elif isinstance(item, str):
            prompt = item.strip()
            title = f"Visual {index}"
            caption = f"Generated visual direction for {topic}"
        else:
            continue

        if prompt:
            normalized.append({"title": title, "caption": caption, "prompt": prompt})

    return normalized


def coerce_article_payload(payload: dict, topic: str) -> dict:
    sections = normalize_sections(
        payload.get("sections")
        or payload.get("body_sections")
        or payload.get("article_sections")
    )

    if not sections:
        paragraphs = [
            value.strip()
            for value in (
                payload.get("body"),
                payload.get("article"),
                payload.get("content"),
            )
            if isinstance(value, str) and value.strip()
        ]
        if paragraphs:
            sections = [{"title": "Main Section", "body": "\n\n".join(paragraphs)}]

    images = normalize_image_prompts(
        topic,
        payload.get("image_prompts")
        or payload.get("images")
        or payload.get("visuals")
        or payload.get("imageIdeas"),
    )

    return {
        "title": _first_non_empty_string(payload.get("title"), payload.get("heading"), topic),
        "heading": _first_non_empty_string(payload.get("heading"), payload.get("title"), topic),
        "intro": _first_non_empty_string(
            payload.get("intro"),
            payload.get("introduction"),
            payload.get("summary"),
            payload.get("lede"),
        ),
        "sections": sections,
        "conclusion": _first_non_empty_string(
            payload.get("conclusion"),
            payload.get("closing"),
            payload.get("final_thoughts"),
            payload.get("takeaway"),
        ),
        "images": build_image_cards(topic, images),
    }


def build_svg_image_url(topic: str, title: str, caption: str, prompt: str, seed: int) -> str:
    safe_topic = escape(topic[:58] or "AI Blog")
    safe_title = escape(title[:34] or "Visual")
    safe_caption = escape(caption[:72] or prompt[:72] or "AI generated visual direction")
    safe_prompt = escape(prompt[:96] or f"Editorial illustration about {topic}")

    palettes = [
        {
            "bg_start": "#0f0b16",
            "bg_end": "#181122",
            "glow": "#b67cff",
            "accent": "#ff9b6a",
            "line": "#3de2ff",
        },
        {
            "bg_start": "#110b17",
            "bg_end": "#191321",
            "glow": "#8f7cff",
            "accent": "#ffb26b",
            "line": "#8c7bff",
        },
        {
            "bg_start": "#100c18",
            "bg_end": "#1a1324",
            "glow": "#c58cff",
            "accent": "#ffcf7a",
            "line": "#5cd9ff",
        },
    ]
    palette = palettes[(seed - 1) % len(palettes)]

    chip_x = 560 + (seed * 18)
    chip_y = 118 + (seed * 12)

    if seed == 1:
        composition = """
  <rect x="84" y="294" width="500" height="282" rx="26" fill="rgba(13,11,20,0.96)" stroke="rgba(255,255,255,0.08)" />
  <rect x="112" y="326" width="224" height="26" rx="13" fill="rgba(255,255,255,0.05)" />
  <rect x="112" y="374" width="420" height="2" rx="1" fill="rgba(255,255,255,0.08)" />
  <rect x="86" y="392" width="34" height="118" rx="12" fill="url(#barGlow)" opacity="0.85" />
  <rect x="150" y="368" width="34" height="142" rx="12" fill="url(#barGlow)" opacity="0.85" />
  <rect x="214" y="406" width="34" height="104" rx="12" fill="url(#barGlow)" opacity="0.85" />
  <rect x="278" y="346" width="34" height="164" rx="12" fill="url(#barGlow)" opacity="0.85" />
  <rect x="342" y="378" width="34" height="132" rx="12" fill="url(#barGlow)" opacity="0.85" />
  <rect x="406" y="334" width="34" height="176" rx="12" fill="url(#barGlow)" opacity="0.85" />
  <rect x="470" y="389" width="34" height="121" rx="12" fill="url(#barGlow)" opacity="0.85" />
  <rect x="112" y="512" width="420" height="2" rx="1" fill="rgba(255,255,255,0.08)" />

  <rect x="612" y="294" width="300" height="282" rx="26" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" />
  <rect x="640" y="324" width="244" height="162" rx="22" fill="url(#halo)" stroke="rgba(255,255,255,0.1)" />
  <rect x="{chip_x}" y="{chip_y}" width="174" height="174" rx="28" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.14)" transform="rotate(14 {chip_x} {chip_y})" />
  <rect x="652" y="342" width="78" height="78" rx="20" fill="rgba(255,255,255,0.08)" />
  <rect x="744" y="342" width="112" height="18" rx="9" fill="rgba(255,255,255,0.09)" />
  <rect x="744" y="372" width="92" height="12" rx="6" fill="rgba(255,255,255,0.06)" />
  <rect x="744" y="398" width="74" height="12" rx="6" fill="rgba(255,255,255,0.06)" />

  <path d="M580 320 L610 296" stroke="{line}" stroke-width="2" stroke-linecap="round" opacity="0.7" />
  <path d="M540 548 L612 548" stroke="{line}" stroke-width="2" stroke-linecap="round" opacity="0.48" />
  <path d="M324 280 L324 610" stroke="rgba(255,255,255,0.04)" stroke-width="1" />
"""
    elif seed == 2:
        composition = """
  <rect x="84" y="294" width="396" height="282" rx="26" fill="rgba(13,11,20,0.96)" stroke="rgba(255,255,255,0.08)" />
  <path d="M110 500 C158 438 202 430 248 462 C298 497 336 506 388 446 C430 398 450 356 470 344" stroke="{line}" stroke-width="5" stroke-linecap="round" />
  <path d="M110 470 C162 420 202 414 252 444 C304 475 352 484 402 430 C430 401 453 372 470 362" stroke="{accent}" stroke-width="3" stroke-linecap="round" opacity="0.85" />
  <path d="M112 396 L450 396" stroke="rgba(255,255,255,0.08)" stroke-width="2" stroke-dasharray="8 12" />
  <path d="M112 538 L450 538" stroke="rgba(255,255,255,0.08)" stroke-width="2" stroke-dasharray="8 12" />
  <circle cx="248" cy="462" r="14" fill="{glow}" fill-opacity="0.85" />
  <circle cx="388" cy="446" r="14" fill="{accent}" fill-opacity="0.75" />

  <rect x="520" y="294" width="392" height="128" rx="24" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" />
  <rect x="548" y="324" width="146" height="70" rx="18" fill="url(#halo)" stroke="rgba(255,255,255,0.08)" />
  <rect x="718" y="324" width="166" height="18" rx="9" fill="rgba(255,255,255,0.08)" />
  <rect x="718" y="356" width="136" height="12" rx="6" fill="rgba(255,255,255,0.06)" />
  <rect x="718" y="382" width="110" height="12" rx="6" fill="rgba(255,255,255,0.06)" />

  <rect x="520" y="448" width="392" height="128" rx="24" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" />
  <rect x="548" y="474" width="72" height="74" rx="20" fill="rgba(255,255,255,0.08)" />
  <rect x="644" y="478" width="208" height="18" rx="9" fill="rgba(255,255,255,0.08)" />
  <rect x="644" y="510" width="176" height="12" rx="6" fill="rgba(255,255,255,0.06)" />
  <rect x="644" y="536" width="142" height="12" rx="6" fill="rgba(255,255,255,0.06)" />

  <rect x="{chip_x}" y="{chip_y}" width="174" height="174" rx="28" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.14)" transform="rotate(-12 {chip_x} {chip_y})" />
"""
    else:
        composition = """
  <rect x="84" y="294" width="828" height="282" rx="26" fill="rgba(13,11,20,0.96)" stroke="rgba(255,255,255,0.08)" />
  <rect x="112" y="322" width="252" height="226" rx="24" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" />
  <circle cx="238" cy="436" r="72" fill="none" stroke="{accent}" stroke-width="22" stroke-opacity="0.9" />
  <circle cx="238" cy="436" r="48" fill="none" stroke="{line}" stroke-width="18" stroke-opacity="0.75" />
  <text x="200" y="444" fill="#F7F2FF" font-family="Segoe UI, Arial, sans-serif" font-size="28" font-weight="700">84%</text>

  <rect x="396" y="322" width="244" height="226" rx="24" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" />
  <rect x="430" y="488" width="28" height="30" rx="10" fill="url(#barGlow)" opacity="0.85" />
  <rect x="476" y="452" width="28" height="66" rx="10" fill="url(#barGlow)" opacity="0.85" />
  <rect x="522" y="416" width="28" height="102" rx="10" fill="url(#barGlow)" opacity="0.85" />
  <rect x="568" y="380" width="28" height="138" rx="10" fill="url(#barGlow)" opacity="0.85" />
  <rect x="430" y="356" width="166" height="16" rx="8" fill="rgba(255,255,255,0.08)" />

  <rect x="672" y="322" width="212" height="96" rx="24" fill="url(#halo)" stroke="rgba(255,255,255,0.08)" />
  <rect x="672" y="452" width="212" height="96" rx="24" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" />
  <rect x="700" y="476" width="102" height="16" rx="8" fill="rgba(255,255,255,0.08)" />
  <rect x="700" y="506" width="154" height="12" rx="6" fill="rgba(255,255,255,0.06)" />

  <path d="M140 560 C242 610 344 602 432 566 C516 532 606 522 696 540 C778 556 842 558 900 534" stroke="{line}" stroke-width="4" stroke-linecap="round" opacity="0.65" />
"""

    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="768" viewBox="0 0 1024 768" fill="none">
  <defs>
    <linearGradient id="bg" x1="120" y1="72" x2="914" y2="684" gradientUnits="userSpaceOnUse">
      <stop stop-color="{palette["bg_start"]}" />
      <stop offset="1" stop-color="{palette["bg_end"]}" />
    </linearGradient>
    <linearGradient id="panelStroke" x1="200" y1="154" x2="840" y2="614" gradientUnits="userSpaceOnUse">
      <stop stop-color="rgba(255,255,255,0.18)" />
      <stop offset="1" stop-color="rgba(255,255,255,0.05)" />
    </linearGradient>
    <linearGradient id="barGlow" x1="86" y1="320" x2="534" y2="510" gradientUnits="userSpaceOnUse">
      <stop stop-color="{palette["accent"]}" />
      <stop offset="1" stop-color="{palette["glow"]}" />
    </linearGradient>
    <radialGradient id="halo" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(720 224) rotate(128) scale(298 266)">
      <stop stop-color="{palette["glow"]}" stop-opacity="0.42" />
      <stop offset="1" stop-color="{palette["glow"]}" stop-opacity="0" />
    </radialGradient>
    <filter id="blurGlow" x="0" y="0" width="1024" height="768" filterUnits="userSpaceOnUse">
      <feGaussianBlur stdDeviation="46" />
    </filter>
  </defs>

  <rect width="1024" height="768" rx="34" fill="url(#bg)" />
  <g opacity="0.65" filter="url(#blurGlow)">
    <circle cx="762" cy="216" r="118" fill="{palette["glow"]}" />
    <circle cx="322" cy="468" r="126" fill="{palette["accent"]}" fill-opacity="0.36" />
  </g>

  <rect x="58" y="58" width="908" height="652" rx="28" fill="rgba(18,16,26,0.88)" stroke="rgba(255,255,255,0.08)" />
  <rect x="84" y="90" width="260" height="36" rx="18" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)" />
  <circle cx="108" cy="108" r="7" fill="{palette["accent"]}" />
  <text x="128" y="115" fill="#F2DBA2" font-family="Segoe UI, Arial, sans-serif" font-size="22" font-weight="700">{safe_topic}</text>

  <rect x="84" y="154" width="856" height="112" rx="24" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.06)" />
  <text x="110" y="198" fill="#F7F2FF" font-family="Segoe UI, Arial, sans-serif" font-size="44" font-weight="700">{safe_title}</text>
  <text x="110" y="234" fill="rgba(255,255,255,0.68)" font-family="Segoe UI, Arial, sans-serif" font-size="20">{safe_caption}</text>

  {composition.format(chip_x=chip_x, chip_y=chip_y, line=palette["line"], accent=palette["accent"], glow=palette["glow"])}

  <rect x="84" y="610" width="856" height="64" rx="22" fill="rgba(255,255,255,0.025)" stroke="rgba(255,255,255,0.06)" />
  <text x="112" y="648" fill="#D8CBFF" font-family="Segoe UI, Arial, sans-serif" font-size="20" font-weight="600">Prompt</text>
  <text x="198" y="648" fill="rgba(255,255,255,0.64)" font-family="Segoe UI, Arial, sans-serif" font-size="18">{safe_prompt}</text>
</svg>
"""
    return f"data:image/svg+xml;charset=UTF-8,{quote(svg)}"


def build_image_cards(topic: str, image_prompts: list[dict]) -> list[dict]:
    image_cards = []
    for index, item in enumerate(image_prompts[:3], start=1):
        prompt = item.get("prompt") or f"Cinematic editorial illustration about {topic}"
        title = item.get("title") or f"Visual {index}"
        caption = item.get("caption") or f"Generated visual direction for {topic}"
        image_cards.append(
            {
                "id": index,
                "title": title,
                "caption": caption,
                "prompt": prompt,
                "url": build_svg_image_url(topic, title, caption, prompt, index),
            }
        )
    return image_cards


def build_fallback_image_prompt(topic: str, brief: str, index: int) -> dict:
    label = ["Hero Visual", "Insight Visual", "Closing Visual"][index - 1] if index <= 3 else f"Visual {index}"
    return {
        "title": label,
        "caption": brief,
        "prompt": (
            f"{brief}, editorial illustration about {topic}, premium dark SaaS aesthetic, "
            "cinematic lighting, polished composition"
        ),
    }


def build_fallback_payload(topic: str, category: str, tone: str, image_briefs: list[str] | None = None) -> dict:
    image_briefs = image_briefs or []
    fallback_briefs = image_briefs or [
        f"Hero image showing {topic} in a premium futuristic workspace",
        f"Supporting visual focused on analytics and trends for {topic}",
        f"Closing visual showing the future impact of {topic}",
    ]
    return {
        "title": f"{topic[:42]}..." if len(topic) > 45 else topic,
        "heading": f"{topic}: A {tone} Guide",
        "intro": (
            f"This draft explores {topic} through a {tone.lower()} lens within the {category} space. "
            "It is a fallback response generated because the structured AI response was unavailable."
        ),
        "sections": [
            {
                "title": "Why This Topic Matters",
                "body": (
                    f"{topic} is increasingly relevant for teams working in {category.lower()}, "
                    "where speed, clarity, and credibility all shape results."
                ),
            },
            {
                "title": "How To Turn Insight Into Execution",
                "body": (
                    "A strong article should combine trustworthy research, a clear narrative, "
                    "and visuals that reinforce the core message for readers."
                ),
            },
        ],
        "conclusion": (
            "With the right workflow, creators can move from idea to polished article much faster "
            "without sacrificing structure or presentation."
        ),
        "images": build_image_cards(
            topic,
            [
                build_fallback_image_prompt(topic, brief, index)
                for index, brief in enumerate(fallback_briefs[:3], start=1)
            ],
        ),
    }


def ensure_image_cards(topic: str, images: list[dict], image_briefs: list[str]) -> list[dict]:
    if len(images) >= 3:
        return images

    existing_prompts = [
        {
            "title": image.get("title") or f"Visual {index + 1}",
            "caption": image.get("caption") or image.get("prompt") or f"Generated visual direction for {topic}",
            "prompt": image.get("prompt") or image.get("caption") or f"Editorial illustration about {topic}",
        }
        for index, image in enumerate(images)
    ]

    fallback_briefs = image_briefs or [
        f"Hero image showing {topic} in a premium futuristic workspace",
        f"Supporting visual focused on analytics and trends for {topic}",
        f"Closing visual showing the future impact of {topic}",
    ]

    for index, brief in enumerate(fallback_briefs, start=1):
        if len(existing_prompts) >= 3:
            break
        existing_prompts.append(build_fallback_image_prompt(topic, brief, len(existing_prompts) + 1))

    return build_image_cards(topic, existing_prompts[:3])


def generate_blog_payload(topic: str, category: str, tone: str, image_briefs: list[str] | None = None) -> dict:
    if importlib.util.find_spec("crewai") is None:
        return generate_blog_payload_via_venv(topic, category, tone, image_briefs)

    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise RuntimeError(
            "Missing Hugging Face token. Add HF_TOKEN or HUGGINGFACE_API_TOKEN to .env."
        )

    image_briefs = image_briefs or []
    crew = build_crew(hf_token, topic, category, tone, image_briefs)
    result = crew.kickoff()
    candidate_payloads = []

    json_dict = getattr(result, "json_dict", None)
    if isinstance(json_dict, dict):
        candidate_payloads.append(json_dict)

    pydantic_value = getattr(result, "pydantic", None)
    if hasattr(pydantic_value, "model_dump"):
        dumped = pydantic_value.model_dump()
        if isinstance(dumped, dict):
            candidate_payloads.append(dumped)

    tasks_output = getattr(result, "tasks_output", None) or []
    for task_output in reversed(tasks_output):
        task_json = getattr(task_output, "json_dict", None)
        if isinstance(task_json, dict):
            candidate_payloads.append(task_json)
            break

        task_pydantic = getattr(task_output, "pydantic", None)
        if hasattr(task_pydantic, "model_dump"):
            dumped = task_pydantic.model_dump()
            if isinstance(dumped, dict):
                candidate_payloads.append(dumped)
                break

    raw_text = getattr(result, "raw", str(result))
    candidate_payloads.append(parse_result_json(raw_text))

    last_error = None
    for candidate in candidate_payloads:
        try:
            article = coerce_article_payload(candidate, topic)
            if article["sections"]:
                article["images"] = ensure_image_cards(topic, article["images"], image_briefs)
                return article
        except Exception as error:
            last_error = error

    raise ValueError(f"Model returned no usable sections. {last_error or ''}".strip())


class BlogRequestHandler(BaseHTTPRequestHandler):
    server_version = "AIBlogGenerator/1.0"

    def _set_headers(self, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _write_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        self._set_headers(status)
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_OPTIONS(self) -> None:
        self._set_headers(HTTPStatus.NO_CONTENT)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._write_json(
                {
                    "message": "AI Blog Generator backend is running.",
                    "health": "/api/health",
                    "generate": "/api/generate",
                    "method": "POST",
                }
            )
            return

        if parsed.path == "/api/health":
            current_python = Path(sys.executable).resolve()
            uses_project_venv = VENV_PYTHON.exists() and current_python == VENV_PYTHON.resolve()
            self._write_json(
                {
                    "status": "ok",
                    "apiVersion": BACKEND_API_VERSION,
                    "pythonExecutable": str(current_python),
                    "usesProjectVenv": uses_project_venv,
                    "generationTimeoutSeconds": get_generation_timeout_seconds(),
                }
            )
            return

        self._write_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/generate":
            self._write_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body or "{}")
            topic = str(data.get("topic", "")).strip()
            category = str(data.get("category", "Technology")).strip() or "Technology"
            tone = str(data.get("tone", "Professional")).strip() or "Professional"
            image_briefs = normalize_image_briefs(data.get("imageBriefs"))

            if not topic:
                self._write_json(
                    {"error": "Blog topic cannot be empty."},
                    HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                # Run generation in a subprocess so slow or stuck model work is
                # bounded per request and doesn't linger in the server process.
                payload = generate_blog_payload_via_venv(
                    topic,
                    category,
                    tone,
                    image_briefs,
                )
            except Exception as generation_error:
                payload = build_fallback_payload(topic, category, tone, image_briefs)
                if isinstance(generation_error, subprocess.TimeoutExpired):
                    payload["warning"] = (
                        "The live AI generation took too long, so a fallback article was returned."
                    )
                else:
                    payload["warning"] = (
                        "Live AI response could not be structured cleanly, so a fallback article was returned."
                    )
                payload["debug_error"] = str(generation_error)

            self._write_json(payload)
        except json.JSONDecodeError:
            self._write_json({"error": "Invalid JSON body."}, HTTPStatus.BAD_REQUEST)
        except Exception as error:
            self._write_json(
                {"error": f"Unexpected server error: {error}"},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def log_message(self, format: str, *args) -> None:
        return


def run_server() -> None:
    configure_environment()
    server = ThreadingHTTPServer((HOST, PORT), BlogRequestHandler)
    server.daemon_threads = True
    print(f"Backend server running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBackend server stopped.")
    finally:
        server.server_close()


def run_cli() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    configure_environment()

    topic = input("Enter blog topic: ").strip()
    if not topic:
        raise ValueError("Blog topic cannot be empty.")

    category = input("Enter category [Technology]: ").strip() or "Technology"
    tone = input("Enter tone [Professional]: ").strip() or "Professional"
    image_briefs = normalize_image_briefs(
        [
            input("Enter hero image direction [optional]: ").strip(),
            input("Enter supporting image direction [optional]: ").strip(),
            input("Enter closing image direction [optional]: ").strip(),
        ]
    )

    payload = generate_blog_payload(topic, category, tone, image_briefs)
    print("\nFinal Output:\n")
    print(json.dumps(payload, indent=2))


def main() -> None:
    ensure_runtime_dependencies()

    if "--cli" in sys.argv:
        run_cli()
        return

    run_server()


if __name__ == "__main__":
    main()
