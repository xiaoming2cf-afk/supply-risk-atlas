from __future__ import annotations

from pathlib import Path

from sra_core.ingestion.connectors.base import ConnectorConfig
from sra_core.ingestion.connectors.nga_world_port_index_lite import (
    NgaWorldPortIndexLiteConnector,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "nga_world_port_index_lite_sample.json"
)


def test_nga_world_port_index_lite_promotes_logistics_facility() -> None:
    connector = NgaWorldPortIndexLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=5)
    )
    result = connector.fetch()

    promoted = connector.promote(result.records)

    assert result.status == "ok"
    assert promoted[0]["record_type"] == "logistics_facility"
    assert promoted[0]["name"] == "Kaohsiung"
    assert promoted[0]["country_code"] == "CN"
    assert promoted[0]["payload_hash"]
    assert "navigational_decision_support" in promoted[0]["warnings"][0]


def test_nga_world_port_index_lite_live_mode_is_disabled() -> None:
    connector = NgaWorldPortIndexLiteConnector(config=ConnectorConfig(mode="live"))

    result = connector.fetch({"country": "CN"})

    assert result.status == "unavailable"
    assert "nga_world_port_index_lite_live_fetch_not_implemented" in result.warnings
