from __future__ import annotations

from services.api.storage import SQLiteStore
from services.api.storage.migrations import initialize_storage


def test_sqlite_store_initializes_required_tables(tmp_path) -> None:
    store = initialize_storage(tmp_path / "sra.db")

    tables = {
        row["name"]
        for row in store.fetch_all(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    }

    assert {
        "source_manifest",
        "raw_record_index",
        "silver_entity",
        "silver_event",
        "graph_snapshot",
        "graph_node",
        "graph_edge",
        "run_record",
        "report_record",
        "audit_event",
    } <= tables


def test_sqlite_store_persists_across_connections(tmp_path) -> None:
    path = tmp_path / "sra.db"
    store = SQLiteStore(path)
    store.initialize()

    store.execute(
        "INSERT INTO audit_event (event_type, entity_id, summary_json) VALUES (?, ?, ?)",
        ("storage_test", "entity:test", '{"ok": true}'),
    )

    reopened = SQLiteStore(path)
    rows = reopened.fetch_all("SELECT event_type, entity_id FROM audit_event")

    assert rows == [{"event_type": "storage_test", "entity_id": "entity:test"}]

