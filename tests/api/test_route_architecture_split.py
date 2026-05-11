from __future__ import annotations

import json
from pathlib import Path

import pytest

from services.api import main

pytest.importorskip("fastapi")


def _forward_payload() -> dict[str, object]:
    return {
        "scenario_type": "earthquake",
        "targets": ["company:tsmc"],
        "severity_distribution": {"type": "fixed", "params": {"value": 0.5}},
        "duration_days_distribution": {"type": "fixed", "params": {"value": 7}},
        "iterations": 5,
    }


def _reverse_payload() -> dict[str, object]:
    return {
        "target_metric": "cvar95_loss",
        "failure_threshold": 35,
        "candidate_scope": {"node_types": ["company", "equipment", "material"], "edge_types": []},
        "max_combination_size": 1,
        "beam_width": 2,
        "iterations_per_candidate": 5,
    }


def test_gate1_route_and_runtime_modules_exist() -> None:
    root = Path("services/api")
    expected = [
        "routes/__init__.py",
        "routes/system_health.py",
        "routes/graph.py",
        "routes/risk.py",
        "routes/scenarios.py",
        "routes/reverse_stress.py",
        "routes/optimization.py",
        "routes/reports.py",
        "runtime/__init__.py",
        "runtime/envelope.py",
        "runtime/errors.py",
        "runtime/cache.py",
        "security/__init__.py",
        "security/validation.py",
        "security/headers.py",
    ]

    missing = [path for path in expected if not (root / path).exists()]
    assert missing == []


def test_gate1_public_routes_remain_registered() -> None:
    app = main.create_app()
    assert app is not None
    registered = {(route.path, ",".join(sorted(route.methods or []))) for route in app.routes}
    paths = {path for path, _methods in registered}

    assert "/api/v1/dashboard/system-health-center" in paths
    assert "/api/v1/graph/snapshot" in paths
    assert "/api/v1/graph/neighborhood" in paths
    assert "/api/v1/risk/entities/{entity_id}" in paths
    assert "/api/v1/risk/portfolio" in paths
    assert "/api/v1/scenarios/forward" in paths
    assert "/api/v1/scenarios/reverse" in paths
    assert "/api/v1/optimization/interventions" in paths
    assert "/api/v1/reports/investigation" in paths


def test_gate1_main_route_functions_remain_import_compatible() -> None:
    assert main.route_system_health_center()["status"] == "success"
    assert main.route_semiconductor_graph_snapshot()["status"] == "success"
    assert main.route_semiconductor_graph_neighborhood(node_id="company:tsmc")["status"] == "success"
    assert main.route_semirisk_entity_risk("company:tsmc")["status"] == "success"
    assert main.route_semirisk_risk_portfolio()["status"] == "success"
    assert main.route_forward_scenario(_forward_payload())["status"] == "success"
    assert main.route_reverse_scenario(_reverse_payload())["status"] == "success"
    assert main.route_intervention_optimization({"max_actions": 1})["status"] == "success"
    assert main.route_investigation_report({"entity_id": "company:tsmc"})["status"] == "success"


def test_gate1_runtime_caches_are_bounded_and_sanitized() -> None:
    main.route_semiconductor_graph_snapshot()
    assert main.SNAPSHOT_CACHE.keys()

    response = main.route_forward_scenario(
        {
            **_forward_payload(),
            "raw_payload": {"secret": "do-not-store"},
        }
    )
    assert response["status"] == "success"

    summaries = main.RUN_CACHE.list_summaries()
    assert summaries
    rendered = json.dumps(summaries, sort_keys=True).lower()
    assert "raw_payload" not in rendered
    assert "do-not-store" not in rendered
    assert "secret" not in rendered
