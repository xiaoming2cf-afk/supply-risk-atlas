from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from graph_kernel.relationship_builder import build_relationship_edge_groups


def supply_relationship_rows(edges: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups = build_relationship_edge_groups(edges)
    return [
        {
            **_relationship_row_common(edge),
            "relationship_class": "SUPPLY_RELATIONSHIP",
            "edge_id": edge["edge_id"],
            "edge_type": edge["edge_type"],
            "source_node_id": edge["source_node_id"],
            "target_node_id": edge["target_node_id"],
            "supplier_id": edge["source_node_id"],
            "supplied_item_id": edge["attributes"]["supplied_item_id"],
            "buyer_or_stage_id": edge["target_node_id"],
            "supplied_item_type": edge["edge_type"],
            "relationship_scope": edge["attributes"]["relationship_scope"],
            "share_or_capacity_proxy": edge["attributes"].get("share_or_capacity_proxy"),
            "lead_time_days": edge["attributes"].get("lead_time_days"),
            "qualification_time_days": edge["attributes"].get("qualification_time_days"),
            "substitution_available": edge["attributes"].get("substitution_available"),
        }
        for edge in groups["supply_edges"]
    ]


def demand_relationship_rows(edges: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups = build_relationship_edge_groups(edges)
    return [
        {
            **_relationship_row_common(edge),
            "relationship_class": "DEMAND_RELATIONSHIP",
            "edge_id": edge["edge_id"],
            "edge_type": edge["edge_type"],
            "source_node_id": edge["source_node_id"],
            "target_node_id": edge["target_node_id"],
            "demand_source_id": edge["source_node_id"],
            "product_grade_id": edge["target_node_id"],
            "region": edge["attributes"].get("region"),
            "period": edge["attributes"].get("period"),
            "demand_proxy_type": edge["attributes"]["demand_proxy_type"],
            "demand_value": edge["attributes"].get("demand_value"),
            "demand_growth_proxy": edge["attributes"].get("demand_growth_proxy"),
        }
        for edge in groups["demand_edges"]
    ]


def production_dependency_rows(edges: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups = build_relationship_edge_groups(edges)
    return [
        {
            **_relationship_row_common(edge),
            "relationship_class": "PRODUCTION_DEPENDENCY",
            "edge_id": edge["edge_id"],
            "edge_type": edge["edge_type"],
            "source_node_id": edge["source_node_id"],
            "target_node_id": edge["target_node_id"],
            "dependency_source_id": edge["source_node_id"],
            "dependency_target_id": edge["target_node_id"],
            "dependency_type": edge["attributes"]["dependency_type"],
            "criticality": edge["attributes"]["criticality"],
            "substitutability": edge["attributes"]["substitutability"],
            "bottleneck_flag": edge["attributes"]["bottleneck_flag"],
            "propagation_mode_hint": edge["attributes"]["propagation_mode_hint"],
        }
        for edge in groups["production_dependency_edges"]
    ]


def evidence_context_rows(edges: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups = build_relationship_edge_groups(edges)
    return [
        {
            **_relationship_row_common(edge),
            "relationship_class": "EVIDENCE_CONTEXT",
            "edge_id": edge["edge_id"],
            "source_node_id": edge["source_node_id"],
            "target_node_id": edge["target_node_id"],
            "edge_type": edge["edge_type"],
            "derived_context": edge["attributes"]["derived_context"],
            "not_supply_chain_dependency": edge["attributes"]["not_supply_chain_dependency"],
            "user_facing_label": edge["attributes"]["user_facing_label"],
            "warning": edge["attributes"]["warning"],
        }
        for edge in groups["evidence_context_links"]
    ]


def supply_demand_balance_rows(edges: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups = build_relationship_edge_groups(edges)
    demand_by_target: dict[str, int] = {}
    supply_by_target: dict[str, int] = {}
    dependency_by_source: dict[str, int] = {}

    for edge in groups["demand_edges"]:
        demand_by_target[edge["target_node_id"]] = demand_by_target.get(edge["target_node_id"], 0) + 1
    for edge in groups["supply_edges"]:
        supply_by_target[edge["target_node_id"]] = supply_by_target.get(edge["target_node_id"], 0) + 1
    for edge in groups["production_dependency_edges"]:
        dependency_by_source[edge["source_node_id"]] = dependency_by_source.get(edge["source_node_id"], 0) + 1

    product_ids = sorted(set(demand_by_target) | set(supply_by_target) | set(dependency_by_source))
    return [
        {
            "product_grade_id": product_id,
            "relationship_class": "SUPPLY_DEMAND_BALANCE",
            "demand_edge_count": demand_by_target.get(product_id, 0),
            "supply_edge_count": supply_by_target.get(product_id, 0),
            "production_dependency_count": dependency_by_source.get(product_id, 0),
            "shortage_proxy": max(0, demand_by_target.get(product_id, 0) - supply_by_target.get(product_id, 0)),
        }
        for product_id in product_ids
    ]


def _relationship_row_common(edge: Mapping[str, Any]) -> dict[str, Any]:
    source_refs = edge["source_refs"]
    return {
        "source_refs": source_refs,
        "evidence_refs": source_refs,
        "confidence": edge["confidence"],
        "valid_from": edge.get("valid_from"),
        "valid_to": edge.get("valid_to"),
        "warnings": [],
        "calibration_status": "fixture_or_promoted_calibration_not_validated",
    }
