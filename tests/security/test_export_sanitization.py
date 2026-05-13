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


def test_analytics_exports_do_not_expose_private_or_payload_fields() -> None:
    response = _client().get("/api/v1/analytics/export/source-catalog?format=json&limit=20")
    assert response.status_code == 200
    payload = response.json()
    rendered = json.dumps(payload, sort_keys=True).lower()

    assert payload["status"] == "success"
    assert payload["data"]["table_id"] == "source_catalog"
    assert payload["data"]["graph_version"]
    assert payload["data"]["source_manifest_id"]
    assert "raw_payload" not in rendered
    assert "source_payload" not in rendered
    assert "private_diagnostics" not in rendered
    assert "authorization" not in rendered
    assert "api_key" not in rendered
    assert "cookie" not in rendered
    assert "<script" not in rendered
    assert "onerror" not in rendered


def test_analytics_markdown_export_contains_only_bounded_summary() -> None:
    response = _client().get("/api/v1/analytics/export/graph-quality?format=markdown&limit=3")
    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]

    assert payload["status"] == "success"
    assert data["format"] == "markdown"
    assert data["row_count"] <= 3
    assert data["content"].startswith("# graph_quality_table")
    rendered = json.dumps(payload, sort_keys=True).lower()
    assert "raw_payload" not in rendered
    assert "private_diagnostics" not in rendered
