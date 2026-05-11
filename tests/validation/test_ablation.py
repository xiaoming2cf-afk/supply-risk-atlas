from __future__ import annotations

import json

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.validation.ablation import ablated_score, ablation_rows


def test_ablation_neutralizes_named_factor_without_raw_payload() -> None:
    snapshot = build_semiconductor_fixture_snapshot()

    result = ablated_score("company:tsmc", "concentration", snapshot=snapshot)

    assert result["ablation_factor"] == "concentration"
    assert result["ablated_vulnerability_modifier"] <= result["baseline_vulnerability_modifier"]
    assert "source_concentration_hhi" in result["affected_explanation_fields"]
    assert "raw_payload" not in json.dumps(result, sort_keys=True)


def test_ablation_rows_are_deterministic_and_report_rank_changes() -> None:
    snapshot = build_semiconductor_fixture_snapshot()

    first = ablation_rows(snapshot, node_ids=["company:tsmc", "company:asml"], factors=["policy_risk", "event_pressure"])
    second = ablation_rows(snapshot, node_ids=["company:tsmc", "company:asml"], factors=["policy_risk", "event_pressure"])

    assert first == second
    assert {row["ablation_factor"] for row in first} == {"policy_risk", "event_pressure"}
    assert all("rank_delta" in row for row in first)
