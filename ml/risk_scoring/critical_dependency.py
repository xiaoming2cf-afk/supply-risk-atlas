from __future__ import annotations

from typing import Any

from sra_core.contracts.semiconductor import SemiriskGraphSnapshot

from .concentration import source_concentration_by_node, substitution_gap
from .weighting import clamp01


FORMULA_REFS = [
    "nist_sp_800_30_r1_likelihood_impact",
    "oecd_supply_chain_resilience_critical_dependency",
    "oecd_trade_dependency_hhi_concentration",
]


def critical_dependency_importance(snapshot: SemiriskGraphSnapshot, node_id: str) -> dict[str, Any]:
    incident = [
        edge
        for edge in snapshot.edges
        if edge.source_node_id == node_id or edge.target_node_id == node_id
    ]
    max_degree = max(
        (
            sum(
                edge.weight * edge.confidence
                for edge in snapshot.edges
                if edge.source_node_id == node.node_id or edge.target_node_id == node.node_id
            )
            for node in snapshot.nodes
        ),
        default=0.0,
    )
    weighted_degree = sum(edge.weight * edge.confidence for edge in incident)
    graph_importance = clamp01(weighted_degree / max_degree) if max_degree else 0.0
    concentration = source_concentration_by_node(snapshot, node_id)
    substitution = substitution_gap(snapshot, node_id)
    supply_demand_risk = max(float(concentration["hhi"]), float(substitution["substitution_gap"]))
    strategic_bonus = 0.15 if node_id.startswith(("company:", "equipment:", "material:", "chemical:", "product_grade:")) else 0.0
    strategic_importance = clamp01(graph_importance + strategic_bonus)
    critical_dependency_score = clamp01(max(graph_importance, (supply_demand_risk + strategic_importance) / 2.0))
    return {
        "node_id": node_id,
        "critical_dependency_score": round(critical_dependency_score, 6),
        "supply_demand_risk": round(supply_demand_risk, 6),
        "strategic_importance": round(strategic_importance, 6),
        "graph_importance": round(graph_importance, 6),
        "formula_refs": FORMULA_REFS,
        "source_refs": concentration.get("source_refs", [])[:5],
        "warnings": ["fixture_proxy_critical_dependency"],
    }
