from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from sra_core.sources.license_policy import license_policy_for_source
from sra_core.sources.models import (
    DATA_CATEGORIES,
    REQUIRED_SOURCE_FIELDS,
    SOURCE_TIERS,
    SourceEntry,
    SourceRegistry,
)
from sra_core.sources.source_status import connector_status_for_source, source_status_for_source


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_semiconductor_registry_path() -> Path:
    return repository_root() / "configs" / "sources" / "semiconductor.yaml"


def load_semiconductor_source_registry(path: str | Path | None = None) -> SourceRegistry:
    registry_path = Path(path) if path is not None else default_semiconductor_registry_path()
    raw_registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    validate_semiconductor_source_registry(raw_registry)
    return SourceRegistry(
        registry_version=str(raw_registry["registry_version"]),
        generated_at=str(raw_registry["generated_at"]),
        sources=tuple(SourceEntry.from_dict(item) for item in raw_registry["sources"]),
    )


def validate_semiconductor_source_registry(raw_registry: dict[str, Any]) -> None:
    if not isinstance(raw_registry, dict):
        raise ValueError("source registry must be a mapping")
    if not raw_registry.get("registry_version"):
        raise ValueError("source registry missing registry_version")
    if not raw_registry.get("generated_at"):
        raise ValueError("source registry missing generated_at")
    sources = raw_registry.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source registry must contain at least one source")

    seen: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("source registry entries must be mappings")
        missing = sorted(REQUIRED_SOURCE_FIELDS - set(source))
        if missing:
            source_id = source.get("source_id", "<missing-source-id>")
            raise ValueError(f"{source_id} missing required fields: {missing}")

        source_id = str(source["source_id"])
        if source_id in seen:
            raise ValueError(f"duplicate source_id: {source_id}")
        seen.add(source_id)

        if not str(source["source_url"]).startswith("https://"):
            raise ValueError(f"{source_id} source_url must use https")
        if not str(source["terms_url"]).startswith("https://"):
            raise ValueError(f"{source_id} terms_url must use https")
        if source["source_tier"] not in SOURCE_TIERS:
            raise ValueError(f"{source_id} has invalid source_tier {source['source_tier']!r}")
        if source["data_category"] not in DATA_CATEGORIES:
            raise ValueError(f"{source_id} has invalid data_category {source['data_category']!r}")
        if not isinstance(source["allowed_use"], list) or not source["allowed_use"]:
            raise ValueError(f"{source_id} must define allowed_use")
        if not isinstance(source["enabled_by_default"], bool):
            raise ValueError(f"{source_id} enabled_by_default must be boolean")
        if not isinstance(source["live_fetch_default"], bool):
            raise ValueError(f"{source_id} live_fetch_default must be boolean")
        if int(source["freshness_sla_hours"]) < 1:
            raise ValueError(f"{source_id} freshness_sla_hours must be positive")
        if source["source_tier"] == "tier_3":
            if source["enabled_by_default"] or source["live_fetch_default"]:
                raise ValueError(f"{source_id} tier_3 sources must be disabled")


def source_readiness_rows(registry: SourceRegistry | None = None) -> list[dict[str, Any]]:
    registry = registry or load_semiconductor_source_registry()
    rows: list[dict[str, Any]] = []
    for source in registry.sources:
        license_policy = license_policy_for_source(source)
        public_license_policy = {
            "api_visible_summary_allowed": license_policy["api_visible_summary_allowed"],
            "payload_storage_allowed": license_policy["raw_payload_storage_allowed"],
            "redistribution_allowed": license_policy["redistribution_allowed"],
            "attribution_required": license_policy["attribution_required"],
            "terms_review_required": license_policy["terms_review_required"],
            "manual_review_note": license_policy["manual_review_note"],
        }
        rows.append(
            {
                **source.to_public_dict(),
                "status": source_status_for_source(source),
                "connector_status": connector_status_for_source(source),
                "license_policy": public_license_policy,
            }
        )
    return rows


def source_registry_readiness(path: str | Path | None = None) -> dict[str, Any]:
    registry = load_semiconductor_source_registry(path)
    rows = source_readiness_rows(registry)

    status_counts = Counter(row["status"] for row in rows)
    connector_counts = Counter(row["connector_status"] for row in rows)
    tier_counts = Counter(row["source_tier"] for row in rows)
    enabled_count = sum(1 for row in rows if row["enabled_by_default"])
    live_default_count = sum(1 for row in rows if row["live_fetch_default"])
    terms_review_count = sum(
        1 for row in rows if row["license_policy"]["terms_review_required"]
    )
    deferred_count = status_counts.get("deferred_paid_or_proprietary", 0)

    warnings = [
        "live_fetch_disabled_by_default",
        "payload_storage_disabled_by_default",
    ]
    if terms_review_count:
        warnings.append("some_sources_require_terms_review")
    if deferred_count:
        warnings.append("paid_or_proprietary_sources_are_registry_only")

    overall_status = "ready"
    if terms_review_count or deferred_count:
        overall_status = "degraded"

    return {
        "registry_version": registry.registry_version,
        "generated_at": registry.generated_at,
        "status": overall_status,
        "source_count": len(rows),
        "enabled_count": enabled_count,
        "disabled_count": len(rows) - enabled_count,
        "live_default_count": live_default_count,
        "terms_review_count": terms_review_count,
        "deferred_count": deferred_count,
        "source_status_counts": dict(status_counts),
        "connector_status_counts": dict(connector_counts),
        "source_tier_counts": dict(tier_counts),
        "sources": rows,
        "warnings": warnings,
    }
