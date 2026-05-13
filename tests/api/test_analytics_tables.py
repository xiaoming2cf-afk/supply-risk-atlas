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


def test_named_analytics_tables_are_bounded_and_metadata_bound() -> None:
    client = _client()
    for table_id, expected_key in [
        ("source-catalog", "source_id"),
        ("evidence-refs", "edge_id"),
        ("graph-quality", "metric"),
        ("risk-ranking", "id"),
        ("trade-flows", "edge_type"),
        ("policy-events", "id"),
        ("hazard-events", "id"),
        ("logistics-facilities", "id"),
    ]:
        response = client.get(f"/api/v1/analytics/tables/{table_id}?limit=5&offset=0")
        assert response.status_code == 200
        payload = response.json()
        data = payload["data"]
        assert payload["status"] == "success"
        assert data["table_id"]
        assert data["graph_version"]
        assert data["source_manifest_id"]
        assert data["data_mode"]
        assert data["graph_mode"]
        assert data["limit"] == 5
        assert len(data["rows"]) <= 5
        if data["rows"]:
            assert expected_key in data["rows"][0]
        rendered = json.dumps(payload, sort_keys=True).lower()
        assert "raw_payload" not in rendered
        assert "authorization" not in rendered
        assert "api_key" not in rendered


def test_analytics_export_formats_are_sanitized_and_bounded() -> None:
    client = _client()
    for export_format in ["json", "csv", "markdown"]:
        response = client.get(f"/api/v1/analytics/export/evidence-refs?format={export_format}&limit=7")
        assert response.status_code == 200
        payload = response.json()
        data = payload["data"]
        assert payload["status"] == "success"
        assert data["format"] == export_format
        assert data["graph_version"]
        assert data["source_manifest_id"]
        assert data["export_time"]
        assert data["row_count"] <= 7
        assert data["content_hash"]
        rendered = json.dumps(payload, sort_keys=True).lower()
        assert "raw_payload" not in rendered
        assert "private_diagnostics" not in rendered
        assert "authorization" not in rendered
