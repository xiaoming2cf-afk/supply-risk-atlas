from __future__ import annotations

import json

import pytest

from sra_core.ingestion.connectors.errors import ConnectorUnavailableError
from sra_core.ingestion.connectors.gdelt_semiconductor_lite import (
    GDELT_SEMICONDUCTOR_QUERY_TERMS,
    GdeltSemiconductorLiteConnector,
)


def test_gdelt_lite_query_scope_is_narrow_and_semiconductor_specific() -> None:
    expected_terms = {
        "semiconductor",
        "chip supply chain",
        "lithography",
        "wafer fab",
        "photoresist",
        "export control",
        "earthquake semiconductor region",
    }

    assert set(GDELT_SEMICONDUCTOR_QUERY_TERMS) == expected_terms


def test_gdelt_lite_replays_fixture_without_article_body() -> None:
    records = GdeltSemiconductorLiteConnector().replay_fixture()

    assert len(records) == 1
    payload = records[0].model_dump(mode="json")
    rendered = json.dumps(payload)
    assert payload["source_id"] == "gdelt_semiconductor_events"
    assert len(payload["payload_hash"]) == 64
    assert payload["provenance_url"].startswith("https://")
    assert "raw_payload" not in payload
    assert "article_body" not in rendered.lower()


def test_gdelt_lite_promotes_risk_event_and_graph_evidence() -> None:
    promoted = GdeltSemiconductorLiteConnector().promote_fixture()

    assert promoted["raw_record_count"] == 1
    assert promoted["query_terms"] == list(GDELT_SEMICONDUCTOR_QUERY_TERMS)
    event = promoted["silver_events"][0]
    assert event["attributes"]["event_type_label"] == "earthquake semiconductor region"
    assert event["attributes"]["location"] == "Taiwan"
    assert event["attributes"]["evidence_url"].startswith("https://")
    edge_types = {edge["edge_type"] for edge in promoted["graph_edges"]}
    assert {"impacted_by", "evidence_for"} <= edge_types


def test_gdelt_lite_live_mode_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPPLY_RISK_GDELT_LIVE_ENABLED", raising=False)

    with pytest.raises(ConnectorUnavailableError):
        GdeltSemiconductorLiteConnector().fetch_live(request=object())  # type: ignore[arg-type]
