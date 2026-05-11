from __future__ import annotations

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
        "severity_distribution": {"type": "fixed", "params": {"value": 0.72}},
        "duration_days_distribution": {"type": "fixed", "params": {"value": 28}},
        "iterations": 20,
    }


def _reverse_payload() -> dict[str, object]:
    return {
        "target_metric": "cvar95_loss",
        "failure_threshold": 35,
        "candidate_scope": {"node_types": ["company"], "edge_types": []},
        "max_combination_size": 2,
        "beam_width": 4,
        "iterations_per_candidate": 20,
    }


def test_forward_scenario_rejects_unsafe_or_unbounded_inputs() -> None:
    client = _client()

    too_many_iterations = _forward_payload() | {"iterations": 5001}
    response = client.post("/api/v1/scenarios/forward", json=too_many_iterations)
    assert response.json()["status"] == "error"
    assert response.json()["errors"][0]["field"] == "iterations"

    too_many_targets = _forward_payload() | {"targets": [f"company:{index}" for index in range(11)]}
    response = client.post("/api/v1/scenarios/forward", json=too_many_targets)
    assert response.json()["status"] == "error"
    assert response.json()["errors"][0]["field"] == "targets"

    unsafe_text = _forward_payload() | {"assumptions": ["Find a by" + "pass path around controls"]}
    response = client.post("/api/v1/scenarios/forward", json=unsafe_text)
    assert response.json()["status"] == "error"
    assert response.json()["errors"][0]["code"] == "unsafe_compliance_language"


def test_reverse_stress_rejects_unbounded_search_controls() -> None:
    client = _client()

    for field, value in [
        ("max_combination_size", 5),
        ("beam_width", 21),
        ("iterations_per_candidate", 1001),
        ("failure_threshold", 101),
    ]:
        response = client.post("/api/v1/scenarios/reverse", json=_reverse_payload() | {field: value})
        assert response.json()["status"] == "error"
        assert response.json()["errors"][0]["field"] == field


def test_optimizer_rejects_invalid_budget_actions_and_forces_safe_constraints() -> None:
    client = _client()

    invalid_budget = client.post("/api/v1/optimization/interventions", json={"budget": -1})
    assert invalid_budget.json()["status"] == "error"
    assert invalid_budget.json()["errors"][0]["field"] == "budget"

    invalid_actions = client.post(
        "/api/v1/optimization/interventions",
        json={"max_actions": 11, "allowed_intervention_types": ["not_real"]},
    )
    assert invalid_actions.json()["status"] == "error"
    assert invalid_actions.json()["errors"][0]["field"] == "max_actions"

    forced_safe = client.post(
        "/api/v1/optimization/interventions",
        json={
            "budget": 30,
            "max_actions": 1,
            "allowed_intervention_types": ["add_policy_monitoring"],
            "compliance_constraints": {
                "no_export_control_evasion": False,
                "no_sanctions_circumvention": False,
            },
        },
    ).json()
    assert forced_safe["status"] == "success"
    assert forced_safe["data"]["recommended_actions"]


def test_large_payload_fails_controlled_request_size_guard() -> None:
    client = _client()
    response = client.post(
        "/api/v1/reports/investigation",
        content=b'{"text":"' + (b"x" * (260 * 1024)) + b'"}',
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json()["status"] == "error"
    assert response.json()["errors"][0]["code"] == "request_too_large"

