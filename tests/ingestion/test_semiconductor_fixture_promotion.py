from __future__ import annotations

import inspect

from sra_core.ingestion.connectors.eto_supply_chain import EtoSupplyChainConnector
from sra_core.ingestion.connectors.gdelt_semiconductor_events import GdeltSemiconductorEventsConnector
from sra_core.ingestion.connectors.gta_export_controls import GtaExportControlsConnector
from sra_core.ingestion.connectors.wsts_billings import WstsBillingsConnector
from sra_core.ingestion.semiconductor_promote import promote_semiconductor_fixtures


def test_fixture_connectors_are_deterministic_and_offline() -> None:
    connectors = [
        EtoSupplyChainConnector(),
        WstsBillingsConnector(),
        GtaExportControlsConnector(),
        GdeltSemiconductorEventsConnector(),
    ]
    for connector in connectors:
        first = [record.model_dump(mode="json") for record in connector.replay()]
        second = [record.model_dump(mode="json") for record in connector.replay()]
        assert first == second
        assert first
        source = inspect.getsource(type(connector))
        assert "requests" not in source
        assert "urlopen" not in source


def test_raw_record_summaries_include_required_lineage_fields() -> None:
    records = [
        record
        for connector in [
            EtoSupplyChainConnector(),
            WstsBillingsConnector(),
            GtaExportControlsConnector(),
            GdeltSemiconductorEventsConnector(),
        ]
        for record in connector.replay()
    ]

    for record in records:
        payload = record.model_dump(mode="json")
        assert payload["source_id"]
        assert payload["source_record_id"]
        assert payload["retrieved_at"]
        assert payload["as_of_time"]
        assert len(payload["payload_hash"]) == 64
        assert payload["provenance_url"].startswith("https://")
        assert "raw_payload" not in payload


def test_semiconductor_fixture_promotion_is_deterministic_and_lineaged() -> None:
    first = promote_semiconductor_fixtures()
    second = promote_semiconductor_fixtures()

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.source_manifest_id.startswith("semirisk_fixture_manifest_")
    assert first.raw_records
    assert first.silver_entities
    assert first.silver_events
    assert first.market_indicators
    assert first.graph_nodes
    assert first.graph_edges
    assert all(node.source_refs for node in first.graph_nodes)
    assert all(edge.provenance_refs for edge in first.graph_edges)
    assert all(entity.source_refs and entity.valid_from for entity in first.silver_entities)
    assert all(edge.valid_from and edge.valid_to is None for edge in first.graph_edges)
