from __future__ import annotations

import json

from services.api.runtime.run_store import RunStore
from services.api.storage.run_store_sqlite import SQLiteRunStore
from services.api.storage.sqlite_store import SQLiteStore


def _run_payload(run_id: str) -> dict[str, object]:
    return {
        "status": "success",
        "warnings": ["fixture_graph:not_production_ready"],
        "data": {
            "run_id": run_id,
            "timestamp": "2026-05-01T00:00:00Z",
            "graph_version": "graph_test",
            "source_manifest_id": "manifest_test",
            "expected_loss": 12.5,
            "request_hash": "request_hash_test",
            "evidence_refs": ["sec_edgar_lite"],
            "raw_payload": {"secret": "must-not-store"},
            "simulation_version": "sim_test",
            "data_mode": "fixture",
            "graph_mode": "fixture",
        },
    }


def test_sqlite_run_store_persists_sanitized_summaries(tmp_path) -> None:
    path = tmp_path / "runs.db"
    first = SQLiteRunStore(SQLiteStore(path), max_items=8)
    first.put_summary("forward_scenario", _run_payload("run_1"))

    second = SQLiteRunStore(SQLiteStore(path), max_items=8)
    listed = second.list_summaries()
    detail = second.get("run_1")
    rendered = json.dumps({"listed": listed, "detail": detail}, sort_keys=True).lower()

    assert listed[0]["run_id"] == "run_1"
    assert listed[0]["graph_version"] == "graph_test"
    assert listed[0]["request_hash"] == "request_hash_test"
    assert detail is not None
    assert detail["summary"]["expected_loss"] == 12.5
    assert detail["evidence_refs"] == ["sec_edgar_lite"]
    assert detail["versions"]["simulation_version"] == "sim_test"
    assert "must-not-store" not in rendered
    assert '"raw_payload":' not in rendered
    assert "secret" not in rendered


def test_sqlite_run_store_retention_limit(tmp_path) -> None:
    run_store = SQLiteRunStore(SQLiteStore(tmp_path / "runs.db"), max_items=2)

    for index in range(3):
        run_store.put_summary("forward_scenario", _run_payload(f"run_{index}"))

    assert [run["run_id"] for run in run_store.list_summaries()] == ["run_2", "run_1"]
    assert run_store.get("run_0") is None


def test_existing_in_memory_run_store_remains_available() -> None:
    run_store = RunStore(max_items=2)
    stored = run_store.put_summary("forward_scenario", _run_payload("memory_run"))

    assert stored is not None
    assert run_store.get("memory_run") is not None
    assert run_store.list_summaries()[0]["run_id"] == "memory_run"
