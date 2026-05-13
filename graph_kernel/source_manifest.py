from __future__ import annotations

from collections import Counter
from typing import Any

from graph_kernel.graph_versioning import source_manifest_id, stable_hash
from sra_core.sources import source_registry_readiness


def build_source_manifest(source_ids: list[str]) -> dict[str, Any]:
    readiness = source_registry_readiness()
    selected = [row for row in readiness["sources"] if row["source_id"] in set(source_ids)]
    basis = {
        "registry_version": readiness["registry_version"],
        "source_ids": sorted(source_ids),
        "statuses": {row["source_id"]: row["status"] for row in selected},
    }
    return {
        "source_manifest_id": source_manifest_id(basis),
        "registry_version": readiness["registry_version"],
        "generated_at": readiness["generated_at"],
        "source_count": len(selected),
        "source_ids": sorted(source_ids),
        "checksum": stable_hash(basis),
        "status_counts": dict(Counter(row["status"] for row in selected)),
        "connector_status_counts": dict(Counter(row["connector_status"] for row in selected)),
        "warnings": readiness["warnings"],
    }

