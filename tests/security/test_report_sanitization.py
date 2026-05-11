from __future__ import annotations

import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api import main


def _client() -> TestClient:
    app = main.create_app()
    assert app is not None
    return TestClient(app)


def test_markdown_report_export_is_sanitized_and_metadata_bound() -> None:
    marker = "RAW-MARKDOWN-PAYLOAD-SHOULD-NOT-ECHO"
    response = _client().post(
        "/api/v1/reports/investigation",
        json={
            "entity_id": "company:tsmc",
            "format": "markdown",
            "raw_payload": {"record": marker},
            "private_diagnostics": {"internal_path": "D:/private/report.py"},
            "notes": "<script>alert(1)</script><img src=x onerror=alert(2)>",
        },
    )
    payload = response.json()
    rendered = json.dumps(payload, sort_keys=True).lower()
    report = payload["data"]

    assert payload["status"] == "success"
    assert report["format"] == "markdown"
    assert report["graph_context"]["node_count"] > 0
    assert report["versions"]["graph_version"]
    assert report["versions"]["source_manifest_id"]
    assert report["raw_payload_excluded"] is True
    assert report["private_diagnostics_excluded"] is True
    assert marker.lower() not in rendered
    assert "<script" not in rendered
    assert "onerror" not in rendered
    assert "d:/private" not in rendered
