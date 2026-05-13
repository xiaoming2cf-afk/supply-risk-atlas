from __future__ import annotations

from pathlib import Path

from sra_core.ingestion.connectors.base import ConnectorConfig
from sra_core.ingestion.connectors.gdelt_semiconductor_lite import (
    GdeltSemiconductorLiteConnector,
)


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "gdelt_semiconductor_lite_sample.json"


def test_gdelt_semiconductor_lite_fixture_replay_has_no_article_body() -> None:
    connector = GdeltSemiconductorLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=10)
    )

    result = connector.fetch()

    assert result.status == "ok"
    assert len(result.records) == 2
    public = result.to_public_dict()
    assert "raw_payload" not in str(public)
    assert "article_body" not in str(public)
    assert all(record.payload_summary for record in result.records)


def test_gdelt_semiconductor_lite_promotes_to_risk_events() -> None:
    connector = GdeltSemiconductorLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=10)
    )
    result = connector.fetch()

    promoted = connector.promote(result.records)

    assert {row["record_type"] for row in promoted} == {"risk_event"}
    assert promoted[0]["event_type"] == "policy_export_control"
    assert promoted[0]["affected_entities"] == ["company:asml", "product:euv_lithography"]
    assert promoted[0]["source_refs"] == ["gdelt_semiconductor_lite:gdelt-lite-2026-0001"]
    assert promoted[0]["payload_hash"]
    assert "article_body" not in str(promoted)


def test_gdelt_semiconductor_lite_live_mode_rejects_broad_queries_without_fetch() -> None:
    connector = GdeltSemiconductorLiteConnector(config=ConnectorConfig(mode="live"))

    result = connector.fetch({"query": "general business news"})

    assert result.status == "unavailable"
    assert "query_scope_not_allowed" in result.warnings
