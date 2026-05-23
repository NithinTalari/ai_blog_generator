from __future__ import annotations

import json
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from main import configure_environment, generate_blog_payload, normalize_image_briefs


def main() -> None:
    raw_payload = sys.stdin.read().strip() or "{}"
    data = json.loads(raw_payload)

    topic = str(data.get("topic", "")).strip()
    if not topic:
        raise ValueError("Blog topic cannot be empty.")

    category = str(data.get("category", "Technology")).strip() or "Technology"
    tone = str(data.get("tone", "Professional")).strip() or "Professional"
    image_briefs = normalize_image_briefs(data.get("imageBriefs"))

    configure_environment()
    payload = generate_blog_payload(topic, category, tone, image_briefs)
    sys.stdout.write(json.dumps(payload))


if __name__ == "__main__":
    main()
