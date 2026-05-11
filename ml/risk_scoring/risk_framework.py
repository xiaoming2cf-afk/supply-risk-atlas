from __future__ import annotations

from typing import Any

from sra_core.contracts.semiconductor import SemiriskEdge, SemiriskGraphSnapshot, SemiriskNode

from .concentration import country_concentration_by_input, source_concentration_by_node, substitution_gap
from .critical_dependency import critical_dependency_importance
from .weighting import bounded_mean, clamp01, noisy_or


FORMULA_VERSION = "semirisk_liv_framework_v0.1"
FEATURE_VERSION = "semirisk_risk_score_likelihood_impact_v0.1"
SCORING_METHOD = "likelihood_impact_vulnerability_framework"
CALIBRATION_STATUS = "fixture_proxy_not_calibrated"
FORMULA_REFS = [
    "nist_sp_800_30_r1_likelihood_impact",
    "oecd_supply_chain_resilience_critical_dependency",
    "oecd_trade_dependency_hhi_concentration",
    "resilience_triangle_functionality_loss",
    "production_network_input_output_propagation",
    "production_shortage_interdependency_perfect_complements",
]


def score_likelihood_impact_vulnerability(
    snapshot: SemiriskGraphSnapshot,
    node: SemiriskNode,
    *,
    context_edges: list[SemiriskEdge],
) -> dict[str, Any]:
    policy_edges = [edge for edge in context_edges if edge.edge_type == "restricted_by"]
    event_edges = [edge for edge in context_edges if edge.edge_type == "impacted_by"]
    market_edges = [
        edge
        for edge in context_edges
        if edge.edge_type == "correlated_with" and _touches_node_type(snapshot, edge, "market_indicator")
    ]
    dependency_edges = [
        edge
        for edge in context_edges
        if edge.edge_type in {"depends_on", "requires", "supplies", "produces", "routes_through", "participates_in"}
    ]
    likelihood = noisy_or(
        [
            _edge_pressure(policy_edges),
            _edge_pressure(event_edges),
            _edge_pressure(market_edges) * 0.75,
            _average_confidence(context_edges) * 0.35,
        ]
    )
    critical_dependency = critical_dependency_importance(snapshot, node.node_id)
    downstream_propagation = _edge_pressure(dependency_edges)
    resilience_integral_proxy = clamp01(0.35 + downstream_propagation * 0.45 + critical_dependency["critical_dependency_score"] * 0.20)
    demand_fulfillment_proxy = clamp01(downstream_propagation * 0.8 + critical_dependency["supply_demand_risk"] * 0.2)
    capacity_functionality_proxy = clamp01(critical_dependency["graph_importance"] * 0.7 + downstream_propagation * 0.3)
    impact = max(
        resilience_integral_proxy,
        demand_fulfillment_proxy,
        capacity_functionality_proxy,
        critical_dependency["strategic_importance"],
    )
    source_concentration = source_concentration_by_node(snapshot, node.node_id)
    country_concentration = country_concentration_by_input(snapshot, node.node_id)
    substitution = substitution_gap(snapshot, node.node_id)
    recovery_difficulty = clamp01(1.0 - _node_recovery_rate(node))
    policy_event_exposure = noisy_or([_edge_pressure(policy_edges), _edge_pressure(event_edges)])
    vulnerability_modifier = clamp01(
        0.75
        + max(float(source_concentration["hhi"]), float(country_concentration["hhi"])) * 0.35
        + float(substitution["substitution_gap"]) * 0.25
        + recovery_difficulty * 0.15
        + policy_event_exposure * 0.20
    )
    score = round(100.0 * likelihood * impact * vulnerability_modifier, 2)
    evidence_refs = _unique_refs([ref for edge in context_edges for ref in _edge_evidence(edge)])
    components = [
        _component("likelihood", likelihood, "Noisy-or combination of event, policy, market, and confidence proxies.", context_edges),
        _component("impact", impact, "Maximum of fixture proxy functionality loss, fulfillment loss, capacity loss, and critical dependency importance.", dependency_edges or context_edges),
        _component("vulnerability_modifier", vulnerability_modifier, "Concentration, substitution gap, recovery difficulty, and policy/event exposure proxy.", context_edges),
        _component("resilience_integral_loss_proxy", resilience_integral_proxy, "Fixture proxy for resilience triangle functionality loss.", dependency_edges),
        _component("demand_fulfillment_loss_proxy", demand_fulfillment_proxy, "Fixture proxy for demand fulfillment loss.", dependency_edges),
        _component("capacity_functionality_loss_proxy", capacity_functionality_proxy, "Fixture proxy for capacity/functionality loss.", dependency_edges),
        _component("source_concentration_hhi", float(source_concentration["hhi"]), "HHI source concentration on 0_to_1 scale.", context_edges),
        _component("substitution_gap", float(substitution["substitution_gap"]), "Dependency pressure not offset by substitute evidence.", context_edges),
    ]
    return {
        "score": score,
        "scoring_method": SCORING_METHOD,
        "formula_version": FORMULA_VERSION,
        "feature_version": FEATURE_VERSION,
        "likelihood": round(likelihood, 6),
        "impact": round(impact, 6),
        "vulnerability_modifier": round(vulnerability_modifier, 6),
        "components": components,
        "concentration": {
            "source_concentration": source_concentration,
            "country_concentration": country_concentration,
            "substitution": substitution,
            "critical_dependency": critical_dependency,
        },
        "formula_refs": FORMULA_REFS,
        "evidence_refs": evidence_refs,
        "calibration_status": CALIBRATION_STATUS,
        "warnings": [
            "fixture_graph:not_production_ready",
            "fixture_proxy_not_calibrated",
            "not_for_production_decision",
        ],
    }


def _component(name: str, value: float, explanation: str, edges: list[SemiriskEdge]) -> dict[str, Any]:
    return {
        "name": name,
        "value": round(clamp01(value) * 100.0, 2),
        "normalized_value": round(clamp01(value), 6),
        "status": "available" if edges or name in {"likelihood", "impact", "vulnerability_modifier"} else "unavailable",
        "weight": None,
        "weighted_contribution": None,
        "evidence_refs": _unique_refs([ref for edge in edges[:5] for ref in _edge_evidence(edge)]),
        "explanation": explanation,
    }


def _edge_pressure(edges: list[SemiriskEdge]) -> float:
    return noisy_or([edge.weight * edge.confidence for edge in edges])


def _average_confidence(edges: list[SemiriskEdge]) -> float:
    return bounded_mean([edge.confidence for edge in edges])


def _touches_node_type(snapshot: SemiriskGraphSnapshot, edge: SemiriskEdge, node_type: str) -> bool:
    node_by_id = {node.node_id: node for node in snapshot.nodes}
    return any(
        node_by_id.get(node_id) is not None and node_by_id[node_id].node_type == node_type
        for node_id in (edge.source_node_id, edge.target_node_id)
    )


def _node_recovery_rate(node: SemiriskNode) -> float:
    try:
        return clamp01(float(node.attributes.get("recovery_rate", 0.25)))
    except (TypeError, ValueError):
        return 0.25


def _edge_evidence(edge: SemiriskEdge) -> list[dict[str, Any]]:
    return [
        {
            "edge_id": edge.edge_id,
            "source_node_id": edge.source_node_id,
            "target_node_id": edge.target_node_id,
            "edge_type": edge.edge_type,
            "evidence_text_summary": edge.evidence_text_summary,
            "source_refs": [
                {
                    "source_id": ref.source_id,
                    "source_record_id": ref.source_record_id,
                    "raw_id": ref.raw_id,
                    "payload_hash": ref.payload_hash,
                    "provenance_url": ref.provenance_url,
                    "retrieved_at": ref.retrieved_at.isoformat(),
                    "as_of_time": ref.as_of_time.isoformat(),
                }
                for ref in edge.provenance_refs
            ],
        }
    ]


def _unique_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {}
    for ref in refs:
        by_key[(ref.get("edge_id"), ref.get("source_node_id"), ref.get("target_node_id"))] = ref
    return [by_key[key] for key in sorted(by_key)]
