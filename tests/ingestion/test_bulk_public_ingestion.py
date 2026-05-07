from __future__ import annotations

import json

from sra_core.ingestion.bulk_public import BulkLimits, build_bulk_catalog, write_promoted_catalog


def test_bulk_public_fixture_builds_data_governance_nodes(tmp_path) -> None:
    catalog, manifest = build_bulk_catalog(
        mode="fixture",
        cache_dir=tmp_path / "cache",
        limits=BulkLimits(
            sec_companies=20,
            gleif_legal_entities=10,
            world_bank_indicators=20,
            world_bank_countries=20,
            ourairports_airports=20,
            gdelt_articles=10,
            ofac_entries=10,
            usgs_earthquakes=5,
        ),
    )

    entity_types = {entity["entity_type"] for entity in catalog["entities"]}
    edge_types = {edge["edge_type"] for edge in catalog["edges"]}

    assert manifest["raw_data_in_git"] is False
    assert manifest["source_status"] == "fresh"
    assert len(catalog["entities"]) >= 240
    assert len(catalog["edges"]) >= 340
    assert {
        "schema_field",
        "license_policy",
        "coverage_area",
        "source_release",
        "observation_series",
        "legal_entity",
        "risk_event",
    } <= entity_types
    assert {
        "dataset_has_field",
        "licensed_under",
        "released_as",
        "observed_for",
        "dataset_observes",
        "event_affects",
        "risk_transmits_to",
    } <= edge_types
    assert any(entity["source_id"] == "usgs_earthquakes" for entity in catalog["entities"])


def test_bulk_public_writer_creates_promoted_manifest(tmp_path) -> None:
    promoted_dir = tmp_path / "promoted" / "public_real" / "latest"

    manifest = write_promoted_catalog(
        mode="fixture",
        cache_dir=tmp_path / "cache",
        promoted_dir=promoted_dir,
        limits=BulkLimits(sec_companies=12),
    )

    catalog_path = promoted_dir / "catalog.json"
    manifest_path = promoted_dir / "manifest.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["catalog_path"] == str(catalog_path)
    assert manifest["manifest_path"] == str(manifest_path)
    assert written_manifest["schema_version"] == "promoted-public-real-v1"
    assert written_manifest["record_counts"]["entities"] == len(catalog["entities"])
    assert written_manifest["record_counts"]["edges"] == len(catalog["edges"])
