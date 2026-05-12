from __future__ import annotations

from services.api.storage import SQLiteStore
from services.api.storage.migrations import initialize_storage
from services.api.storage.sqlite_store import configured_storage_mode, default_sqlite_path


REQUIRED_TABLES = {
    "source_manifest",
    "source_status",
    "raw_record_index",
    "silver_entity",
    "silver_event",
    "market_indicator",
    "trade_flow",
    "policy_event",
    "logistics_node",
    "hazard_event",
    "graph_snapshot",
    "graph_node",
    "graph_edge",
    "graph_view_cache",
    "run_record",
    "report_record",
    "audit_event",
    "validation_artifact",
}


def test_sqlite_store_initializes_required_tables(tmp_path) -> None:
    store = initialize_storage(tmp_path / "sra.db")
    tables = {
        row["name"]
        for row in store.fetch_all(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    }

    assert REQUIRED_TABLES <= tables


def test_sqlite_store_persists_across_connections(tmp_path) -> None:
    path = tmp_path / "sra.db"
    store = SQLiteStore(path)
    store.initialize()

    store.execute(
        """
        INSERT INTO audit_event
        (created_at, event_type, actor_type, endpoint, request_hash, status, warnings_json, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("2026-05-01T00:00:00Z", "storage_test", "system", "/test", "hash", "success", "[]", "{}"),
    )

    reopened = SQLiteStore(path)
    rows = reopened.fetch_all("SELECT event_type, actor_type, endpoint FROM audit_event")

    assert rows == [{"event_type": "storage_test", "actor_type": "system", "endpoint": "/test"}]


def test_storage_env_defaults_are_bounded(monkeypatch) -> None:
    monkeypatch.delenv("SUPPLY_RISK_STORAGE_MODE", raising=False)
    monkeypatch.delenv("SUPPLY_RISK_SQLITE_PATH", raising=False)

    assert configured_storage_mode() == "sqlite"
    assert default_sqlite_path().as_posix().endswith("data/runtime/supply_risk_atlas.db")

    monkeypatch.setenv("SUPPLY_RISK_STORAGE_MODE", "memory")
    assert configured_storage_mode() == "memory"
