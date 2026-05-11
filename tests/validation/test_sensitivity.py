from __future__ import annotations

import json

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.validation.sensitivity import (
    concentration_level_for_thresholds,
    hhi_sensitivity_rows,
    significant_dependency_for_reference,
)


def test_hhi_sensitivity_flips_and_fixture_warnings_are_deterministic() -> None:
    snapshot = build_semiconductor_fixture_snapshot()

    first = hhi_sensitivity_rows(snapshot, node_ids=["company:tsmc"])
    second = hhi_sensitivity_rows(snapshot, node_ids=["company:tsmc"])

    assert first == second
    assert any(row["significant_dependency_flipped_from_base"] for row in first)
    assert all(row["threshold_policy"] == "oecd_derived_supply_chain" for row in first)
    assert any("fixture_proxy_supplier_shares" in row["warnings"] for row in first)
    assert "raw_payload" not in json.dumps(first)


def test_threshold_helpers_follow_operational_policy() -> None:
    assert concentration_level_for_thresholds(0.19, low_cutoff=0.20, high_cutoff=0.40) == "low"
    assert concentration_level_for_thresholds(0.20, low_cutoff=0.20, high_cutoff=0.40) == "moderate"
    assert concentration_level_for_thresholds(0.40, low_cutoff=0.20, high_cutoff=0.40) == "high"
    assert significant_dependency_for_reference(0.50, 0.20) is True
    assert significant_dependency_for_reference(0.40, 0.20) is False
    assert significant_dependency_for_reference(0.50, 0.15) is False

