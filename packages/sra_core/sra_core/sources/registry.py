from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from sra_core.sources.license_policy import license_policy_summary, license_terms_status
from sra_core.sources.source_status import connector_status, source_runtime_status


REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "publisher",
    "source_url",
    "terms_url",
    "license_or_terms_summary",
    "allowed_use",
    "redistribution_limits",
    "attribution",
    "requires_api_key",
    "enabled_by_default",
    "update_frequency",
    "freshness_sla_hours",
    "connector",
    "raw_contract",
    "silver_contract",
    "graph_contract",
    "owner",
    "review_status",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_semiconductor_registry_path() -> Path:
    return project_root() / "configs" / "sources" / "semiconductor.yaml"


def load_semiconductor_source_registry(path: str | Path | None = None) -> dict[str, Any]:
    registry_path = Path(path) if path else default_semiconductor_registry_path()
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    validate_semiconductor_source_registry(registry)
    return registry


def validate_semiconductor_source_registry(registry: dict[str, Any]) -> None:
    if not isinstance(registry.get("sources"), list) or not registry["sources"]:
        raise ValueError("semiconductor source registry must contain sources")
    seen: set[str] = set()
    for source in registry["sources"]:
        missing = sorted(REQUIRED_SOURCE_FIELDS - set(source))
        if missing:
            raise ValueError(f"{source.get('source_id', '<missing>')} missing {missing}")
        source_id = str(source["source_id"])
        if source_id in seen:
            raise ValueError(f"duplicate source_id: {source_id}")
        seen.add(source_id)
        if not str(source["source_url"]).startswith("https://"):
            raise ValueError(f"{source_id} source_url must be https")
        if not str(source["terms_url"]).startswith("https://"):
            raise ValueError(f"{source_id} terms_url must be https")
        if int(source["freshness_sla_hours"]) <= 0:
            raise ValueError(f"{source_id} freshness_sla_hours must be positive")


def source_registry_readiness(path: str | Path | None = None) -> dict[str, Any]:
    registry = load_semiconductor_source_registry(path)
    source_rows = [_source_readiness(source) for source in registry["sources"]]
    connector_counts = Counter(row["connector_status"] for row in source_rows)
    license_counts = Counter(row["license_terms_status"] for row in source_rows)
    unavailable_count = connector_counts.get("live_connector_unavailable", 0)
    disabled_count = connector_counts.get("disabled_review_required", 0)
    status = "ready" if unavailable_count == 0 else "degraded"
    return {
        "registry_version": registry.get("registry_version"),
        "generated_at": registry.get("generated_at"),
        "status": status,
        "source_count": len(source_rows),
        "enabled_count": sum(1 for row in source_rows if row["runtime_status"] == "enabled"),
        "disabled_count": disabled_count,
        "unavailable_count": unavailable_count,
        "connector_status_counts": dict(sorted(connector_counts.items())),
        "license_status_counts": dict(sorted(license_counts.items())),
        "sources": source_rows,
        "warnings": _readiness_warnings(source_rows),
    }


def _source_readiness(source: dict[str, Any]) -> dict[str, Any]:
    status = connector_status(source)
    return {
        "source_id": source["source_id"],
        "publisher": source["publisher"],
        "enabled_by_default": bool(source["enabled_by_default"]),
        "runtime_status": source_runtime_status(source),
        "connector": source["connector"],
        "connector_status": status,
        "live_connector_available": status == "live_connector_available",
        "fixture_connector": status == "fixture_connector",
        "license_terms_status": license_terms_status(source),
        "license_policy": license_policy_summary(source),
        "terms_url": source["terms_url"],
        "source_url": source["source_url"],
        "freshness_sla_hours": int(source["freshness_sla_hours"]),
        "review_status": source["review_status"],
        "owner": source["owner"],
    }


def _readiness_warnings(source_rows: list[dict[str, Any]]) -> list[str]:
    warnings = ["source_registry:no_live_fetch_in_runtime"]
    unavailable = [row["source_id"] for row in source_rows if row["connector_status"] == "live_connector_unavailable"]
    disabled = [row["source_id"] for row in source_rows if row["connector_status"] == "disabled_review_required"]
    if unavailable:
        warnings.append(f"live_connectors_unavailable:{','.join(unavailable)}")
    if disabled:
        warnings.append(f"disabled_sources_require_review:{','.join(disabled)}")
    return warnings

