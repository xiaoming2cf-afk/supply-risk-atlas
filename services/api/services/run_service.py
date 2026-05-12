from __future__ import annotations

import os
from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from sra_core.api.envelope import make_envelope
from services.api.runtime.run_store import RUN_STORE_VERSION, RunStore
from services.api.services.common import semiconductor_metadata


def run_store_size() -> int:
    try:
        configured = int(os.getenv("SUPPLY_RISK_RUN_STORE_SIZE", "32"))
    except ValueError:
        return 32
    return max(1, min(configured, 256))


RUN_STORE = RunStore(max_items=run_store_size())
RUN_CACHE = RUN_STORE


def route_runs(request_id: str | None = None) -> dict[str, Any]:
    snapshot = build_semiconductor_fixture_snapshot()
    runs = RUN_STORE.list_summaries()
    payload = {
        "run_store_version": RUN_STORE_VERSION,
        "graph_version": snapshot.graph_version,
        "source_manifest_id": snapshot.source_manifest_id,
        "as_of_time": snapshot.as_of_time,
        "count": len(runs),
        "max_items": RUN_STORE.max_items,
        "runs": runs,
        "warnings": ["fixture_graph:not_production_ready", "run_history:sanitized_summaries_only"],
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=RUN_STORE_VERSION),
        request_id=request_id,
        warnings=payload["warnings"],
    )


def route_run_detail(run_id: str, request_id: str | None = None) -> dict[str, Any]:
    snapshot = build_semiconductor_fixture_snapshot()
    run = RUN_STORE.get(run_id)
    if run is None:
        raise LookupError(f"Run not found: {run_id}")
    payload = {
        **run,
        "run_store_version": RUN_STORE_VERSION,
        "graph_version": run.get("graph_version") or snapshot.graph_version,
        "source_manifest_id": run.get("source_manifest_id") or snapshot.source_manifest_id,
        "raw_payload_excluded": True,
        "private_diagnostics_excluded": True,
        "warnings": sorted(
            set(
                [
                    *run.get("warnings", []),
                    "fixture_graph:not_production_ready",
                    "run_history:sanitized_summaries_only",
                ]
            )
        ),
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=RUN_STORE_VERSION),
        request_id=request_id,
        warnings=payload["warnings"],
    )

