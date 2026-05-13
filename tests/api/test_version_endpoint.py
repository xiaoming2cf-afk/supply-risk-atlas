from __future__ import annotations

import json

from fastapi.testclient import TestClient

from services.api import main


def _assert_sanitized_version(payload: dict[str, object]) -> None:
    text = json.dumps(payload, sort_keys=True)
    assert "supply_risk_atlas.db" not in text
    assert "data/runtime" not in text.replace("\\", "/")
    assert "Authorization" not in text
    assert "cookie" not in text.lower()


def test_route_version_returns_sanitized_deployment_metadata(monkeypatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GIT_COMMIT", "abcdef1234567890")
    monkeypatch.setenv("SUPPLY_RISK_BUILD_TIME", "2026-05-12T12:00:00Z")
    monkeypatch.setenv("SUPPLY_RISK_ENV", "production")
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "fixture")
    monkeypatch.setenv("SUPPLY_RISK_STORAGE_MODE", "memory")

    payload = main.route_version(request_id="req_version")

    assert payload["request_id"] == "req_version"
    assert payload["status"] == "success"
    data = payload["data"]
    assert data["git_commit"] == "abcdef1234567890"
    assert data["build_time"] == "2026-05-12T12:00:00Z"
    assert data["app_version"] == "0.1.0"
    assert data["data_mode"] == "fixture"
    assert data["graph_mode"] == "fixture"
    assert data["storage_mode"] == "memory"
    assert data["environment"] == "render"
    assert data["not_production_ready"] is True
    assert data["graph_version"].startswith("semirisk_kg_v0_1_")
    assert data["source_manifest_id"].startswith("semirisk_fixture_manifest_")
    assert "not_production_ready" in data["warnings"]
    _assert_sanitized_version(payload)


def test_fastapi_version_endpoint_is_registered(monkeypatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GIT_COMMIT", "fedcba9876543210")
    app = main.create_app()
    assert app is not None

    client = TestClient(app)
    response = client.get("/api/v1/version", headers={"x-request-id": "req_http_version"})

    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == "req_http_version"
    assert body["data"]["git_commit"] == "fedcba9876543210"
    assert body["data"]["environment"] in {"local", "render", "unknown"}
    _assert_sanitized_version(body)
