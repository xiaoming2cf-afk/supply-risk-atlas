from __future__ import annotations

from pathlib import Path
from typing import Any

from sra_core.sources.registry import load_semiconductor_source_registry, source_registry_readiness


def promoted_source_status(registry_path: str | Path | None = None) -> dict[str, Any]:
    readiness = source_registry_readiness(registry_path)
    return {
        "registry_version": readiness["registry_version"],
        "generated_at": readiness["generated_at"],
        "status": readiness["status"],
        "source_count": readiness["source_count"],
        "enabled_count": readiness["enabled_count"],
        "disabled_count": readiness["disabled_count"],
        "unavailable_count": readiness["unavailable_count"],
        "connector_status_counts": readiness["connector_status_counts"],
        "license_status_counts": readiness["license_status_counts"],
        "sources": readiness["sources"],
        "warnings": [
            *readiness["warnings"],
            "promoted_graph:no_live_fetch_during_build",
            "raw_payloads_excluded",
        ],
    }


def license_terms_for_sources(
    source_ids: set[str],
    registry_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    registry = load_semiconductor_source_registry(registry_path)
    rows: list[dict[str, Any]] = []
    for source in registry["sources"]:
        if source["source_id"] not in source_ids:
            continue
        rows.append(
            {
                "source_id": source["source_id"],
                "publisher": source["publisher"],
                "terms_url": source["terms_url"],
                "allowed_use": list(source["allowed_use"]),
                "redistribution_limits": source["redistribution_limits"],
                "license_or_terms_summary": source["license_or_terms_summary"],
            }
        )
    return sorted(rows, key=lambda row: row["source_id"])
