from __future__ import annotations

from pathlib import Path

from sra_core.ingestion.connectors.base import ConnectorConfig
from sra_core.ingestion.connectors.sec_edgar_lite import SecEdgarLiteConnector


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "sec_edgar_lite_sample.json"


def test_sec_edgar_lite_fixture_replay_extracts_sanitized_disclosure_records() -> None:
    connector = SecEdgarLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=10)
    )

    result = connector.fetch()

    assert result.status == "ok"
    assert len(result.records) == 2
    public = result.to_public_dict()
    assert "raw_payload" not in str(public)
    assert "filing_body" not in str(public)
    assert "ignore previous instructions" not in str(public).lower()
    assert all(record.payload_hash for record in result.records)


def test_sec_edgar_lite_promotes_to_company_disclosure_events() -> None:
    connector = SecEdgarLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=10)
    )
    result = connector.fetch()

    promoted = connector.promote(result.records)

    assert {row["record_type"] for row in promoted} == {"company_disclosure_event"}
    assert promoted[0]["company_identifier"] == "company:tsmc"
    assert promoted[0]["filing_type"] == "20-F"
    assert promoted[0]["semiconductor_keyword_match"] is True
    assert promoted[0]["source_refs"] == ["sec_edgar_lite:sec-edgar-lite-tsmc-2025-20f"]
    assert promoted[0]["payload_hash"]
    assert "raw_payload" not in str(promoted)


def test_sec_edgar_lite_live_mode_is_controlled_unavailable_without_user_agent() -> None:
    connector = SecEdgarLiteConnector(config=ConnectorConfig(mode="live"))

    result = connector.fetch({"cik": "0001046179"})

    assert result.status == "unavailable"
    assert "sec_user_agent_required_for_live_edgar_fetch" in result.warnings

