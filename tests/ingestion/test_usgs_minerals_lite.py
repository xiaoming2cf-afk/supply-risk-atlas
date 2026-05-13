from __future__ import annotations

from pathlib import Path

from sra_core.ingestion.connectors.base import ConnectorConfig
from sra_core.ingestion.connectors.usgs_minerals_lite import UsgsMineralsLiteConnector


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "usgs_minerals_lite_sample.json"


def test_usgs_minerals_lite_produces_raw_index_and_promoted_indicator() -> None:
    connector = UsgsMineralsLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=5)
    )
    result = connector.fetch()

    record = result.records[0].to_public_dict()
    promoted = connector.promote(result.records)
    rendered = str(promoted).lower()

    assert result.status == "ok"
    assert record["source_id"] == "usgs_mineral_commodity_summaries_lite"
    assert record["payload_hash"]
    assert record["provenance_url"].startswith("https://")
    assert record["payload_summary"]
    assert record["payload_stored"] is False
    assert promoted[0]["record_type"] == "mineral_supply_indicator"
    assert promoted[0]["mineral"] == "gallium"
    assert "raw_payload" not in rendered


def test_usgs_minerals_lite_live_mode_is_disabled() -> None:
    connector = UsgsMineralsLiteConnector(config=ConnectorConfig(mode="live"))

    result = connector.fetch({"mineral": "gallium"})

    assert result.status == "unavailable"
    assert "usgs_minerals_lite_live_fetch_not_implemented" in result.warnings
