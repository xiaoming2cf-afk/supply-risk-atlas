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
    assert data["api_commit"] == "abcdef1234567890"
    assert data["git_commit"] == "abcdef1234567890"
    assert data["build_time"] == "2026-05-12T12:00:00Z"
    assert data["app_version"] == "0.1.0"
    assert data["data_mode"] == "fixture"
    assert data["graph_mode"] == "fixture"
    assert data["storage_mode"] == "memory"
    assert data["environment"] == "render"
    assert data["runtime_env"] == "render"
    assert data["source_status"] == "partial"
    assert data["web_commit"] == "not_verified"
    assert data["commit_mismatch"] is False
    assert data["deployment_readiness_state"] == "stale_or_unverified"
    assert data["deployment_stale_or_unverified"] is True
    assert data["deployment_unavailable"] is False
    assert data["last_checked_at"].endswith("Z")
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
    assert body["data"]["api_commit"] == "fedcba9876543210"
    assert body["data"]["environment"] in {"local", "render", "unknown"}
    _assert_sanitized_version(body)


def test_version_endpoint_reports_commit_mismatch_without_raw_environment(monkeypatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GIT_COMMIT", "aaaaaaaaaaaaaaa")
    monkeypatch.setenv("NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT", "bbbbbbbbbbbbbbb")
    monkeypatch.setenv("SUPPLY_RISK_STORAGE_MODE", "memory")

    payload = main.route_version(request_id="req_version_mismatch")
    data = payload["data"]

    assert data["api_commit"] == "aaaaaaaaaaaaaaa"
    assert data["web_commit"] == "bbbbbbbbbbbbbbb"
    assert data["commit_mismatch"] is True
    assert data["deployment_readiness_state"] == "stale_or_unverified"
    assert data["deployment_stale_or_unverified"] is True
    _assert_sanitized_version(payload)


def test_version_endpoint_accepts_prefix_equivalent_api_and_web_commits(monkeypatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GIT_COMMIT", "aaaaaaaaaaaaaaa")
    monkeypatch.setenv("NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT", "aaaaaaa")
    monkeypatch.setenv("SUPPLY_RISK_STORAGE_MODE", "memory")

    payload = main.route_version(request_id="req_version_prefix_match")
    data = payload["data"]

    assert data["commit_mismatch"] is False
    assert data["deployment_readiness_state"] == "commit_reported"
    assert data["deployment_stale_or_unverified"] is False
    _assert_sanitized_version(payload)


def test_version_endpoint_sanitizes_non_hex_commits_and_sensitive_build_time(monkeypatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GIT_COMMIT", "release-secret-token")
    monkeypatch.setenv("SUPPLY_RISK_WEB_COMMIT", "web-build-not-a-sha")
    monkeypatch.setenv("SUPPLY_RISK_BUILD_TIME", "https://private.example/build?token=secret")

    payload = main.route_version(request_id="req_version_sanitized_env")
    data = payload["data"]
    rendered = json.dumps(payload, sort_keys=True).lower()

    assert data["api_commit"] == "unknown"
    assert data["web_commit"] == "unknown"
    assert data["build_time"] == "unknown"
    assert data["deployment_readiness_state"] == "unavailable"
    assert "secret" not in rendered
    assert "private.example" not in rendered
    _assert_sanitized_version(payload)


def test_version_endpoint_reports_unavailable_deployment_state(monkeypatch) -> None:
    monkeypatch.delenv("SUPPLY_RISK_GIT_COMMIT", raising=False)
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)
    monkeypatch.delenv("GIT_COMMIT", raising=False)
    monkeypatch.delenv("COMMIT_SHA", raising=False)
    monkeypatch.setattr("services.api.services.version_service.current_git_commit", lambda: "unknown")

    payload = main.route_version(request_id="req_version_unavailable")
    data = payload["data"]

    assert data["deployment_readiness_state"] == "unavailable"
    assert data["deployment_unavailable"] is True
    assert data["deployment_stale_or_unverified"] is False
    _assert_sanitized_version(payload)
