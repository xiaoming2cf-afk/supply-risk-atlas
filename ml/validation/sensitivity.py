from __future__ import annotations

from typing import Any, Iterable

from ml.risk_scoring.concentration import (
    country_concentration_by_input,
    source_concentration_by_node,
    substitution_gap,
)
from sra_core.contracts.semiconductor import SemiriskGraphSnapshot


DEFAULT_THRESHOLD_PAIRS = [
    {"low_cutoff": 0.18, "high_cutoff": 0.38},
    {"low_cutoff": 0.20, "high_cutoff": 0.40},
    {"low_cutoff": 0.22, "high_cutoff": 0.42},
]


def concentration_level_for_thresholds(hhi: float, *, low_cutoff: float, high_cutoff: float) -> str:
    value = max(0.0, min(1.0, float(hhi)))
    if value < low_cutoff:
        return "low"
    if value < high_cutoff:
        return "moderate"
    return "high"


def significant_dependency_for_reference(country_level_hhi: float, global_reference_hhi: float) -> bool:
    country_hhi = max(0.0, min(1.0, float(country_level_hhi)))
    reference_hhi = max(0.0, min(1.0, float(global_reference_hhi)))
    return country_hhi >= 0.40 and reference_hhi >= 0.20 and country_hhi > 2 * reference_hhi


def hhi_sensitivity_rows(
    snapshot: SemiriskGraphSnapshot,
    *,
    node_ids: Iterable[str] | None = None,
    global_reference_hhi_values: Iterable[float] = (0.15, 0.20, 0.25, 0.30),
    threshold_pairs: Iterable[dict[str, float]] = DEFAULT_THRESHOLD_PAIRS,
) -> list[dict[str, Any]]:
    target_ids = list(node_ids or [node.node_id for node in snapshot.nodes])
    rows: list[dict[str, Any]] = []
    for node_id in sorted(target_ids):
        source = source_concentration_by_node(snapshot, node_id)
        country = country_concentration_by_input(snapshot, node_id)
        substitution = substitution_gap(snapshot, node_id)
        for reference in global_reference_hhi_values:
            significant = significant_dependency_for_reference(float(country["hhi"]), float(reference))
            for thresholds in threshold_pairs:
                level = concentration_level_for_thresholds(
                    float(source["hhi"]),
                    low_cutoff=float(thresholds["low_cutoff"]),
                    high_cutoff=float(thresholds["high_cutoff"]),
                )
                baseline_level = concentration_level_for_thresholds(
                    float(source["hhi"]),
                    low_cutoff=0.20,
                    high_cutoff=0.40,
                )
                rows.append(
                    {
                        "node_id": node_id,
                        "source_hhi": source["hhi"],
                        "country_hhi": country["hhi"],
                        "substitution_gap": substitution["substitution_gap"],
                        "global_reference_hhi": round(float(reference), 4),
                        "low_cutoff": round(float(thresholds["low_cutoff"]), 4),
                        "high_cutoff": round(float(thresholds["high_cutoff"]), 4),
                        "concentration_level": level,
                        "level_changed_from_base": level != baseline_level,
                        "significant_dependency": significant,
                        "significant_dependency_flipped_from_base": significant != significant_dependency_for_reference(float(country["hhi"]), 0.20),
                        "threshold_policy": "oecd_derived_supply_chain",
                        "threshold_basis": "operational_supply_chain_trade_dependency_not_official_generic_oecd_label",
                        "source_refs": source.get("source_refs", []),
                        "warnings": sorted(
                            {
                                *source.get("warnings", []),
                                *country.get("warnings", []),
                                "fixture_graph:not_production_ready",
                            }
                        ),
                    }
                )
    return rows

