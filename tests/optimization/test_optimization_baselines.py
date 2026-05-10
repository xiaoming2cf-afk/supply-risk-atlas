from __future__ import annotations

from ml.optimization.interventions import run_intervention_optimization


def test_optimization_baselines_are_present() -> None:
    result = run_intervention_optimization({
        "budget": 100,
        "max_actions": 4,
        "risk_aversion_beta": 0.7,
        "seed": 7,
        "as_of_time": "2026-05-01T00:00:00Z",
    })

    baselines = {row["baseline"] for row in result["baseline_comparison"]}
    assert {
        "random_intervention",
        "highest_risk_score_protection",
        "cheapest_first",
        "proposed_risk_adjusted_greedy_optimizer",
    } <= baselines

