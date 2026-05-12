from __future__ import annotations

from pathlib import Path

from sra_core.ingestion.connectors.base import ConnectorConfig
from sra_core.ingestion.connectors.wits_trade_tariff_lite import WitsTradeTariffLiteConnector


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "wits_trade_tariff_lite_sample.json"


def test_wits_lite_fixture_replay_has_indicator_metadata_only() -> None:
    connector = WitsTradeTariffLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=10)
    )

    result = connector.fetch()

    assert result.status == "ok"
    assert len(result.records) == 2
    assert "raw_payload" not in str(result.to_public_dict())
    assert all(record.payload_hash for record in result.records)


def test_wits_lite_promotes_to_trade_tariff_indicators() -> None:
    connector = WitsTradeTariffLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=10)
    )
    result = connector.fetch()

    promoted = connector.promote(result.records)

    assert {row["record_type"] for row in promoted} == {"trade_tariff_indicator"}
    assert promoted[0]["indicator_type"] == "applied_tariff_proxy"
    assert promoted[1]["unit"] == "hhi"
    assert promoted[1]["value"] == 0.48
    assert all(row["payload_hash"] for row in promoted)
    assert "raw_payload" not in str(promoted)


def test_wits_lite_live_mode_is_disabled() -> None:
    connector = WitsTradeTariffLiteConnector(config=ConnectorConfig(mode="live"))

    result = connector.fetch({"country": "TW", "commodity_group": "370790"})

    assert result.status == "unavailable"
    assert "wits_trade_tariff_lite_live_fetch_not_implemented" in result.warnings
