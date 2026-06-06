from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
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
    parser.add_argument("--attempts", type=int, default=2, help="Bounded attempts per public deployed probe.")
    args = parser.parse_args()

    expected_commit = _clean_commit(args.expected_commit or local_git_commit())
    attempts = max(1, min(args.attempts, 5))
    api_result = retry_probe(lambda: fetch_api_version(args.api_url, args.timeout), attempts=attempts)
    web_html_result = retry_probe(
        lambda: fetch_web_commit_presence(args.web_url, expected_commit, args.timeout),
        attempts=attempts,
    )
    web_build_result = retry_probe(lambda: fetch_web_build_info(args.web_url, args.timeout), attempts=attempts)
    web_proxy_result = retry_probe(lambda: fetch_web_proxy_version(args.web_url, args.timeout), attempts=attempts)
    api_commit = _clean_commit(str(api_result.get("git_commit") or "unknown"))
    web_build_commit = _clean_commit(str(web_build_result.get("web_commit") or "unknown"))
    web_proxy_commit = _clean_commit(str(web_proxy_result.get("git_commit") or "unknown"))

    status, warnings = deployment_status(
        expected_commit=expected_commit,
        api_result=api_result,
        api_commit=api_commit,
        web_html_result=web_html_result,
        web_build_result=web_build_result,
        web_build_commit=web_build_commit,
        web_proxy_result=web_proxy_result,
        web_proxy_commit=web_proxy_commit,
    )
    failure_class = deployment_failure_class(
        status=status,
        warnings=warnings,
        probe_results=[api_result, web_html_result, web_build_result, web_proxy_result],
    )

    report = {
        "status": status,
        "deployment_status": status,
        "failure_class": failure_class,
        "retry_hint": retry_hint(failure_class),
        "expected_commit": expected_commit,
        "api": {
            "status": api_result.get("status", "failed"),
            "git_commit": api_commit,
            "app_version": api_result.get("app_version", "unknown"),
            "environment": api_result.get("environment", "unknown"),
            "latency_class": api_result.get("latency_class", "failed"),
            "failure_class": api_result.get("failure_class", "none"),
            "attempts": api_result.get("attempts", 1),
        },
        "web": {
            "html": web_html_result,
            "build_info": {
                "status": web_build_result.get("status", "failed"),
                "web_commit": web_build_commit,
                "deployment_readiness_state": web_build_result.get("deployment_readiness_state", "unknown"),
                "latency_class": web_build_result.get("latency_class", "failed"),
                "failure_class": web_build_result.get("failure_class", "none"),
                "attempts": web_build_result.get("attempts", 1),
            },
            "proxy": {
                "status": web_proxy_result.get("status", "failed"),
                "git_commit": web_proxy_commit,
                "app_version": web_proxy_result.get("app_version", "unknown"),
                "environment": web_proxy_result.get("environment", "unknown"),
                "latency_class": web_proxy_result.get("latency_class", "failed"),
                "failure_class": web_proxy_result.get("failure_class", "none"),
                "attempts": web_proxy_result.get("attempts", 1),
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
    except HTTPError as exc:
        return sanitized_fetch_failure(exc)
    except (TimeoutError, OSError, URLError) as exc:
        return sanitized_fetch_failure(exc)
    except (json.JSONDecodeError, AttributeError) as exc:
        return sanitized_fetch_failure(exc, failure_class="schema_mismatch")
    latency = time.perf_counter() - started
    if not isinstance(body, dict):
        return {
            "status": "failed",
            "error": "InvalidEnvelope",
            "latency_class": latency_class(latency),
            "failure_class": "schema_mismatch",
        }
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


def retry_probe(factory, *, attempts: int) -> dict[str, Any]:
    result: dict[str, Any] = {"status": "failed", "latency_class": "failed"}
    for attempt in range(1, attempts + 1):
        try:
            result = factory()
        except Exception as exc:
            result = {
                "status": "failed",
                "error": type(exc).__name__,
                "latency_class": "failed",
                "failure_class": "probe_exception",
            }
        result["attempts"] = attempt
        if result.get("status") in {"ok", "verified"}:
            result["failure_class"] = result.get("failure_class", "none")
            return result
        if attempt < attempts:
            time.sleep(min(3.0, 0.75 * attempt))
    return result


def fetch_web_proxy_version(web_url: str, timeout: float) -> dict[str, Any]:
    proxy_url = f"{web_url.rstrip('/')}/api/v1/version"
    started = time.perf_counter()
    try:
        with urlopen(Request(proxy_url, headers={"accept": "application/json"}), timeout=timeout) as response:
            body = json.loads(response.read(250_000).decode("utf-8"))
    except HTTPError as exc:
        return sanitized_fetch_failure(exc)
    except (TimeoutError, OSError, URLError) as exc:
        return sanitized_fetch_failure(exc)
    except (json.JSONDecodeError, AttributeError) as exc:
        return sanitized_fetch_failure(exc, failure_class="schema_mismatch")
    latency = time.perf_counter() - started
    if not isinstance(body, dict):
        return {
            "status": "failed",
            "error": "InvalidEnvelope",
            "latency_class": latency_class(latency),
            "failure_class": "schema_mismatch",
        }
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


def fetch_web_build_info(web_url: str, timeout: float) -> dict[str, Any]:
    build_info_url = f"{web_url.rstrip('/')}/api/build-info"
    started = time.perf_counter()
    try:
        with urlopen(Request(build_info_url, headers={"accept": "application/json"}), timeout=timeout) as response:
            body = json.loads(response.read(250_000).decode("utf-8"))
            cache_control = response.headers.get("Cache-Control", "")
    except HTTPError as exc:
        return sanitized_fetch_failure(exc)
    except (TimeoutError, OSError, URLError) as exc:
        return sanitized_fetch_failure(exc)
    except (json.JSONDecodeError, AttributeError) as exc:
        return sanitized_fetch_failure(exc, failure_class="schema_mismatch")
    latency = time.perf_counter() - started
    if not isinstance(body, dict):
        return {
            "status": "failed",
            "error": "InvalidEnvelope",
            "latency_class": latency_class(latency),
            "failure_class": "schema_mismatch",
        }
    data = body.get("data") if isinstance(body, dict) else {}
    if not isinstance(data, dict):
        data = {}
    return {
        "status": "ok" if body.get("status") == "success" else "failed",
        "web_commit": data.get("web_commit", "unknown"),
        "deployment_readiness_state": data.get("deployment_readiness_state", "unknown"),
        "cache_control": cache_control,
        "latency_class": latency_class(latency),
    }


def fetch_web_commit_presence(web_url: str, expected_commit: str, timeout: float) -> dict[str, Any]:
    if expected_commit == "unknown":
        return {
            "status": "not_verified",
            "commit_visible": False,
            "latency_class": "not_checked",
            "failure_class": "expected_commit_unknown",
        }
    started = time.perf_counter()
    try:
        with urlopen(Request(web_url, headers={"accept": "text/html"}), timeout=timeout) as response:
            html = response.read(500_000).decode("utf-8", errors="replace")
    except HTTPError as exc:
        failure = sanitized_fetch_failure(exc)
        failure["commit_visible"] = False
        return failure
    except (TimeoutError, OSError, URLError) as exc:
        failure = sanitized_fetch_failure(exc)
        failure["commit_visible"] = False
        return failure
    latency = time.perf_counter() - started
    visible = web_commit_visible(html, expected_commit)
    return {
        "status": "verified" if visible else "commit_not_visible",
        "commit_visible": visible,
        "latency_class": latency_class(latency),
        "failure_class": "none" if visible else "web_commit_marker_missing",
    }


def deployment_status(
    *,
    expected_commit: str,
    api_result: dict[str, Any],
    api_commit: str,
    web_html_result: dict[str, Any],
    web_build_result: dict[str, Any],
    web_build_commit: str,
    web_proxy_result: dict[str, Any],
    web_proxy_commit: str,
) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if expected_commit == "unknown":
        return "probe_error", ["expected_commit_unknown"]

    api_failed = api_result.get("status") != "ok"
    web_html_failed = web_html_result.get("status") == "failed"
    web_build_failed = web_build_result.get("status") != "ok"
    web_proxy_failed = web_proxy_result.get("status") != "ok"
    if api_failed and web_html_failed and web_build_failed and web_proxy_failed:
        return "deployed_unavailable", [
            "api_unavailable",
            "web_unavailable",
            "web_build_info_unavailable",
            "web_proxy_unavailable",
        ]

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

    if web_build_failed:
        warnings.append("web_build_info_unavailable")
    elif not commits_match(expected_commit, web_build_commit):
        warnings.append("web_build_info_commit_mismatch")
    elif "no-store" not in str(web_build_result.get("cache_control", "")).lower():
        warnings.append("web_build_info_cache_control_missing")

    if web_html_result.get("status") != "verified":
        warnings.append(f"web_html_{web_html_result.get('status', 'not_verified')}")

    if warnings:
        return "deployed_stale_or_unverified", warnings
    return "deployed_verified", []


def sanitized_fetch_failure(exc: BaseException, *, failure_class: str | None = None) -> dict[str, Any]:
    status_code = getattr(exc, "code", None)
    result: dict[str, Any] = {
        "status": "failed",
        "error": type(exc).__name__,
        "latency_class": "failed",
        "failure_class": failure_class or classify_fetch_failure(exc),
    }
    if isinstance(status_code, int):
        result["http_status"] = status_code
    return result


def classify_fetch_failure(exc: BaseException) -> str:
    status_code = getattr(exc, "code", None)
    if isinstance(status_code, int):
        if status_code in {502, 503, 504}:
            return "cold_start_or_deploy_transition"
        if 500 <= status_code <= 599:
            return "server_error"
        if 400 <= status_code <= 499:
            return "unavailable"
    if isinstance(exc, TimeoutError) or "timeout" in type(exc).__name__.lower():
        return "transport_timeout"
    if isinstance(exc, (URLError, OSError)):
        return "transport_error"
    if isinstance(exc, (json.JSONDecodeError, AttributeError)):
        return "schema_mismatch"
    return "unavailable"


def deployment_failure_class(
    *,
    status: str,
    warnings: list[str],
    probe_results: list[dict[str, Any]],
) -> str:
    if status == "deployed_verified":
        return "none"
    classes = {str(result.get("failure_class", "")) for result in probe_results}
    classes.discard("")
    classes.discard("none")
    if "cold_start_or_deploy_transition" in classes:
        return "cold_start_or_deploy_transition"
    if "transport_timeout" in classes:
        return "transport_timeout"
    if "schema_mismatch" in classes or any("schema" in warning for warning in warnings):
        return "schema_mismatch"
    if any("mismatch" in warning for warning in warnings):
        return "commit_mismatch"
    if any("unavailable" in warning for warning in warnings):
        return "unavailable"
    if status == "probe_error":
        return "probe_error"
    return "deployed_stale_or_unverified"


def retry_hint(failure_class: str) -> str:
    hints = {
        "none": "none",
        "cold_start_or_deploy_transition": "wait_for_render_warmup_then_retry_bounded_probe",
        "transport_timeout": "retry_bounded_probe_with_existing_timeout_limits",
        "commit_mismatch": "redeploy_api_and_web_from_expected_commit_or_verify_render_service_commit",
        "schema_mismatch": "verify_public_version_envelope_and_web_build_info_contract",
        "unavailable": "check_api_web_service_readiness_before_redeploy",
        "probe_error": "provide_expected_git_commit_and_retry_probe",
    }
    return hints.get(failure_class, "inspect_sanitized_probe_warnings")


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
