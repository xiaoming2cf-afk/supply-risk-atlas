from __future__ import annotations

import json
import shutil
from pathlib import Path

from graph_kernel.promoted_pipeline import build_promoted_graph
from services.api.storage.sqlite_store import SQLiteStore


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "ingestion" / "fixtures"


def test_promoted_pipeline_writes_sanitized_artifacts(tmp_path: Path) -> None:
    result = build_promoted_graph(output_dir=tmp_path)

    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "graph_snapshot.json").exists()
    assert (tmp_path / "source_status.json").exists()
    assert result.manifest["graph_mode"] == "promoted"
    assert result.manifest["data_mode"] == "promoted_public_evidence_fixture"
    assert result.manifest["production_status"] == "not_production_ready"
    assert result.snapshot.graph_version == result.manifest["graph_version"]
    assert result.snapshot.source_manifest_id == result.manifest["source_manifest_id"]
    assert result.snapshot.missing_provenance_count == 0
    assert result.snapshot.unresolved_entity_count == 0
    rendered = json.dumps(json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8")))
    assert "raw_payload_body" not in rendered
    assert "raw_payload_json" not in rendered
    assert "article_body" not in rendered
    assert "filing_body" not in rendered


def test_promoted_pipeline_is_deterministic_for_same_inputs(tmp_path: Path) -> None:
    first = build_promoted_graph(output_dir=tmp_path / "first")
    second = build_promoted_graph(output_dir=tmp_path / "second")

    assert first.snapshot.graph_version == second.snapshot.graph_version
    assert first.snapshot.model_dump(mode="json") == second.snapshot.model_dump(mode="json")
    assert first.manifest["manifest_hash"] == second.manifest["manifest_hash"]


def test_promoted_graph_version_changes_when_input_changes(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixtures"
    shutil.copytree(FIXTURE_DIR, fixture_dir)
    baseline = build_promoted_graph(fixture_dir=fixture_dir)

    sec_fixture_path = fixture_dir / "sec_edgar_lite_sample.json"
    sec_fixture = json.loads(sec_fixture_path.read_text(encoding="utf-8"))
    sec_fixture["records"][0]["edges"][0]["weight"] = 0.41
    sec_fixture_path.write_text(json.dumps(sec_fixture, sort_keys=True), encoding="utf-8")
    changed = build_promoted_graph(fixture_dir=fixture_dir)

    assert baseline.snapshot.graph_version != changed.snapshot.graph_version


def test_promoted_pipeline_can_store_sanitized_snapshot_in_sqlite(tmp_path: Path) -> None:
    db_path = tmp_path / "promoted.db"
    result = build_promoted_graph(output_dir=tmp_path / "out", store_sqlite=True, sqlite_path=db_path)
    store = SQLiteStore(db_path)

    snapshot_row = store.fetch_one(
        "SELECT graph_version, source_manifest_id, node_count, edge_count FROM graph_snapshot WHERE graph_version = ?",
        (result.snapshot.graph_version,),
    )
    raw_rows = store.fetch_all("SELECT * FROM raw_record_index ORDER BY source_id, source_record_id")

    assert snapshot_row is not None
    assert snapshot_row["source_manifest_id"] == result.snapshot.source_manifest_id
    assert snapshot_row["node_count"] == result.snapshot.node_count
    assert snapshot_row["edge_count"] == result.snapshot.edge_count
    assert raw_rows
    assert all("raw_payload_body" not in json.dumps(row) for row in raw_rows)
    assert all("raw_payload_json" not in json.dumps(row) for row in raw_rows)
