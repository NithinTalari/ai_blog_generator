from pathlib import Path
import os
import sys

from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ENV = BASE_DIR / ".env"
VENV_ENV = BASE_DIR / "venv" / ".env"
LOCAL_STORAGE_ROOT = BASE_DIR / ".crewai_storage"


def configure_environment() -> str:
    """Load environment variables and keep CrewAI storage inside the project."""
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

    # Some CrewAI modules resolve the storage path through appdirs at import time.
    # Patch the helper functions so SQLite storage stays inside this project.
    from crewai.memory.storage import kickoff_task_outputs_storage
    from crewai.utilities import paths as crewai_paths

    crewai_paths.db_storage_path = lambda: str(crewai_db_dir)
    kickoff_task_outputs_storage.db_storage_path = lambda: str(crewai_db_dir)

    hf_token = (
        os.getenv("HF_TOKEN")
        or os.getenv("HUGGINGFACE_API_TOKEN")
        or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    )
    if not hf_token:
        raise RuntimeError(
            "Missing Hugging Face token. Add HF_TOKEN or HUGGINGFACE_API_TOKEN to .env."
        )

    os.environ["HF_TOKEN"] = hf_token
    return hf_token


def build_crew(hf_token: str, topic: str) -> Crew:
    llm = LLM(
        model="huggingface/Qwen/Qwen2.5-7B-Instruct",
        api_key=hf_token,
        temperature=0.7,
        max_tokens=512,
    )

    researcher = Agent(
        role="Research Analyst",
        goal=f"Find useful, accurate information about {topic}",
        backstory="An expert researcher who extracts clear, relevant insights.",
        llm=llm,
        verbose=False,
    )

    writer = Agent(
        role="Blog Writer",
        goal=f"Write an engaging, easy-to-read blog post about {topic}",
        backstory="A creative writer who turns research into structured articles.",
        llm=llm,
        verbose=False,
    )

    editor = Agent(
        role="Editor",
        goal="Improve clarity, grammar, and overall readability",
        backstory="A professional editor focused on polished final drafts.",
        llm=llm,
        verbose=False,
    )

    research_task = Task(
        description=(
            f"Research the topic '{topic}'. Find the most useful facts, ideas, "
            "key trends, and practical insights for a blog post."
        ),
        expected_output="A concise research summary with bullet points.",
        agent=researcher,
    )

    write_task = Task(
        description=(
            f"Write a blog post on '{topic}' using the research provided. "
            "Include a title, introduction, clear section headings, and a conclusion."
        ),
        expected_output="A well-structured blog post draft.",
        agent=writer,
        context=[research_task],
    )

    edit_task = Task(
        description=(
            "Edit the draft for grammar, clarity, flow, and readability while "
            "preserving the main ideas."
        ),
        expected_output="A polished final blog post.",
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


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    configure_environment()

    topic = input("Enter blog topic: ").strip()
    if not topic:
        raise ValueError("Blog topic cannot be empty.")

    hf_token = os.environ["HF_TOKEN"]
    crew = build_crew(hf_token, topic)

    print("\nGenerating blog...\n")
    result = crew.kickoff()

    print("\nFinal Output:\n")
    print(result)


if __name__ == "__main__":
    main()
