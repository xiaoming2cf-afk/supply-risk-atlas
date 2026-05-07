from __future__ import annotations

from sra_core.real_pipeline import run_public_real_pipeline
from sra_core.ingestion.registry import load_source_registry
from sra_core.ingestion.bulk_public import BulkLimits, write_promoted_catalog


def test_public_real_pipeline_end_to_end_is_default_ready() -> None:
    result = run_public_real_pipeline()

    assert result.real.sources
    assert result.real.source_manifest_ref.startswith("manifest_public_real_")
    assert {source.source_id for source in result.real.sources} >= {
        "sec_edgar",
        "gleif",
        "gdelt",
        "world_bank",
        "ofac",
        "ourairports",
        "nga_world_port_index",
        "usgs_earthquakes",
    }
    assert result.real.entities
    assert result.real.raw_records
    assert result.real.source_manifests
    assert result.real.silver_entities
    assert result.real.silver_events
    assert result.real.gold_edge_events
    assert result.edge_states
    assert result.snapshot.graph_version.startswith("g_")
    assert result.features
    assert result.predictions
    assert result.explanations


def test_public_real_node_catalog_expands_graph_volume() -> None:
    result = run_public_real_pipeline()
    entity_ids = {entity.canonical_id for entity in result.real.entities}
    edge_types = {edge.edge_type for edge in result.real.edge_events}
    entity_types = {entity.entity_type for entity in result.real.entities}

    assert len(result.real.entities) >= 140
    assert len(result.real.edge_events) >= 180
    assert result.snapshot.node_count == len(result.real.entities)
    assert result.snapshot.edge_count == len(result.edge_states)
    assert {"data_source", "data_category", "dataset", "indicator", "industry"} <= entity_types
    assert {
        "firm_apple",
        "firm_tsmc",
        "firm_nvidia",
        "firm_tesla",
        "port_singapore",
        "airport_taoyuan",
        "data_source_world_bank",
        "dataset_world_bank_indicators",
        "indicator_high_tech_exports",
        "industry_semiconductors",
        "product_ev_batteries",
        "risk_event_taiwan_strait_tension",
        "data_source_usgs_earthquakes",
        "dataset_usgs_m45_earthquakes_month",
        "risk_event_usgs_taiwan_m62",
    } <= entity_ids
    assert {
        "located_in",
        "produces",
        "buys_from",
        "ships_through",
        "route_connects",
        "policy_targets",
        "source_provides",
        "dataset_observes",
        "dataset_measures",
        "categorized_as",
        "classified_as",
        "indicator_context_for",
        "event_affects",
        "risk_transmits_to",
    } <= edge_types


def test_public_real_snapshot_is_deterministic_for_same_manifest() -> None:
    first = run_public_real_pipeline()
    second = run_public_real_pipeline()

    assert first.real.source_manifest_checksum == second.real.source_manifest_checksum
    assert first.snapshot.checksum == second.snapshot.checksum
    assert first.snapshot.graph_version == second.snapshot.graph_version


def test_public_real_edges_and_freshness_resolve_to_source_registry() -> None:
    result = run_public_real_pipeline()
    registry_by_source = {source.source_id: source for source in load_source_registry().sources}
    edge_sources = {event.source for event in result.real.edge_events}
    freshness_by_source = {item.source_id: item for item in result.real.freshness}

    assert edge_sources <= set(registry_by_source)
    assert {edge.edge_event_id for edge in result.real.gold_edge_events} == {
        event.edge_event_id for event in result.real.edge_events
    }
    for source_id, freshness in freshness_by_source.items():
        assert freshness.max_stale_minutes == registry_by_source[source_id].freshness_sla_hours * 60
        assert freshness.record_count >= 1


def test_public_real_pipeline_can_read_promoted_bulk_catalog(tmp_path, monkeypatch) -> None:
    promoted_dir = tmp_path / "promoted" / "public_real" / "latest"
    manifest = write_promoted_catalog(
        mode="fixture",
        cache_dir=tmp_path / "cache",
        promoted_dir=promoted_dir,
        limits=BulkLimits(sec_companies=20, world_bank_indicators=20, ourairports_airports=20),
    )
    monkeypatch.setenv("SUPPLY_RISK_REAL_CATALOG_PATH", manifest["catalog_path"])

    result = run_public_real_pipeline()
    entity_types = {entity.entity_type for entity in result.real.entities}
    edge_types = {edge.edge_type for edge in result.real.edge_events}

    assert len(result.real.entities) >= 240
    assert len(result.real.edge_events) >= 340
    assert {"schema_field", "license_policy", "source_release", "observation_series"} <= entity_types
    assert {"dataset_has_field", "licensed_under", "released_as", "observed_for"} <= edge_types
