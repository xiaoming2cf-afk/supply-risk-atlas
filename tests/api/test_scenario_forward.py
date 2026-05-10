from __future__ import annotations

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from services.api import main
from services.api.dev_server import Handler

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient


def _payload() -> dict[str, object]:
    return {
        "scenario_type": "earthquake",
        "targets": ["company:tsmc"],
        "severity_distribution": {"type": "fixed", "params": {"value": 0.72}},
        "duration_days_distribution": {"type": "fixed", "params": {"value": 28}},
        "iterations": 80,
        "seed": 42,
        "as_of_time": "2026-05-01T00:00:00Z",
        "assumptions": ["fixture-only API test"],
    }


def _assert_no_raw_payload(payload: object) -> None:
    text = json.dumps(payload, sort_keys=True)
    assert "raw_payload" not in text
    assert "private_diagnostics" not in text


def _post_json(base_url: str, path: str, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=body,
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


@pytest.fixture()
def dev_server_base_url() -> str:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_route_forward_scenario_returns_required_manifest() -> None:
    response = main.route_forward_scenario(_payload(), request_id="req_forward")

    assert response["request_id"] == "req_forward"
    assert response["status"] == "success"
    data = response["data"]
    assert data["run_id"].startswith("fwd_")
    assert data["seed"] == 42
    assert data["graph_version"].startswith("semirisk_kg_v0_1_")
    assert data["source_manifest_id"].startswith("semirisk_fixture_manifest_")
    assert data["simulation_version"] == "semirisk_forward_mc_v0.1"
    assert data["p50_loss"] <= data["p90_loss"] <= data["p95_loss"] <= data["cvar_95"]
    assert data["affected_nodes"]
    assert data["top_transmission_paths"]
    assert data["evidence_refs"]
    assert "fixture_graph:not_production_ready" in response["warnings"]
    _assert_no_raw_payload(response)


def test_route_forward_scenario_rejects_unknown_target() -> None:
    payload = _payload()
    payload["targets"] = ["company:not_real"]
    response = main.route_forward_scenario(payload, request_id="req_forward_bad_target")

    assert response["status"] == "error"
    assert response["errors"][0]["code"] == "forward_scenario_validation_error"
    assert response["errors"][0]["field"] == "targets"
    assert response["data"] is None


def test_fastapi_forward_scenario_endpoint() -> None:
    app = main.create_app()
    assert app is not None
    client = TestClient(app)

    response = client.post(
        "/api/v1/scenarios/forward",
        json=_payload(),
        headers={"x-request-id": "req_http_forward"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == "req_http_forward"
    assert body["data"]["simulation_version"] == "semirisk_forward_mc_v0.1"
    _assert_no_raw_payload(body)


def test_dev_server_forward_scenario_endpoint(dev_server_base_url: str) -> None:
    status, body = _post_json(dev_server_base_url, "/api/v1/scenarios/forward", _payload())

    assert status == 200
    assert body["status"] == "success"
    assert body["data"]["seed"] == 42
    assert body["data"]["source_manifest_id"].startswith("semirisk_fixture_manifest_")
    _assert_no_raw_payload(body)

