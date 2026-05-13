from __future__ import annotations

from pathlib import Path

from sra_core.ingestion.connectors.base import ConnectorConfig
from sra_core.ingestion.connectors.un_comtrade_semiconductor_trade_lite import (
    UnComtradeSemiconductorTradeLiteConnector,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "un_comtrade_semiconductor_trade_lite_sample.json"
)


def test_un_comtrade_lite_fixture_replay_has_proxy_trade_metadata_only() -> None:
    connector = UnComtradeSemiconductorTradeLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=10)
    )

    result = connector.fetch()

    assert result.status == "ok"
    assert len(result.records) == 3
    assert "raw_payload" not in str(result.to_public_dict())
    assert all(record.payload_hash for record in result.records)


def test_un_comtrade_lite_promotion_computes_hhi_and_dependency_share() -> None:
    connector = UnComtradeSemiconductorTradeLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=10)
    )
    result = connector.fetch()

    promoted = connector.promote(result.records)
    taiwan_rows = [row for row in promoted if row["reporter"] == "TW"]

    assert {row["record_type"] for row in promoted} == {"trade_flow"}
    assert {row["commodity_code"] for row in promoted} >= {"370790", "848620"}
    assert taiwan_rows[0]["country_product_hhi"] == 0.58
    assert sorted(row["dependency_share"] for row in taiwan_rows) == [0.3, 0.7]
    assert any(row["significant_dependency"] for row in taiwan_rows)
    assert all("hs_code_mapping_is_proxy" in row["warnings"][0] for row in promoted)
    assert "raw_payload" not in str(promoted)


def test_un_comtrade_lite_live_mode_is_disabled() -> None:
    connector = UnComtradeSemiconductorTradeLiteConnector(config=ConnectorConfig(mode="live"))

    result = connector.fetch({"reporter": "TW", "commodity_code": "370790"})

    assert result.status == "unavailable"
    assert "un_comtrade_lite_live_fetch_not_implemented" in result.warnings

