from __future__ import annotations

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot


def test_semiconductor_fixture_snapshot_is_deterministic() -> None:
    first = build_semiconductor_fixture_snapshot(as_of_time="2026-05-01T00:00:00Z")
    second = build_semiconductor_fixture_snapshot(as_of_time="2026-05-01T00:00:00Z")

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.graph_version == second.graph_version
    assert first.source_manifest_id == second.source_manifest_id


def test_semiconductor_fixture_snapshot_has_required_size_and_quality_counts() -> None:
    snapshot = build_semiconductor_fixture_snapshot()

    assert snapshot.graph_version.startswith("semirisk_kg_v0_1_20260501T000000Z_")
    assert snapshot.source_manifest_id.startswith("semirisk_fixture_manifest_")
    assert snapshot.node_count >= 20
    assert snapshot.edge_count >= 30
    assert snapshot.node_count_by_type["company"] >= 5
    assert snapshot.edge_count_by_type["requires"] >= 1
    assert snapshot.missing_provenance_count == 0
    assert snapshot.unresolved_entity_count == 0
    assert snapshot.stale_source_count >= 0
    assert "status" in snapshot.quality_report


def test_every_semiconductor_node_and_edge_has_provenance() -> None:
    snapshot = build_semiconductor_fixture_snapshot()

    assert all(node.source_refs for node in snapshot.nodes)
    assert all(edge.provenance_refs for edge in snapshot.edges)
    assert all(ref.provenance_url.startswith("https://") for node in snapshot.nodes for ref in node.source_refs)
    assert all(
        ref.provenance_url.startswith("https://")
        for edge in snapshot.edges
        for ref in edge.provenance_refs
    )
