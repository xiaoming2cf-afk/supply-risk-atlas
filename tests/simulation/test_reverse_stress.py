from __future__ import annotations

import json

import pytest

from ml.simulation.reverse_stress import run_reverse_stress
from ml.simulation.scenario_schema import ScenarioValidationError
from ml.simulation.shock_candidates import generate_shock_candidates
from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot


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
        "iterations_per_candidate": 40,
        "seed": 42,
        "as_of_time": "2026-05-01T00:00:00Z",
    }


def test_shock_candidates_are_evidence_backed() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    candidates = generate_shock_candidates(snapshot, candidate_scope={"node_types": ["company"]})

    assert candidates
    assert candidates[0]["target_id"].startswith("company:")
    assert candidates[0]["evidence_refs"]


def test_reverse_stress_is_deterministic_and_ranked() -> None:
    first = run_reverse_stress(_payload())
    second = run_reverse_stress(_payload())

    assert first == second
    assert first["run_id"].startswith("rev_")
    assert first["simulation_version"] == "semirisk_reverse_stress_v0.1"
    assert first["graph_version"].startswith("semirisk_kg_v0_1_")
    assert first["source_manifest_id"].startswith("semirisk_fixture_manifest_")
    assert first["ranked_shock_sets"]
    assert first["ranked_shock_sets"][0]["shock_set_id"].startswith("shockset_")
    assert first["ranked_shock_sets"][0]["affected_paths"]
    assert first["baseline_comparison"]
    assert "fixture_graph:not_production_ready" in first["warnings"]


def test_reverse_stress_threshold_and_safety_language() -> None:
    result = run_reverse_stress(_payload())
    top = result["ranked_shock_sets"][0]

    assert top["threshold_met"] is True
    assert top["plausibility_cost"] >= 0
    text = json.dumps(result, sort_keys=True).lower()
    assert "raw_payload" not in text
    assert "private_diagnostics" not in text
    assert "evad" not in text
    assert "circumvent" not in text
    assert "bypass" not in text


def test_reverse_stress_rejects_invalid_metric_and_empty_candidates() -> None:
    invalid = _payload()
    invalid["target_metric"] = "made_up"
    with pytest.raises(ScenarioValidationError):
        run_reverse_stress(invalid)

    empty = _payload()
    empty["candidate_scope"] = {"node_types": ["not_a_node_type"], "edge_types": []}
    with pytest.raises(ScenarioValidationError):
        run_reverse_stress(empty)

