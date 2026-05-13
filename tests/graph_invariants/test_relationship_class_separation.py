from __future__ import annotations

from graph_kernel.promoted_pipeline import build_promoted_graph_snapshot
from graph_kernel.relationship_builder import (
    EVIDENCE_RELATIONSHIP_CLASS,
    edge_allowed_for_demand_shock,
    edge_allowed_for_physical_propagation,
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
