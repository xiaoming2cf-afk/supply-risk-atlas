from __future__ import annotations

from graph_kernel.promoted_pipeline import build_promoted_graph_snapshot
from graph_kernel.relationship_builder import (
    EVIDENCE_RELATIONSHIP_CLASS,
    edge_allowed_for_demand_shock,
    edge_allowed_for_physical_propagation,
    normalize_relationship_edge,
)


def test_promoted_graph_keeps_relationship_edge_groups_separate() -> None:
    payload = build_promoted_graph_snapshot().model_dump(mode="json")
    groups = payload["relationship_edge_groups"]

    assert set(groups) == {
        "supply_edges",
        "demand_edges",
        "production_dependency_edges",
        "evidence_context_links",
    }
    edge_ids_by_group = {
        group_name: {edge["edge_id"] for edge in edges}
        for group_name, edges in groups.items()
    }

    assert edge_ids_by_group["supply_edges"].isdisjoint(edge_ids_by_group["demand_edges"])
    assert edge_ids_by_group["supply_edges"].isdisjoint(
        edge_ids_by_group["production_dependency_edges"]
    )
    assert edge_ids_by_group["evidence_context_links"].isdisjoint(
        edge_ids_by_group["production_dependency_edges"]
    )


def test_evidence_context_links_cannot_be_used_for_propagation() -> None:
    groups = build_promoted_graph_snapshot().model_dump(mode="json")["relationship_edge_groups"]

    assert groups["evidence_context_links"]
    for edge in groups["evidence_context_links"]:
        assert edge["relationship_class"] == EVIDENCE_RELATIONSHIP_CLASS
        assert edge["attributes"]["not_supply_chain_dependency"] is True
        assert edge["attributes"]["user_facing_label"] == "evidence-context link"
        assert edge["attributes"]["warning"] == "This is not a supply-chain dependency edge."
        assert not edge_allowed_for_physical_propagation(edge)
        assert not edge_allowed_for_demand_shock(edge)


def test_not_supply_chain_dependency_overrides_depends_on_edge_type() -> None:
    edge = {
        "edge_id": "edge:context-not-dependency",
        "source_node_id": "evidence:public-context",
        "target_node_id": "vc_wafer_fabrication",
        "edge_type": "depends_on",
        "attributes": {"not_supply_chain_dependency": True},
    }

    normalized = normalize_relationship_edge(edge)

    assert normalized["relationship_class"] == EVIDENCE_RELATIONSHIP_CLASS
    assert normalized["attributes"]["not_supply_chain_dependency"] is True
    assert normalized["attributes"]["derived_context"] is True
    assert "dependency_type" not in normalized["attributes"]
    assert not edge_allowed_for_physical_propagation(edge)
    assert not edge_allowed_for_demand_shock(edge)


def test_explicit_evidence_context_overrides_depends_on_edge_type() -> None:
    edge = {
        "edge_id": "edge:explicit-evidence-context",
        "source_node_id": "evidence:public-context",
        "target_node_id": "vc_advanced_packaging",
        "edge_type": "depends_on",
        "attributes": {"relationship_class": EVIDENCE_RELATIONSHIP_CLASS},
    }

    normalized = normalize_relationship_edge(edge)

    assert normalized["relationship_class"] == EVIDENCE_RELATIONSHIP_CLASS
    assert normalized["attributes"]["not_supply_chain_dependency"] is True
    assert normalized["attributes"]["user_facing_label"] == "evidence-context link"
    assert "dependency_type" not in normalized["attributes"]
    assert not edge_allowed_for_physical_propagation(edge)
    assert not edge_allowed_for_demand_shock(edge)


def test_demand_and_supply_relationships_do_not_share_operational_roles() -> None:
    groups = build_promoted_graph_snapshot().model_dump(mode="json")["relationship_edge_groups"]

    assert groups["supply_edges"]
    assert groups["demand_edges"]
    for edge in groups["supply_edges"]:
        assert edge["relationship_class"] == "SUPPLY_RELATIONSHIP"
        assert "supplied_item_id" in edge["attributes"]
        assert edge_allowed_for_physical_propagation(edge)
        assert not edge_allowed_for_demand_shock(edge)
    for edge in groups["demand_edges"]:
        assert edge["relationship_class"] == "DEMAND_RELATIONSHIP"
        assert "demand_proxy_type" in edge["attributes"]
        assert edge_allowed_for_demand_shock(edge)
        assert not edge_allowed_for_physical_propagation(edge)
