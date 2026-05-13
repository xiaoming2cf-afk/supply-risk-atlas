from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


DEFAULT_API_URL = "https://supply-risk-atlas-api.onrender.com/api/v1"
DEFAULT_WEB_URL = "https://supply-risk-atlas-web.onrender.com"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check deployed API/Web commit visibility without printing raw payloads.")
    parser.add_argument("--expected-commit", default=None, help="Expected git commit SHA. Defaults to local HEAD when available.")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API base URL ending in /api/v1.")
    parser.add_argument("--web-url", default=DEFAULT_WEB_URL, help="Web origin URL.")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    expected_commit = _clean_commit(args.expected_commit or local_git_commit())
    api_result = fetch_api_version(args.api_url, args.timeout)
    web_result = fetch_web_commit_presence(args.web_url, expected_commit, args.timeout)
    api_commit = _clean_commit(str(api_result.get("git_commit") or "unknown"))

    status = "verified"
    warnings: list[str] = []
    if expected_commit == "unknown":
        status = "not_verified"
        warnings.append("expected_commit_unknown")
    if api_commit == "unknown":
        status = "stale_or_unverified"
        warnings.append("api_commit_unknown")
    elif expected_commit != "unknown" and api_commit != expected_commit:
        status = "stale_or_unverified"
        warnings.append("api_commit_mismatch")
    if web_result["status"] != "verified":
        status = "stale_or_unverified"
        warnings.append(str(web_result["status"]))

    report = {
        "status": status,
        "expected_commit": expected_commit,
        "api": {
            "status": api_result.get("status", "failed"),
            "git_commit": api_commit,
            "app_version": api_result.get("app_version", "unknown"),
            "environment": api_result.get("environment", "unknown"),
            "latency_class": api_result.get("latency_class", "failed"),
        },
        "web": web_result,
        "warnings": sorted(set(warnings)),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "verified" else 1


def fetch_api_version(api_url: str, timeout: float) -> dict[str, Any]:
    url = f"{api_url.rstrip('/')}/version"
    started = time.perf_counter()
    try:
        with urlopen(Request(url, headers={"accept": "application/json"}), timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError) as exc:
        return {"status": "failed", "error": type(exc).__name__, "latency_class": "failed"}
    latency = time.perf_counter() - started
    data = body.get("data") if isinstance(body, dict) else {}
    if not isinstance(data, dict):
        data = {}
    return {
        "status": "ok" if body.get("status") == "success" else "failed",
        "git_commit": data.get("git_commit", "unknown"),
        "app_version": data.get("app_version", "unknown"),
        "environment": data.get("environment", "unknown"),
        "latency_class": latency_class(latency),
    }


def fetch_web_commit_presence(web_url: str, expected_commit: str, timeout: float) -> dict[str, Any]:
    if expected_commit == "unknown":
        return {"status": "not_verified", "commit_visible": False, "latency_class": "not_checked"}
    started = time.perf_counter()
    try:
        with urlopen(Request(web_url, headers={"accept": "text/html"}), timeout=timeout) as response:
            html = response.read(500_000).decode("utf-8", errors="replace")
    except (OSError, URLError) as exc:
        return {"status": "failed", "commit_visible": False, "error": type(exc).__name__, "latency_class": "failed"}
    latency = time.perf_counter() - started
    visible = expected_commit in html or expected_commit[:12] in html or expected_commit[:7] in html
    return {
        "status": "verified" if visible else "commit_not_visible",
        "commit_visible": visible,
        "latency_class": latency_class(latency),
    }


def local_git_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except Exception:
        return "unknown"
    return completed.stdout.strip()


def latency_class(seconds: float) -> str:
    if seconds < 1:
        return "fast"
    if seconds < 3:
        return "normal"
    if seconds < 10:
        return "slow"
    return "cold_start"


def _clean_commit(value: str) -> str:
    cleaned = "".join(character for character in value.strip() if character.isalnum())
    return cleaned if len(cleaned) >= 7 else "unknown"


if __name__ == "__main__":
    sys.exit(main())
