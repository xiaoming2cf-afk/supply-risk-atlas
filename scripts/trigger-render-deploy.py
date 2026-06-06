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
GIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
SERVICE_ID_RE = re.compile(r"^srv-[A-Za-z0-9]+$")
REQUIRED_ENV_VARS = ("RENDER_API_KEY", "RENDER_API_SERVICE_ID", "RENDER_WEB_SERVICE_ID")


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
    missing = [name for name in REQUIRED_ENV_VARS if not str(env.get(name, "")).strip()]
    if commit == "unknown":
        return {
            "status": "render_deploy_blocked_invalid_commit",
            "missing_env": [],
            "services": [],
            "retry_hint": "provide_7_to_40_character_git_sha",
        }
    if missing:
        return {
            "status": "render_deploy_blocked_missing_safe_deploy_path",
            "missing_env": missing,
            "services": [],
            "retry_hint": "set_render_api_key_and_service_ids_outside_chat_then_retry",
        }

    service_plan = [
        ("supply-risk-atlas-api", str(env["RENDER_API_SERVICE_ID"]).strip()),
        ("supply-risk-atlas-web", str(env["RENDER_WEB_SERVICE_ID"]).strip()),
    ]
    invalid_services = [name for name, service_id in service_plan if not SERVICE_ID_RE.fullmatch(service_id)]
    if invalid_services:
        return {
            "status": "render_deploy_blocked_invalid_service_id",
            "missing_env": [],
            "services": [{"service": name, "status": "invalid_service_id"} for name in invalid_services],
            "retry_hint": "verify_render_service_ids_outside_chat_then_retry",
        }

    if dry_run:
        return {
            "status": "render_deploy_dry_run",
            "commit": commit,
            "clear_cache": clear_cache,
            "services": [{"service": name, "status": "would_trigger"} for name, _service_id in service_plan],
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
        "services": service_reports,
        "retry_hint": "run_check_deployed_version_after_render_builds_finish",
    }


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
    cleaned = "".join(character for character in value.strip().lower() if character.isalnum())
    return cleaned if GIT_SHA_RE.fullmatch(cleaned) else "unknown"


if __name__ == "__main__":
    sys.exit(main())
