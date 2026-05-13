from __future__ import annotations

from graph_kernel.promoted_pipeline import build_promoted_graph_snapshot
from graph_kernel.relationship_builder import (
    edge_allowed_for_demand_shock,
    edge_allowed_for_physical_propagation,
)
from graph_kernel.supply_demand_builder import (
    demand_relationship_rows,
    production_dependency_rows,
    supply_demand_balance_rows,
    supply_relationship_rows,
)


def _edge_payloads() -> list[dict[str, object]]:
    return build_promoted_graph_snapshot().model_dump(mode="json")["edges"]


def test_supply_relationships_have_supplier_direction_and_supplied_item() -> None:
    rows = supply_relationship_rows(_edge_payloads())

    assert rows
    asml_supply = [row for row in rows if row["supplier_id"] == "company:asml"]
    assert asml_supply
    assert asml_supply[0]["supplied_item_id"] == "equipment:euv_scanner"
    assert asml_supply[0]["relationship_class"] == "SUPPLY_RELATIONSHIP"
    assert asml_supply[0]["source_refs"]
    assert edge_allowed_for_physical_propagation(
        {
            "edge_type": "supplies",
            "source_node_id": "company:asml",
            "target_node_id": "equipment:euv_scanner",
        }
    )


def test_demand_relationships_have_demand_proxy_and_do_not_act_as_supply() -> None:
    rows = demand_relationship_rows(_edge_payloads())

    assert rows
    assert all(row["relationship_class"] == "DEMAND_RELATIONSHIP" for row in rows)
    assert all(row["demand_proxy_type"] for row in rows)
    assert any(row["product_grade_id"] == "product_grade:hbm" for row in rows)
    assert edge_allowed_for_demand_shock({"edge_type": "demands"})
    assert not edge_allowed_for_physical_propagation({"edge_type": "demands"})


def test_production_dependencies_have_bottleneck_and_substitution_metadata() -> None:
    rows = production_dependency_rows(_edge_payloads())

    assert rows
    requires_rows = [row for row in rows if row["dependency_type"] == "requires"]
    assert requires_rows
    assert all(row["criticality"] for row in requires_rows)
    assert all(row["substitutability"] for row in requires_rows)
    assert any(row["bottleneck_flag"] is True for row in rows)


def test_supply_demand_balance_rows_are_bounded_to_relationship_inputs() -> None:
    rows = supply_demand_balance_rows(_edge_payloads())

    assert rows
    hbm_rows = [row for row in rows if row["product_grade_id"] == "product_grade:hbm"]
    assert hbm_rows
    assert hbm_rows[0]["demand_edge_count"] >= 1
    assert hbm_rows[0]["shortage_proxy"] >= 0
