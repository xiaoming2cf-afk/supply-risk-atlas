from __future__ import annotations

import json

from services.api.storage.report_store import ReportStore
from services.api.storage.sqlite_store import SQLiteStore


def test_report_store_persists_sanitized_report(tmp_path) -> None:
    store = ReportStore(SQLiteStore(tmp_path / "reports.db"), max_items=8)
    stored = store.put_report(
        {
            "report_id": "report_test",
            "report_version": "report_v1",
            "generated_at": "2026-05-01T00:00:00Z",
            "format": "json",
            "versions": {
                "graph_version": "graph_test",
                "source_manifest_id": "manifest_test",
            },
            "raw_payload": {"secret": "must-not-store"},
            "warnings": ["fixture_graph:not_production_ready"],
        },
        markdown="# Sanitized report",
    )
    loaded = store.get_report("report_test")
    rendered = json.dumps({"stored": stored, "loaded": loaded}, sort_keys=True).lower()

    assert loaded is not None
    assert loaded["report_id"] == "report_test"
    assert loaded["versions"]["source_manifest_id"] == "manifest_test"
    assert loaded["raw_payload_excluded"] is True
    assert loaded["private_diagnostics_excluded"] is True
    assert loaded["markdown"] == "# Sanitized report"
    assert "must-not-store" not in rendered
    assert '"raw_payload":' not in rendered
    assert "secret" not in rendered
