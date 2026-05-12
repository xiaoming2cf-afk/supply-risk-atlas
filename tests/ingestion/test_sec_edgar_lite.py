from __future__ import annotations

import json

import pytest

from sra_core.ingestion.connectors.errors import ConnectorPolicyError, ConnectorUnavailableError
from sra_core.ingestion.connectors.sec_edgar_lite import SecEdgarLiteConnector


def test_sec_edgar_lite_replays_fixture_without_raw_body() -> None:
    records = SecEdgarLiteConnector().replay_fixture()

    assert len(records) == 1
    payload = records[0].model_dump(mode="json")
    rendered = json.dumps(payload)
    assert payload["source_id"] == "sec_edgar"
    assert len(payload["payload_hash"]) == 64
    assert payload["license_or_terms_ref"].startswith("https://www.sec.gov/")
    assert "raw_payload" not in payload
    assert "filing_body" not in rendered.lower()


def test_sec_edgar_lite_promotes_disclosure_event_and_evidence_edges() -> None:
    promoted = SecEdgarLiteConnector().promote_fixture()

    assert promoted["source_id"] == "sec_edgar"
    assert promoted["raw_record_count"] == 1
    assert promoted["raw_records"][0]["source_id"] == "sec_edgar"
    event = promoted["silver_events"][0]
    assert event["attributes"]["company_identifier"] == "CIK0000320193"
    assert event["attributes"]["filing_date"] == "2026-01-30"
    assert event["attributes"]["disclosure_type"] == "10-Q risk factors"
    assert "semiconductor" in event["attributes"]["supply_chain_keywords"]
    assert event["attributes"]["source_url"].startswith("https://www.sec.gov/")
    assert all(edge["edge_type"] == "evidence_for" for edge in promoted["graph_edges"])


def test_sec_edgar_lite_live_mode_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPPLY_RISK_SEC_EDGAR_LIVE_ENABLED", raising=False)
    connector = SecEdgarLiteConnector()

    with pytest.raises(ConnectorUnavailableError):
        connector.fetch_live(
            request=object()  # type: ignore[arg-type]
        )


def test_sec_edgar_lite_live_mode_requires_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_SEC_EDGAR_LIVE_ENABLED", "1")
    monkeypatch.delenv("SUPPLY_RISK_SEC_EDGAR_USER_AGENT", raising=False)

    with pytest.raises(ConnectorPolicyError):
        SecEdgarLiteConnector().fetch_live(request=object())  # type: ignore[arg-type]
