from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


DEFAULT_API_URL = "https://supply-risk-atlas-api.onrender.com/api/v1"
DEFAULT_WEB_URL = "https://supply-risk-atlas-web.onrender.com"
GIT_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check deployed API/Web commit visibility without printing raw payloads.")
    parser.add_argument("--expected-commit", default=None, help="Expected git commit SHA. Defaults to local HEAD when available.")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API base URL ending in /api/v1.")
    parser.add_argument("--web-url", default=DEFAULT_WEB_URL, help="Web origin URL.")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    expected_commit = _clean_commit(args.expected_commit or local_git_commit())
    api_result = fetch_api_version(args.api_url, args.timeout)
    web_html_result = fetch_web_commit_presence(args.web_url, expected_commit, args.timeout)
    web_proxy_result = fetch_web_proxy_version(args.web_url, args.timeout)
    api_commit = _clean_commit(str(api_result.get("git_commit") or "unknown"))
    web_proxy_commit = _clean_commit(str(web_proxy_result.get("git_commit") or "unknown"))

    status, warnings = deployment_status(
        expected_commit=expected_commit,
        api_result=api_result,
        api_commit=api_commit,
        web_html_result=web_html_result,
        web_proxy_result=web_proxy_result,
        web_proxy_commit=web_proxy_commit,
    )

    report = {
        "status": status,
        "deployment_status": status,
        "expected_commit": expected_commit,
        "api": {
            "status": api_result.get("status", "failed"),
            "git_commit": api_commit,
            "app_version": api_result.get("app_version", "unknown"),
            "environment": api_result.get("environment", "unknown"),
            "latency_class": api_result.get("latency_class", "failed"),
        },
        "web": {
            "html": web_html_result,
            "proxy": {
                "status": web_proxy_result.get("status", "failed"),
                "git_commit": web_proxy_commit,
                "app_version": web_proxy_result.get("app_version", "unknown"),
                "environment": web_proxy_result.get("environment", "unknown"),
                "latency_class": web_proxy_result.get("latency_class", "failed"),
            },
        },
        "warnings": sorted(set(warnings)),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "deployed_verified" else 1


def fetch_api_version(api_url: str, timeout: float) -> dict[str, Any]:
    url = f"{api_url.rstrip('/')}/version"
    started = time.perf_counter()
    try:
        with urlopen(Request(url, headers={"accept": "application/json"}), timeout=timeout) as response:
            body = json.loads(response.read(250_000).decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError, AttributeError) as exc:
        return {"status": "failed", "error": type(exc).__name__, "latency_class": "failed"}
    latency = time.perf_counter() - started
    if not isinstance(body, dict):
        return {"status": "failed", "error": "InvalidEnvelope", "latency_class": latency_class(latency)}
    data = body.get("data") if isinstance(body, dict) else {}
    if not isinstance(data, dict):
        data = {}
    return {
        "status": "ok" if body.get("status") == "success" else "failed",
        "git_commit": data.get("git_commit", "unknown"),
        "app_version": data.get("app_version", "unknown"),
        "environment": data.get("environment", "unknown"),
        "deployment_readiness_state": data.get("deployment_readiness_state", "unknown"),
        "deployment_stale_or_unverified": bool(data.get("deployment_stale_or_unverified", False)),
        "deployment_unavailable": bool(data.get("deployment_unavailable", False)),
        "latency_class": latency_class(latency),
    }


def fetch_web_proxy_version(web_url: str, timeout: float) -> dict[str, Any]:
    proxy_url = f"{web_url.rstrip('/')}/api/v1/version"
    started = time.perf_counter()
    try:
        with urlopen(Request(proxy_url, headers={"accept": "application/json"}), timeout=timeout) as response:
            body = json.loads(response.read(250_000).decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError, AttributeError) as exc:
        return {"status": "failed", "error": type(exc).__name__, "latency_class": "failed"}
    latency = time.perf_counter() - started
    if not isinstance(body, dict):
        return {"status": "failed", "error": "InvalidEnvelope", "latency_class": latency_class(latency)}
    data = body.get("data") if isinstance(body, dict) else {}
    if not isinstance(data, dict):
        data = {}
    return {
        "status": "ok" if body.get("status") == "success" else "failed",
        "git_commit": data.get("git_commit") or data.get("api_commit", "unknown"),
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
    visible = web_commit_visible(html, expected_commit)
    return {
        "status": "verified" if visible else "commit_not_visible",
        "commit_visible": visible,
        "latency_class": latency_class(latency),
    }


def deployment_status(
    *,
    expected_commit: str,
    api_result: dict[str, Any],
    api_commit: str,
    web_html_result: dict[str, Any],
    web_proxy_result: dict[str, Any],
    web_proxy_commit: str,
) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if expected_commit == "unknown":
        return "probe_error", ["expected_commit_unknown"]

    api_failed = api_result.get("status") != "ok"
    web_html_failed = web_html_result.get("status") == "failed"
    web_proxy_failed = web_proxy_result.get("status") != "ok"
    if api_failed and web_html_failed and web_proxy_failed:
        return "deployed_unavailable", ["api_unavailable", "web_unavailable", "web_proxy_unavailable"]

    if api_failed:
        warnings.append("api_unavailable")
    elif api_result.get("deployment_unavailable"):
        warnings.append("api_reported_deployment_unavailable")
    elif api_result.get("deployment_stale_or_unverified"):
        warnings.append("api_reported_deployment_stale_or_unverified")
    elif not commits_match(expected_commit, api_commit):
        warnings.append("api_commit_mismatch")

    if web_proxy_failed:
        warnings.append("web_proxy_unavailable")
    elif not commits_match(expected_commit, web_proxy_commit):
        warnings.append("web_proxy_commit_mismatch")

    if web_html_result.get("status") != "verified":
        warnings.append(f"web_html_{web_html_result.get('status', 'not_verified')}")

    if warnings:
        return "deployed_stale_or_unverified", warnings
    return "deployed_verified", []


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
    cleaned = "".join(character for character in value.strip().lower() if character.isalnum())
    return cleaned if GIT_SHA_RE.fullmatch(cleaned) else "unknown"


def commits_match(expected_commit: str, observed_commit: str) -> bool:
    expected = _clean_commit(expected_commit)
    observed = _clean_commit(observed_commit)
    if expected == "unknown" or observed == "unknown":
        return False
    return expected.startswith(observed) or observed.startswith(expected)


def web_commit_visible(html: str, expected_commit: str) -> bool:
    expected = _clean_commit(expected_commit)
    if expected == "unknown":
        return False
    candidates = [expected]
    if len(expected) == 40:
        candidates.append(expected[:12])
    lower_html = html.lower()
    return any(_contains_commit_token(lower_html, candidate) for candidate in candidates)


def _contains_commit_token(text: str, commit: str) -> bool:
    if len(commit) < 12:
        return False
    pattern = re.compile(rf"(?<![0-9a-f]){re.escape(commit)}(?![0-9a-f])")
    return bool(pattern.search(text))


if __name__ == "__main__":
    sys.exit(main())
