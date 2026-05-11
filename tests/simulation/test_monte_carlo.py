from __future__ import annotations

import json

import pytest

from ml.simulation.monte_carlo import run_forward_monte_carlo
from ml.simulation.scenario_schema import ScenarioValidationError


def _payload(seed: int = 42, distribution: str = "fixed") -> dict[str, object]:
    severity = (
        {"type": "beta", "params": {"alpha": 2, "beta": 3, "scale": 0.9, "loc": 0.05}}
        if distribution == "beta"
        else {"type": "fixed", "params": {"value": 0.72}}
    )
    return {
        "scenario_type": "earthquake",
        "targets": ["company:tsmc"],
        "severity_distribution": severity,
        "duration_days_distribution": {"type": "fixed", "params": {"value": 28}},
        "iterations": 120,
        "seed": seed,
        "as_of_time": "2026-05-01T00:00:00Z",
        "assumptions": ["fixture-only test scenario"],
    }


def test_forward_monte_carlo_is_deterministic_for_fixed_seed() -> None:
    first = run_forward_monte_carlo(_payload())
    second = run_forward_monte_carlo(_payload())

    assert first == second
    assert first["run_id"].startswith("fwd_")
    assert first["seed"] == 42
    assert first["graph_version"].startswith("semirisk_kg_v0_1_")
    assert first["source_manifest_id"].startswith("semirisk_fixture_manifest_")
    assert first["simulation_version"] == "semirisk_forward_mc_v0.1"
    assert first["loss_mode"] == "resilience_integral_loss"
    assert first["propagation_mode"] == "auto_semiconductor"
    assert first["expected_loss"] == first["resilience_integral_loss"]
    assert first["formula_refs"]
    assert first["calibration_status"] == "fixture_proxy_not_calibrated"
    assert first["evidence_refs"]
    assert "fixture_graph:not_production_ready" in first["warnings"]


def test_forward_monte_carlo_distribution_metrics_are_ordered() -> None:
    result = run_forward_monte_carlo(_payload(seed=7, distribution="beta"))

    assert 0 <= result["expected_loss"] <= 100
    assert result["p50_loss"] <= result["p90_loss"] <= result["p95_loss"] <= result["cvar_95"]
    assert result["time_to_recover_days"] >= result["time_to_survive_days"] >= 1
    assert result["affected_nodes"]
    assert result["top_transmission_paths"]
    assert result["loss_distribution_summary"]["count"] == 120
    text = json.dumps(result, sort_keys=True)
    assert "raw_payload" not in text
    assert "private_diagnostics" not in text


def test_forward_monte_carlo_seed_variation_is_bounded() -> None:
    first = run_forward_monte_carlo(_payload(seed=1, distribution="beta"))
    second = run_forward_monte_carlo(_payload(seed=2, distribution="beta"))

    assert first["run_id"] != second["run_id"]
    assert abs(first["expected_loss"] - second["expected_loss"]) <= 35


def test_forward_monte_carlo_rejects_invalid_scenario_and_unknown_target() -> None:
    invalid = _payload()
    invalid["scenario_type"] = "made_up"
    with pytest.raises(ScenarioValidationError):
        run_forward_monte_carlo(invalid)

    unknown = _payload()
    unknown["targets"] = ["company:not_real"]
    with pytest.raises(ScenarioValidationError):
        run_forward_monte_carlo(unknown)

    bad_mode = _payload()
    bad_mode["propagation_mode"] = "made_up"
    with pytest.raises(ScenarioValidationError):
        run_forward_monte_carlo(bad_mode)
