from __future__ import annotations

from graph_kernel.promoted_pipeline import build_promoted_artifacts, build_promoted_graph_snapshot


def test_promoted_pipeline_builds_deterministic_snapshot() -> None:
    first = build_promoted_graph_snapshot()
    second = build_promoted_graph_snapshot()

    assert first.graph_version == second.graph_version
    assert first.source_manifest_id == second.source_manifest_id
    assert first.data_mode == "public_evidence_promoted"
    assert first.graph_mode == "promoted"
    assert first.node_count >= 20
    assert first.edge_count >= 30
    assert first.quality_report["status"] == "pass"


def test_promoted_pipeline_writes_expected_artifacts(tmp_path) -> None:
    artifacts = build_promoted_artifacts(output_dir=tmp_path)

    for filename in [
        "manifest.json",
        "graph_snapshot.json",
        "source_status.json",
        "quality_report.json",
        "source_coverage.json",
        "entity_resolution_report.json",
    ]:
        assert (tmp_path / filename).exists()

    assert artifacts["manifest"]["data_mode"] == "public_evidence_promoted"
    assert artifacts["manifest"]["graph_mode"] == "promoted"
    assert artifacts["graph_snapshot"]["graph_version"] == artifacts["manifest"]["graph_version"]

