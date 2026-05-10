from __future__ import annotations

from graph_kernel.lineage import lineage_for_edge, lineage_for_node
from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot


def test_lineage_for_node_returns_source_refs_and_metadata() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    lineage = lineage_for_node(snapshot, "company:tsmc")

    assert lineage["status"] == "success"
    assert lineage["graph_version"] == snapshot.graph_version
    assert lineage["source_manifest_id"] == snapshot.source_manifest_id
    assert lineage["node_id"] == "company:tsmc"
    assert lineage["source_refs"]
    assert lineage["incident_edge_ids"]


def test_lineage_for_edge_returns_source_refs_and_metadata() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    edge_id = "edge:tsmc:produces:advanced_logic"
    lineage = lineage_for_edge(snapshot, edge_id)

    assert lineage["status"] == "success"
    assert lineage["graph_version"] == snapshot.graph_version
    assert lineage["source_manifest_id"] == snapshot.source_manifest_id
    assert lineage["edge_id"] == edge_id
    assert lineage["source_refs"]
    assert lineage["source_node_id"] == "company:tsmc"
    assert lineage["target_node_id"] == "product_grade:advanced_logic"


def test_missing_lineage_ids_return_controlled_errors() -> None:
    snapshot = build_semiconductor_fixture_snapshot()

    node_lineage = lineage_for_node(snapshot, "company:missing")
    edge_lineage = lineage_for_edge(snapshot, "edge:missing")

    assert node_lineage["status"] == "error"
    assert "unknown node_id" in node_lineage["error"]
    assert edge_lineage["status"] == "error"
    assert "unknown edge_id" in edge_lineage["error"]
