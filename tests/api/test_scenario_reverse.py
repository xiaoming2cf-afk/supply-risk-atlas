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
        "target_metric": "cvar95_loss",
        "failure_threshold": 35,
        "candidate_scope": {
            "node_types": ["company", "equipment", "material", "chemical", "process_stage", "product_grade"],
            "edge_types": [],
        },
        "max_combination_size": 2,
        "beam_width": 4,
        "iterations_per_candidate": 30,
        "seed": 42,
        "as_of_time": "2026-05-01T00:00:00Z",
    }


def _assert_no_raw_or_unsafe(payload: object) -> None:
    text = json.dumps(payload, sort_keys=True).lower()
    assert "raw_payload" not in text
    assert "private_diagnostics" not in text
    assert "evad" not in text
    assert "circumvent" not in text
    assert "bypass" not in text


def _post_json(base_url: str, path: str, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
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


def test_route_reverse_scenario_returns_ranked_shock_sets() -> None:
    response = main.route_reverse_scenario(_payload(), request_id="req_reverse")

    assert response["request_id"] == "req_reverse"
    assert response["status"] == "success"
    data = response["data"]
    assert data["run_id"].startswith("rev_")
    assert data["seed"] == 42
    assert data["simulation_version"] == "semirisk_reverse_stress_v0.1"
    assert data["failure_threshold_input"] == 35
    assert data["failure_threshold_normalized"] == 35
    assert data["threshold_metric_basis"] == "normalized_0_to_100_resilience_loss_score"
    assert data["loss_mode"] == "resilience_integral_loss"
    assert data["propagation_mode"] == "auto_semiconductor"
    assert data["ranked_shock_sets"]
    assert data["ranked_shock_sets"][0]["shock_set_id"].startswith("shockset_")
    assert data["baseline_comparison"]
    assert data["evidence_refs"]
    assert "fixture_graph:not_production_ready" in response["warnings"]
    _assert_no_raw_or_unsafe(response)


def test_route_reverse_scenario_controlled_validation_error() -> None:
    payload = _payload()
    payload["target_metric"] = "not_real"
    response = main.route_reverse_scenario(payload, request_id="req_reverse_bad")

    assert response["status"] == "error"
    assert response["errors"][0]["code"] == "reverse_scenario_validation_error"
    assert response["errors"][0]["field"] == "target_metric"


def test_fastapi_reverse_scenario_endpoint() -> None:
    app = main.create_app()
    assert app is not None
    client = TestClient(app)

    response = client.post("/api/v1/scenarios/reverse", json=_payload())

    assert response.status_code == 200
    assert response.json()["data"]["simulation_version"] == "semirisk_reverse_stress_v0.1"
    assert response.json()["data"]["ranked_shock_sets"]
    _assert_no_raw_or_unsafe(response.json())


def test_dev_server_reverse_scenario_endpoint(dev_server_base_url: str) -> None:
    status, body = _post_json(dev_server_base_url, "/api/v1/scenarios/reverse", _payload())

    assert status == 200
    assert body["status"] == "success"
    assert body["data"]["ranked_shock_sets"]
    _assert_no_raw_or_unsafe(body)
