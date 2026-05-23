from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8000"
DEFAULT_GENERATE_TIMEOUT_SECONDS = 150


def get_generate_timeout_seconds() -> int:
    raw_value = os.getenv("GENERATION_TIMEOUT_SECONDS")
    try:
        configured_timeout = int(raw_value) if raw_value else DEFAULT_GENERATE_TIMEOUT_SECONDS
    except (TypeError, ValueError):
        configured_timeout = DEFAULT_GENERATE_TIMEOUT_SECONDS
    return max(60, configured_timeout + 30)


def fetch_json(url: str, method: str = "GET", body: dict | None = None, timeout: int = 12) -> dict:
    payload = None
    headers = {}
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_health(retries: int = 8, delay_seconds: float = 1.25) -> None:
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            response = fetch_json(f"{BASE_URL}/api/health")
            if response.get("status") == "ok":
                print(f"Health check passed on attempt {attempt}.")
                return
        except Exception as error:  # noqa: BLE001
            last_error = error

        time.sleep(delay_seconds)

    raise RuntimeError(f"Backend health check failed. {last_error or ''}".strip())


def run_generate_smoke_test() -> None:
    payload = {
        "topic": "AI blog generator backend smoke test",
        "category": "Technology",
        "tone": "Professional",
        "imageBriefs": [
            "Hero control room with analytics glass panels",
            "Supporting visual with editorial charts and insights",
            "Closing scene showing content publication workflow",
        ],
    }
    response = fetch_json(
        f"{BASE_URL}/api/generate",
        method="POST",
        body=payload,
        timeout=get_generate_timeout_seconds(),
    )
    required_keys = {"heading", "intro", "sections", "images"}
    missing_keys = required_keys.difference(response)
    if missing_keys:
        raise RuntimeError(f"Generate endpoint returned incomplete payload: {sorted(missing_keys)}")

    print("Generate endpoint passed smoke test.")
    print(f"Heading: {response['heading']}")
    print(f"Sections: {len(response['sections'])}")
    print(f"Images: {len(response['images'])}")


def main() -> None:
    wait_for_health()
    run_generate_smoke_test()


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as error:
        raise SystemExit(f"Backend is unreachable: {error}") from error
    except Exception as error:  # noqa: BLE001
        raise SystemExit(str(error)) from error
