from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Any
from datetime import datetime, timezone

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from sra_core.api.envelope import make_envelope

from services.api.services.common import semiconductor_metadata
from services.api.storage.sqlite_store import configured_storage_mode


APP_VERSION = "0.1.0"
VERSION_SERVICE_VERSION = "supply_risk_version_v0.1"
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def build_version_payload() -> dict[str, Any]:
    graph_version = "unavailable"
    source_manifest_id = "unavailable"
    graph_mode = _configured_graph_mode()
    data_mode = _configured_data_mode(graph_mode)
    warnings = [
        "not_production_ready",
        "deployment_version_not_a_production_readiness_claim",
    ]

    try:
        snapshot = build_semiconductor_fixture_snapshot()
        graph_version = snapshot.graph_version
        source_manifest_id = snapshot.source_manifest_id
    except Exception as exc:
        warnings.append(f"version_graph_metadata_unavailable:{type(exc).__name__}")

    git_commit = current_git_commit()
    build_time = current_build_time()
    if git_commit == "unknown":
        warnings.append("git_commit_not_verified")
    if build_time == "unknown":
        warnings.append("build_time_not_verified")

    web_commit = current_web_commit()
    deployment_state = deployment_readiness_state(git_commit, web_commit)
    return {
        "api_commit": git_commit,
        "git_commit": git_commit,
        "build_time": build_time,
        "app_version": APP_VERSION,
        "version_service": VERSION_SERVICE_VERSION,
        "data_mode": data_mode,
        "graph_mode": graph_mode,
        "storage_mode": configured_storage_mode(),
        "source_manifest_id": source_manifest_id,
        "graph_version": graph_version,
        "environment": runtime_environment(),
        "runtime_env": runtime_environment(),
        "source_status": "partial",
        "web_commit": web_commit,
        "commit_mismatch": commit_mismatch(git_commit, web_commit),
        "deployment_readiness_state": deployment_state,
        "deployment_stale_or_unverified": deployment_state == "stale_or_unverified",
        "deployment_unavailable": deployment_state == "unavailable",
        "last_checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "production_status": "public_evidence_promoted" if graph_mode == "promoted" else "research_fixture",
        "calibration_status": ["fixture_proxy_not_calibrated", "not_financial_loss"],
        "not_production_ready": True,
        "warnings": sorted(set(warnings)),
    }


def route_version(request_id: str | None = None) -> dict[str, Any]:
    payload = build_version_payload()
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(feature_version=VERSION_SERVICE_VERSION),
        request_id=request_id,
        warnings=payload["warnings"],
    )


def current_git_commit() -> str:
    configured = _first_env(
        "SUPPLY_RISK_GIT_COMMIT",
        "RENDER_GIT_COMMIT",
        "GIT_COMMIT",
        "COMMIT_SHA",
        "VERCEL_GIT_COMMIT_SHA",
    )
    if configured:
        return _short_or_full_commit(configured)
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except Exception:
        return "unknown"
    return _short_or_full_commit(completed.stdout.strip())


def current_build_time() -> str:
    configured = _first_env(
        "SUPPLY_RISK_BUILD_TIME",
        "RENDER_BUILD_TIMESTAMP",
        "BUILD_TIME",
        "NEXT_PUBLIC_SUPPLY_RISK_WEB_BUILD_TIME",
    )
    if configured:
        return _sanitize_build_time(configured)
    return "unknown"


def current_web_commit() -> str:
    configured = _first_env(
        "SUPPLY_RISK_WEB_COMMIT",
        "NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT",
    )
    return _short_or_full_commit(configured) if configured else "not_verified"


def commit_mismatch(api_commit: str, web_commit: str) -> bool:
    if api_commit in {"unknown", "not_verified"} or web_commit in {"unknown", "not_verified"}:
        return False
    return not commits_match(api_commit, web_commit)


def deployment_readiness_state(api_commit: str, web_commit: str) -> str:
    if api_commit in {"unknown", "not_verified"}:
        return "unavailable"
    if web_commit in {"unknown", "not_verified"}:
        return "stale_or_unverified"
    if commit_mismatch(api_commit, web_commit):
        return "stale_or_unverified"
    return "commit_reported"


def runtime_environment() -> str:
    if os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"):
        return "render"
    env = os.getenv("SUPPLY_RISK_ENV", "").strip().lower()
    if env in {"production", "render"}:
        return "render"
    if env in {"local", "development", "dev", "test"}:
        return "local"
    return "local" if (PROJECT_ROOT / ".git").exists() else "unknown"


def _configured_graph_mode() -> str:
    mode = os.getenv("SUPPLY_RISK_GRAPH_MODE", "fixture").strip().lower()
    return mode if mode in {"fixture", "promoted"} else "fixture"


def _configured_data_mode(graph_mode: str) -> str:
    explicit = os.getenv("SUPPLY_RISK_DATA_MODE", "").strip().lower()
    allowed = {"fixture", "promoted", "live_disabled", "live_enabled", "public_evidence_promoted"}
    if explicit in allowed:
        return "promoted" if explicit == "public_evidence_promoted" else explicit
    return "promoted" if graph_mode == "promoted" else "fixture"


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


def _short_or_full_commit(value: str) -> str:
    cleaned = value.strip().lower()
    if 7 <= len(cleaned) <= 40:
        return cleaned if all(character in "0123456789abcdef" for character in cleaned) else "unknown"
    return "unknown"


def commits_match(left_commit: str, right_commit: str) -> bool:
    left = _short_or_full_commit(left_commit)
    right = _short_or_full_commit(right_commit)
    if left == "unknown" or right == "unknown":
        return False
    return left.startswith(right) or right.startswith(left)


def _sanitize_build_time(value: str) -> str:
    cleaned = value.strip()
    if len(cleaned) > 40:
        return "unknown"
    if any(token in cleaned.lower() for token in ("authorization", "cookie", "token", "secret", "\\", "/", ":\\", "://")):
        return "unknown"
    allowed = set("0123456789TtZz:+-._ ")
    return cleaned if cleaned and all(character in allowed for character in cleaned) else "unknown"
