from __future__ import annotations

from pathlib import Path

from sra_core.ingestion.connectors.base import ConnectorConfig
from sra_core.ingestion.connectors.usgs_earthquake_lite import UsgsEarthquakeLiteConnector


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "usgs_earthquake_lite_sample.json"


def test_usgs_earthquake_lite_promotes_natural_hazard_event() -> None:
    connector = UsgsEarthquakeLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=5)
    )
    result = connector.fetch()

    promoted = connector.promote(result.records)

    assert result.status == "ok"
    assert promoted[0]["record_type"] == "natural_hazard_event"
    assert promoted[0]["hazard_type"] == "earthquake"
    assert promoted[0]["magnitude"] == 5.4
    assert promoted[0]["payload_hash"]
    assert "raw_payload" not in str(promoted)


def test_usgs_earthquake_lite_live_polling_is_disabled() -> None:
    connector = UsgsEarthquakeLiteConnector(config=ConnectorConfig(mode="live"))

    result = connector.fetch({"region": "TW"})

    assert result.status == "unavailable"
    assert "usgs_earthquake_lite_live_fetch_not_implemented" in result.warnings

