from __future__ import annotations

from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.risk_scoring.semirisk_score import score_semirisk_entity
from ml.risk_scoring.weighting import clamp01
from sra_core.contracts.semiconductor import SemiriskGraphSnapshot


ABLATION_FACTORS = [
    "concentration",
    "substitution_gap",
    "policy_risk",
    "event_pressure",
    "market_pressure",
    "recovery_difficulty",
]


def ablated_score(
    node_id: str,
    factor: str,
    *,
    snapshot: SemiriskGraphSnapshot | None = None,
) -> dict[str, Any]:
    if factor not in ABLATION_FACTORS:
        raise ValueError(f"unsupported ablation factor: {factor}")
    graph = snapshot or build_semiconductor_fixture_snapshot()
    baseline = score_semirisk_entity(node_id, snapshot=graph)
    likelihood = float(baseline["likelihood"])
    impact = float(baseline["impact"])
    vulnerability = float(baseline["vulnerability_modifier"])
    adjustments = _factor_adjustments(graph, node_id, baseline)
    adjusted_likelihood = clamp01(likelihood - adjustments[factor]["likelihood_reduction"])
    adjusted_impact = clamp01(impact - adjustments[factor]["impact_reduction"])
    adjusted_vulnerability = clamp01(vulnerability - adjustments[factor]["vulnerability_reduction"])
    score = round(100.0 * adjusted_likelihood * adjusted_impact * adjusted_vulnerability, 2)
    return {
        "node_id": node_id,
        "ablation_factor": factor,
        "baseline_score": baseline["score"],
        "ablated_score": score,
        "score_delta": round(score - float(baseline["score"]), 4),
        "baseline_likelihood": likelihood,
        "ablated_likelihood": adjusted_likelihood,
        "baseline_impact": impact,
        "ablated_impact": adjusted_impact,
        "baseline_vulnerability_modifier": vulnerability,
        "ablated_vulnerability_modifier": adjusted_vulnerability,
        "affected_explanation_fields": adjustments[factor]["affected_explanation_fields"],
        "formula_refs": baseline.get("formula_refs", []),
        "evidence_refs": baseline.get("evidence_refs", []),
        "warnings": sorted(
            {
                "fixture_graph:not_production_ready",
                "ablation_fixture_proxy:not_calibrated",
                *baseline.get("warnings", []),
            }
        ),
    }


def ablation_rows(
    snapshot: SemiriskGraphSnapshot,
    *,
    node_ids: list[str],
    factors: list[str] | None = None,
) -> list[dict[str, Any]]:
    selected_factors = factors or ABLATION_FACTORS
    baseline_rank = _rank({node_id: score_semirisk_entity(node_id, snapshot=snapshot)["score"] for node_id in node_ids})
    rows: list[dict[str, Any]] = []
    for factor in selected_factors:
        factor_scores = {node_id: ablated_score(node_id, factor, snapshot=snapshot)["ablated_score"] for node_id in node_ids}
        factor_rank = _rank(factor_scores)
        for node_id in sorted(node_ids):
            row = ablated_score(node_id, factor, snapshot=snapshot)
            row["baseline_rank"] = baseline_rank[node_id]
            row["ablated_rank"] = factor_rank[node_id]
            row["rank_delta"] = factor_rank[node_id] - baseline_rank[node_id]
            rows.append(row)
    return rows


def _factor_adjustments(graph: SemiriskGraphSnapshot, node_id: str, baseline: dict[str, Any]) -> dict[str, dict[str, Any]]:
    context_edges = [
        edge
        for edge in graph.edges
        if edge.source_node_id == node_id or edge.target_node_id == node_id
    ]
    policy_pressure = _edge_pressure(context_edges, "restricted_by")
    event_pressure = _edge_pressure(context_edges, "impacted_by")
    market_pressure = _edge_pressure(context_edges, "correlated_with")
    concentration_hhi = float(
        baseline.get("concentration", {})
        .get("source_concentration", {})
        .get("hhi", 0.0)
    )
    substitution = float(
        baseline.get("concentration", {})
        .get("substitution", {})
        .get("substitution_gap", 0.0)
    )
    recovery_difficulty = 0.20
    return {
        "concentration": {
            "likelihood_reduction": 0.0,
            "impact_reduction": 0.0,
            "vulnerability_reduction": min(0.35, concentration_hhi * 0.35),
            "affected_explanation_fields": ["vulnerability_modifier", "source_concentration_hhi", "country_concentration"],
        },
        "substitution_gap": {
            "likelihood_reduction": 0.0,
            "impact_reduction": 0.0,
            "vulnerability_reduction": min(0.25, substitution * 0.25),
            "affected_explanation_fields": ["vulnerability_modifier", "substitution_gap"],
        },
        "policy_risk": {
            "likelihood_reduction": min(0.30, policy_pressure * 0.35),
            "impact_reduction": 0.0,
            "vulnerability_reduction": min(0.15, policy_pressure * 0.20),
            "affected_explanation_fields": ["likelihood", "vulnerability_modifier", "restricted_by"],
        },
        "event_pressure": {
            "likelihood_reduction": min(0.25, event_pressure * 0.35),
            "impact_reduction": 0.0,
            "vulnerability_reduction": min(0.12, event_pressure * 0.15),
            "affected_explanation_fields": ["likelihood", "vulnerability_modifier", "impacted_by"],
        },
        "market_pressure": {
            "likelihood_reduction": min(0.20, market_pressure * 0.25),
            "impact_reduction": 0.0,
            "vulnerability_reduction": 0.0,
            "affected_explanation_fields": ["likelihood", "market_indicator"],
        },
        "recovery_difficulty": {
            "likelihood_reduction": 0.0,
            "impact_reduction": min(0.10, recovery_difficulty * 0.10),
            "vulnerability_reduction": min(0.10, recovery_difficulty * 0.15),
            "affected_explanation_fields": ["impact", "vulnerability_modifier", "recovery_difficulty"],
        },
    }


def _edge_pressure(edges: list[Any], edge_type: str) -> float:
    values = [float(edge.weight) * float(edge.confidence) for edge in edges if edge.edge_type == edge_type]
    return clamp01(max(values) if values else 0.0)


def _rank(scores: dict[str, float]) -> dict[str, int]:
    ranked = sorted(scores.items(), key=lambda item: (-float(item[1]), item[0]))
    return {node_id: index + 1 for index, (node_id, _) in enumerate(ranked)}
