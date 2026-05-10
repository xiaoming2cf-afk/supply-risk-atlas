from __future__ import annotations

import json

from ml.optimization.interventions import OPTIMIZATION_VERSION, run_intervention_optimization


def _payload(seed: int = 42) -> dict[str, object]:
    return {
        "budget": 70,
        "allowed_intervention_types": [
            "add_alternative_supplier",
            "increase_inventory_buffer",
            "regional_diversification",
            "improve_recovery_rate",
            "add_policy_monitoring",
            "route_redundancy",
            "qualify_backup_material",
        ],
        "max_actions": 3,
        "risk_aversion_beta": 0.7,
        "compliance_constraints": {
            "no_export_control_evasion": True,
            "no_sanctions_circumvention": True,
        },
        "seed": seed,
        "as_of_time": "2026-05-01T00:00:00Z",
    }


def test_intervention_optimizer_is_deterministic_and_budget_feasible() -> None:
    first = run_intervention_optimization(_payload())
    second = run_intervention_optimization(_payload())

    assert first == second
    assert first["run_id"].startswith("opt_")
    assert first["optimization_version"] == OPTIMIZATION_VERSION
    assert first["cost"] <= first["budget"]
    assert len(first["recommended_actions"]) <= 3
    assert first["after_expected_loss"] <= first["before_expected_loss"]
    assert first["after_cvar95"] <= first["before_cvar95"]
    assert first["evidence_refs"]
    assert "fixture_graph:not_production_ready" in first["warnings"]


def test_intervention_optimizer_respects_allowed_actions() -> None:
    result = run_intervention_optimization({
        **_payload(),
        "allowed_intervention_types": ["add_policy_monitoring"],
        "budget": 20,
        "max_actions": 5,
    })

    assert result["recommended_actions"]
    assert all(action["intervention_type"] == "add_policy_monitoring" for action in result["recommended_actions"])
    assert result["cost"] <= 20


def test_intervention_optimizer_has_no_raw_payload_or_unsafe_wording() -> None:
    text = json.dumps(run_intervention_optimization(_payload()), sort_keys=True).lower()

    assert "raw_payload" not in text
    assert "private_diagnostics" not in text
    assert "evad" not in text
    assert "circumvent" not in text
    assert "bypass" not in text

