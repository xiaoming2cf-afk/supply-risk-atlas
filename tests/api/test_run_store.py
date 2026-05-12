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


def _forward_payload() -> dict[str, object]:
    return {
        "scenario_type": "earthquake",
        "targets": ["company:tsmc"],
        "severity_distribution": {"type": "fixed", "params": {"value": 0.6}},
        "duration_days_distribution": {"type": "fixed", "params": {"value": 7}},
        "iterations": 5,
        "seed": 42,
        "as_of_time": "2026-05-01T00:00:00Z",
        "raw_payload": {"secret": "do-not-store"},
    }


def test_run_store_endpoints_list_and_get_sanitized_runs() -> None:
    main.RUN_STORE.clear()
    client = _client()

    created = client.post("/api/v1/scenarios/forward", json=_forward_payload(), headers={"x-request-id": "req_forward"})
    assert created.status_code == 200
    run_id = created.json()["data"]["run_id"]

    listed = client.get("/api/v1/runs", headers={"x-request-id": "req_runs"})
    listed_payload = listed.json()
    assert listed.status_code == 200
    assert listed_payload["status"] == "success"
    assert listed_payload["data"]["run_store_version"] == "semirisk_run_store_v0.1"
    listed_run = next(run for run in listed_payload["data"]["runs"] if run["run_id"] == run_id)
    assert listed_run["run_type"] == "forward_scenario"
    assert listed_run["graph_version"]
    assert listed_run["source_manifest_id"]
    assert listed_run["data_mode"]
    assert listed_run["graph_mode"]

    detail = client.get(f"/api/v1/runs/{run_id}", headers={"x-request-id": "req_run_detail"})
    detail_payload = detail.json()
    assert detail.status_code == 200
    assert detail_payload["status"] == "success"
    assert detail_payload["data"]["run_id"] == run_id
    assert detail_payload["data"]["raw_payload_excluded"] is True
    assert detail_payload["data"]["private_diagnostics_excluded"] is True

    rendered = json.dumps(detail_payload, sort_keys=True).lower()
    assert "do-not-store" not in rendered
    assert "secret" not in rendered


def test_run_store_not_found_uses_controlled_404() -> None:
    client = _client()

    response = client.get("/api/v1/runs/missing-run", headers={"x-request-id": "req_missing_run"})
    payload = response.json()

    assert response.status_code == 404
    assert payload["status"] == "error"
    assert payload["errors"][0]["code"] == "not_found"


def test_report_detail_endpoint_returns_sanitized_persisted_report() -> None:
    from services.api.services import report_service

    report_service.REPORT_STORE.clear()
    client = _client()
    response = client.post(
        "/api/v1/reports/investigation",
        json={"entity_id": "company:tsmc", "format": "json"},
        headers={"x-request-id": "req_report_create"},
    )
    assert response.status_code == 200
    report_id = response.json()["data"]["report_id"]

    detail = client.get(f"/api/v1/reports/{report_id}", headers={"x-request-id": "req_report_detail"})
    payload = detail.json()
    rendered = json.dumps(payload, sort_keys=True).lower()

    assert detail.status_code == 200
    assert payload["status"] == "success"
    assert payload["data"]["report_id"] == report_id
    assert payload["data"]["content_hash"]
    assert payload["data"]["raw_payload_excluded"] is True
    assert payload["data"]["private_diagnostics_excluded"] is True
    assert payload["data"]["data_mode"]
    assert payload["data"]["graph_mode"]
    assert '"raw_payload":' not in rendered
    assert '"private_diagnostics":' not in rendered
