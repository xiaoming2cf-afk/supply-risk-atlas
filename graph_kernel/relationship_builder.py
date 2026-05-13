from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sra_core.geo.normalize import normalize_geo_id, sanitize_api_visible_text, sanitize_graph_edge


SUPPLY_EDGE_TYPES = {
    "supplies",
    "supplies_item",
    "provides_equipment",
    "provides_material",
    "provides_chemical",
    "provides_ip",
    "provides_service",
    "provides_capacity",
    "packaged_by",
    "tested_by",
    "manufactured_by",
    "produces",
    "participates_in",
}

DEMAND_EDGE_TYPES = {
    "demands",
    "demand_signal_for",
    "used_in_downstream_sector",
    "serves_downstream_sector",
    "demand_shock_on",
}

PRODUCTION_DEPENDENCY_EDGE_TYPES = {
    "requires",
    "depends_on",
    "uses_equipment",
    "uses_material",
    "uses_chemical",
    "uses_ip",
    "routes_through",
    "exposed_to_hazard",
    "restricted_by",
    "impacted_by",
    "located_in",
    "trade_dependency_edge",
    "logistics_route_edge",
    "hazard_exposure_edge",
    "policy_restriction_edge",
    "mineral_dependency_edge",
    "exports_to",
    "imports_from",
}

EVIDENCE_CONTEXT_EDGE_TYPES = {
    "evidence_context_link",
    "evidence_for",
    "correlated_with",
}

PROPAGATION_RELATIONSHIP_CLASSES = {"SUPPLY_RELATIONSHIP", "PRODUCTION_DEPENDENCY"}
DEMAND_RELATIONSHIP_CLASS = "DEMAND_RELATIONSHIP"
EVIDENCE_RELATIONSHIP_CLASS = "EVIDENCE_CONTEXT"
PRODUCTION_DEPENDENCY_CLASS = "PRODUCTION_DEPENDENCY"
SUPPLY_RELATIONSHIP_CLASS = "SUPPLY_RELATIONSHIP"
RELATIONSHIP_EDGE_GROUP_KEYS = (
    "supply_edges",
    "demand_edges",
    "production_dependency_edges",
    "evidence_context_links",
)

BLOCKED_ATTRIBUTE_PARTS = ("raw", "payload", "secret", "token", "private", "cookie", "authorization")


def classify_edge(edge_type: str) -> str:
    if edge_type in SUPPLY_EDGE_TYPES:
        return SUPPLY_RELATIONSHIP_CLASS
    if edge_type in DEMAND_EDGE_TYPES:
        return DEMAND_RELATIONSHIP_CLASS
    if edge_type in PRODUCTION_DEPENDENCY_EDGE_TYPES:
        return PRODUCTION_DEPENDENCY_CLASS
    return EVIDENCE_RELATIONSHIP_CLASS


def relationship_metadata(
    edge_type: str,
    *,
    source_node_id: str | None = None,
    target_node_id: str | None = None,
    attributes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    attributes = attributes or {}
    relationship_class = classify_edge(edge_type)
    metadata: dict[str, Any] = {
        "relationship_class": relationship_class,
        "not_supply_chain_dependency": relationship_class == EVIDENCE_RELATIONSHIP_CLASS,
    }
    if relationship_class == EVIDENCE_RELATIONSHIP_CLASS:
        metadata.update(
            {
                "derived_context": True,
                "user_facing_label": "evidence-context link",
                "warning": "This is not a supply-chain dependency edge.",
            }
        )
    if relationship_class == SUPPLY_RELATIONSHIP_CLASS:
        supplied_item_id = attributes.get("supplied_item_id") or target_node_id
        metadata.update(
            {
                "supplied_item_id": supplied_item_id,
                "service_or_capacity_item_id": attributes.get("service_or_capacity_item_id")
                or supplied_item_id,
                "relationship_scope": attributes.get("relationship_scope", "fixture_or_promoted_evidence"),
                "lead_time_days": attributes.get("lead_time_days"),
                "qualification_time_days": attributes.get("qualification_time_days"),
                "substitution_available": attributes.get("substitution_available"),
                "propagation_mode_hint": "physical_supply",
            }
        )
    if relationship_class == PRODUCTION_DEPENDENCY_CLASS:
        metadata.update(
            {
                "dependency_type": attributes.get("dependency_type", edge_type),
                "criticality": attributes.get("criticality", "medium"),
                "substitutability": attributes.get("substitutability", "unknown"),
                "bottleneck_flag": bool(
                    attributes.get(
                        "bottleneck_flag",
                        edge_type
                        in {
                            "requires",
                            "depends_on",
                            "uses_equipment",
                            "uses_material",
                            "uses_chemical",
                            "uses_ip",
                            "restricted_by",
                            "policy_restriction_edge",
                            "hazard_exposure_edge",
                            "mineral_dependency_edge",
                        },
                    )
                ),
                "propagation_mode_hint": attributes.get(
                    "propagation_mode_hint",
                    "physical_dependency",
                ),
            }
        )
    if relationship_class == DEMAND_RELATIONSHIP_CLASS:
        metadata.update(
            {
                "demand_proxy_type": attributes.get("demand_proxy_type", "fixture_public_evidence_proxy"),
                "demand_value": attributes.get("demand_value"),
                "demand_growth_proxy": attributes.get("demand_growth_proxy"),
                "region": normalize_geo_id(attributes.get("region"))
                if attributes.get("region") is not None
                else None,
                "period": attributes.get("period"),
                "propagation_mode_hint": "demand_shock_only",
            }
        )
    return metadata


def normalize_relationship_edge(edge: Mapping[str, Any]) -> dict[str, Any]:
    safe_edge = sanitize_graph_edge(edge)
    edge_type = str(edge.get("edge_type") or "")
    source_node_id = normalize_geo_id(edge.get("source_node_id"))
    target_node_id = normalize_geo_id(edge.get("target_node_id"))
    safe_attributes = _safe_attributes(edge.get("attributes") or {})
    attributes = {
        **safe_attributes,
        **relationship_metadata(
            edge_type,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            attributes=safe_attributes,
        ),
    }
    normalized = {
        **safe_edge,
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "relationship_class": attributes["relationship_class"],
        "source_refs": _normalize_source_refs(
            edge.get("source_refs") or edge.get("provenance_refs") or []
        ),
        "evidence_text_summary": sanitize_api_visible_text(edge.get("evidence_text_summary", "")),
        "attributes": attributes,
    }
    return normalized


def build_relationship_edge_groups(
    edges: Iterable[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {
        "supply_edges": [],
        "demand_edges": [],
        "production_dependency_edges": [],
        "evidence_context_links": [],
    }
    for edge in edges:
        normalized = normalize_relationship_edge(edge)
        relationship_class = normalized["attributes"]["relationship_class"]
        if relationship_class == SUPPLY_RELATIONSHIP_CLASS:
            groups["supply_edges"].append(normalized)
        elif relationship_class == DEMAND_RELATIONSHIP_CLASS:
            groups["demand_edges"].append(normalized)
        elif relationship_class == PRODUCTION_DEPENDENCY_CLASS:
            groups["production_dependency_edges"].append(normalized)
        else:
            groups["evidence_context_links"].append(normalized)
    return groups


def edge_allowed_for_physical_propagation(edge: Mapping[str, Any]) -> bool:
    normalized = normalize_relationship_edge(edge)
    attributes = normalized["attributes"]
    return (
        attributes["relationship_class"] in PROPAGATION_RELATIONSHIP_CLASSES
        and attributes.get("not_supply_chain_dependency") is not True
    )


def edge_allowed_for_demand_shock(edge: Mapping[str, Any]) -> bool:
    normalized = normalize_relationship_edge(edge)
    return normalized["attributes"]["relationship_class"] == DEMAND_RELATIONSHIP_CLASS


def _safe_attributes(attributes: Mapping[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, value in attributes.items():
        lowered = str(key).lower()
        if any(part in lowered for part in BLOCKED_ATTRIBUTE_PARTS):
            continue
        clean[str(key)] = value
    return clean


def _normalize_source_refs(refs: Any) -> list[dict[str, str]]:
    if isinstance(refs, str):
        refs = [refs]
    if isinstance(refs, Mapping):
        refs = [refs]
    if not isinstance(refs, Iterable):
        return []
    normalized: list[dict[str, str]] = []
    for ref in refs:
        if isinstance(ref, Mapping):
            source_id = sanitize_api_visible_text(ref.get("source_id", "unknown"))
            source_record_id = sanitize_api_visible_text(ref.get("source_record_id", "record"))
        else:
            text = sanitize_api_visible_text(ref)
            source_id, _, source_record_id = text.partition(":")
            source_record_id = source_record_id or "record"
        normalized.append(
            {
                "source_id": source_id or "unknown",
                "source_record_id": source_record_id or "record",
            }
        )
    return normalized
