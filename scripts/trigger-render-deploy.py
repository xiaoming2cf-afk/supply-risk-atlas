from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


RENDER_DEPLOY_URL_TEMPLATE = "https://api.render.com/v1/services/{service_id}/deploys"
GIT_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
SERVICE_ID_RE = re.compile(r"^srv-[A-Za-z0-9]+$")
REQUIRED_ENV_VARS = ("RENDER_API_KEY", "RENDER_API_SERVICE_ID", "RENDER_WEB_SERVICE_ID")
SERVICE_ENV_PLAN = (
    ("supply-risk-atlas-api", "RENDER_API_SERVICE_ID"),
    ("supply-risk-atlas-web", "RENDER_WEB_SERVICE_ID"),
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trigger Render API/Web deploys using environment variables without printing secrets.",
    )
    parser.add_argument("--commit", default=None, help="Git commit SHA to deploy. Defaults to local HEAD.")
    parser.add_argument(
        "--clear-cache",
        choices=("clear", "do_not_clear"),
        default="clear",
        help="Whether Render should clear the build cache.",
    )
    parser.add_argument("--timeout", type=float, default=20.0, help="Bounded request timeout per Render service.")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and print sanitized plan only.")
    args = parser.parse_args()

    commit = clean_commit(args.commit or local_git_commit())
    report = trigger_render_deploys(
        commit=commit,
        clear_cache=args.clear_cache,
        timeout=args.timeout,
        dry_run=args.dry_run,
        env=os.environ,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] in {"render_deploy_triggered", "render_deploy_dry_run"} else 1


def trigger_render_deploys(
    *,
    commit: str,
    clear_cache: str,
    timeout: float,
    dry_run: bool,
    env: Any,
) -> dict[str, Any]:
    preflight = render_deploy_preflight_report(commit=commit, clear_cache=clear_cache, env=env)
    if not preflight["safe_deploy_path"]:
        return preflight

    service_plan = service_plan_from_env(env)

    if dry_run:
        return {
            "status": "render_deploy_dry_run",
            "commit": commit,
            "clear_cache": clear_cache,
            "missing_env": [],
            "render_api_call_attempted": False,
            "safe_deploy_path": True,
            "services": [{"service": name, "status": "would_trigger"} for name, _service_id in service_plan],
            "next_action": "rerun_without_dry_run_when_ready",
            "retry_hint": "rerun_without_dry_run_when_ready",
        }

    api_key = str(env["RENDER_API_KEY"]).strip()
    service_reports = [
        trigger_service_deploy(
            service_name=service_name,
            service_id=service_id,
            api_key=api_key,
            commit=commit,
            clear_cache=clear_cache,
            timeout=timeout,
        )
        for service_name, service_id in service_plan
    ]
    status = (
        "render_deploy_triggered"
        if all(row["status"] == "triggered" for row in service_reports)
        else "render_deploy_trigger_failed"
    )
    return {
        "status": status,
        "commit": commit,
        "clear_cache": clear_cache,
        "missing_env": [],
        "render_api_call_attempted": True,
        "safe_deploy_path": True,
        "services": service_reports,
        "next_action": "run_check_deployed_version_after_render_builds_finish",
        "retry_hint": "run_check_deployed_version_after_render_builds_finish",
    }


def render_deploy_preflight_report(*, commit: str, clear_cache: str, env: Any) -> dict[str, Any]:
    if commit == "unknown":
        return blocked_report(
            status="render_deploy_blocked_invalid_commit",
            commit=commit,
            clear_cache=clear_cache,
            missing_env=[],
            services=[],
            next_action="provide_7_to_40_character_git_sha",
        )

    missing = [name for name in REQUIRED_ENV_VARS if not str(env.get(name, "")).strip()]
    if missing:
        return blocked_report(
            status="render_deploy_blocked_missing_safe_deploy_path",
            commit=commit,
            clear_cache=clear_cache,
            missing_env=missing,
            services=[],
            next_action="set_render_api_key_and_service_ids_outside_chat_then_retry",
        )

    service_plan = service_plan_from_env(env)
    invalid_services = [
        service_name for service_name, service_id in service_plan if not SERVICE_ID_RE.fullmatch(service_id)
    ]
    if invalid_services:
        return blocked_report(
            status="render_deploy_blocked_invalid_service_id",
            commit=commit,
            clear_cache=clear_cache,
            missing_env=[],
            services=[{"service": service_name, "status": "invalid_service_id"} for service_name in invalid_services],
            next_action="set_valid_render_service_ids_outside_chat_then_retry",
        )

    return {
        "status": "render_deploy_preflight_passed",
        "commit": commit,
        "clear_cache": clear_cache,
        "missing_env": [],
        "render_api_call_attempted": False,
        "safe_deploy_path": True,
        "services": [{"service": service_name, "status": "validated"} for service_name, _service_id in service_plan],
        "next_action": "rerun_without_dry_run_when_ready_or_trigger_deploy",
        "retry_hint": "rerun_without_dry_run_when_ready_or_trigger_deploy",
    }


def blocked_report(
    *,
    status: str,
    commit: str,
    clear_cache: str,
    missing_env: list[str],
    services: list[dict[str, Any]],
    next_action: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "commit": commit,
        "clear_cache": clear_cache,
        "missing_env": missing_env,
        "render_api_call_attempted": False,
        "safe_deploy_path": False,
        "services": services,
        "next_action": next_action,
        "retry_hint": next_action,
    }


def service_plan_from_env(env: Any) -> list[tuple[str, str]]:
    return [(service_name, str(env[env_name]).strip()) for service_name, env_name in SERVICE_ENV_PLAN]


def trigger_service_deploy(
    *,
    service_name: str,
    service_id: str,
    api_key: str,
    commit: str,
    clear_cache: str,
    timeout: float,
) -> dict[str, Any]:
    payload = json.dumps({"clearCache": clear_cache, "commitId": commit}).encode("utf-8")
    request = Request(
        RENDER_DEPLOY_URL_TEMPLATE.format(service_id=service_id),
        data=payload,
        method="POST",
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            http_status = int(getattr(response, "status", 0) or response.getcode())
    except HTTPError as exc:
        return {
            "service": service_name,
            "status": "failed",
            "http_status": int(exc.code),
            "error": "HTTPError",
        }
    except (TimeoutError, OSError, URLError) as exc:
        return {
            "service": service_name,
            "status": "failed",
            "http_status": "unavailable",
            "error": type(exc).__name__,
        }
    if http_status not in {201, 202}:
        return {
            "service": service_name,
            "status": "failed",
            "http_status": http_status,
            "error": "UnexpectedStatus",
        }
    return {"service": service_name, "status": "triggered", "http_status": http_status}


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


def clean_commit(value: str) -> str:
    cleaned = value.strip().lower()
    return cleaned if GIT_SHA_RE.fullmatch(cleaned) else "unknown"


if __name__ == "__main__":
    sys.exit(main())
