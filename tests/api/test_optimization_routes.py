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
        "budget": 70,
        "allowed_intervention_types": ["add_alternative_supplier", "increase_inventory_buffer", "add_policy_monitoring"],
        "max_actions": 3,
        "risk_aversion_beta": 0.7,
        "compliance_constraints": {
            "no_export_control_evasion": True,
            "no_sanctions_circumvention": True,
        },
        "seed": 42,
        "as_of_time": "2026-05-01T00:00:00Z",
    }


def _assert_safe(payload: object) -> None:
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


def test_optimization_route_returns_budget_feasible_actions() -> None:
    response = main.route_intervention_optimization(_payload(), request_id="req_opt")

    assert response["request_id"] == "req_opt"
    assert response["status"] == "success"
    data = response["data"]
    assert data["optimization_version"] == "semirisk_intervention_optimizer_v0.1"
    assert data["optimization_context_type"] == "default_fixture_scenario"
    assert data["scenario_count"] == 1
    assert data["before_simulation_run_ids"]
    assert data["after_simulation_run_ids"]
    assert data["cost"] <= data["budget"]
    assert data["after_cvar95"] <= data["before_cvar95"]
    assert data["recommended_actions"]
    assert data["baseline_comparison"]
    _assert_safe(response)


def test_fastapi_optimization_endpoint() -> None:
    app = main.create_app()
    assert app is not None
    client = TestClient(app)

    response = client.post("/api/v1/optimization/interventions", json=_payload())

    assert response.status_code == 200
    assert response.json()["data"]["run_id"].startswith("opt_")
    _assert_safe(response.json())


def test_dev_server_optimization_endpoint(dev_server_base_url: str) -> None:
    status, body = _post_json(dev_server_base_url, "/api/v1/optimization/interventions", _payload())

    assert status == 200
    assert body["status"] == "success"
    assert body["data"]["recommended_actions"]
    _assert_safe(body)
