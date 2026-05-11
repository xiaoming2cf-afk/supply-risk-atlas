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


def test_report_export_drops_raw_payload_private_diagnostics_and_scripts() -> None:
    response = _client().post(
        "/api/v1/reports/investigation",
        json={
            "entity_id": "company:tsmc",
            "format": "json",
            "raw_payload": {"secret": "do-not-echo"},
            "private_diagnostics": {"internal_path": "D:/secret"},
            "notes": "<script>alert(1)</script>",
        },
    )
    payload = response.json()
    rendered = json.dumps(payload, sort_keys=True).lower()

    assert payload["status"] == "success"
    assert '"raw_payload":' not in rendered
    assert '"private_diagnostics":' not in rendered
    assert "do-not-echo" not in rendered
    assert "<script>" not in rendered
    assert "internal_path" not in rendered


def test_report_rejects_unsupported_format_with_controlled_error() -> None:
    payload = _client().post("/api/v1/reports/investigation", json={"format": "html"}).json()

    assert payload["status"] == "error"
    assert payload["errors"][0]["code"] == "report_validation_error"
    assert payload["errors"][0]["field"] == "format"
    assert payload["data"] is None


def test_failed_endpoint_diagnostics_do_not_include_private_details() -> None:
    payload = _client().get("/api/v1/entities/missing").json()
    rendered = json.dumps(payload, sort_keys=True).lower()

    assert payload["status"] == "error"
    assert "traceback" not in rendered
    assert "api_key" not in rendered
    assert "token" not in rendered
    assert "d:\\" not in rendered
