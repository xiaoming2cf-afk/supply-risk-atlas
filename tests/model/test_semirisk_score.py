from __future__ import annotations

import json

import pytest

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.risk_scoring.semirisk_score import (
    FEATURE_VERSION,
    RISK_SCORE_WARNING_FIXTURE_GRAPH,
    RiskScoreUnavailable,
    level_for_score,
    rank_risk_portfolio,
    score_semirisk_entity,
)


def _assert_no_raw_payload(payload: object) -> None:
    text = json.dumps(payload, sort_keys=True)
    assert "raw_payload" not in text
    assert "private_diagnostics" not in text


def test_semirisk_score_for_tsmc_is_deterministic() -> None:
    snapshot = build_semiconductor_fixture_snapshot(as_of_time="2026-05-01T00:00:00Z")

    first = score_semirisk_entity("company:tsmc", snapshot=snapshot)
    second = score_semirisk_entity("company:tsmc", snapshot=snapshot)

    assert first == second
    assert first["node_id"] == "company:tsmc"
    assert first["score"] == 58.33
    assert first["level"] == "elevated"
    assert first["feature_version"] == FEATURE_VERSION
    assert first["graph_version"] == snapshot.graph_version
    assert first["source_manifest_id"] == snapshot.source_manifest_id
    assert first["fixture_graph"] is True
    assert RISK_SCORE_WARNING_FIXTURE_GRAPH in first["warnings"]
    _assert_no_raw_payload(first)


def test_semirisk_score_components_are_evidence_backed_and_consistent() -> None:
    payload = score_semirisk_entity("company:tsmc")

    components = {component["name"]: component for component in payload["components"]}
    assert set(components) == {
        "exposure_score",
        "criticality_score",
        "substitution_gap",
        "policy_risk",
        "event_pressure",
        "market_pressure",
    }
    assert all(0 <= component["value"] <= 100 for component in components.values())
    assert all(component["evidence_refs"] for component in components.values())
    contribution_sum = round(
        sum(component["weighted_contribution"] for component in components.values()),
        2,
    )
    assert contribution_sum == payload["score"]
    assert payload["evidence_refs"]


def test_semirisk_score_range_and_levels() -> None:
    assert level_for_score(0) == "low"
    assert level_for_score(25) == "guarded"
    assert level_for_score(50) == "elevated"
    assert level_for_score(70) == "severe"
    assert level_for_score(85) == "critical"

    portfolio = rank_risk_portfolio(limit=5)
    assert portfolio["scores"]
    assert all(0 <= item["score"] <= 100 for item in portfolio["scores"])
    assert portfolio["scores"] == sorted(
        portfolio["scores"],
        key=lambda item: (-item["score"], item["node_id"]),
    )
    _assert_no_raw_payload(portfolio)


def test_semirisk_score_missing_node_is_unavailable_not_fabricated() -> None:
    with pytest.raises(RiskScoreUnavailable):
        score_semirisk_entity("company:not_real")
