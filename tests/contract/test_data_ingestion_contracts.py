from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from sra_core.contracts.data import (
    GoldEdgeEvent,
    RawRecord,
    SilverEntity,
    SilverEvent,
    SourceManifest,
    SourceReference,
    SourceRegistry,
    payload_checksum,
)
from sra_core.ingestion.registry import load_source_registry


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "data_contracts" / "ingestion_schema"


@pytest.mark.parametrize(
    ("schema_name", "model"),
    [
        ("source_registry.json", SourceRegistry),
        ("raw_record.json", RawRecord),
        ("silver_entity.json", SilverEntity),
        ("silver_event.json", SilverEvent),
        ("gold_edge_event.json", GoldEdgeEvent),
        ("source_freshness_manifest.json", SourceManifest),
    ],
)
def test_static_json_schemas_exist_and_match_model_titles(schema_name, model) -> None:
    schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["title"] == model.model_json_schema()["title"]
    assert schema["additionalProperties"] is False


def test_default_source_registry_validates_license_policy() -> None:
    registry = load_source_registry()
    source_ids = {source.source_id for source in registry.sources}
    assert source_ids == {
        "sec_edgar",
        "gleif",
        "gdelt",
        "world_bank",
        "ofac",
        "ourairports",
        "nga_world_port_index",
        "usgs_earthquakes",
    }

    for source in registry.sources:
        assert source.public_no_key is True
        assert source.endpoints
        assert all(endpoint.auth == "none" for endpoint in source.endpoints)
        assert "research" in source.license.allowed_use
        assert source.freshness_sla_hours > 0
        if "commercial_risk_analysis" in source.license.allowed_use:
            assert source.license.commercial_use_allowed is True
        if "redistribution" in source.license.allowed_use:
            assert source.license.redistribution_allowed is True


def test_raw_record_checksum_is_deterministic_for_canonical_payload() -> None:
    event_time = datetime(2026, 1, 30, tzinfo=timezone.utc)
    ingest_time = datetime(2026, 1, 31, tzinfo=timezone.utc)
    payload_a = {"cik": "0000320193", "facts": {"form": "10-Q", "fy": 2026}}
    payload_b = {"facts": {"fy": 2026, "form": "10-Q"}, "cik": "0000320193"}

    record_a = RawRecord.from_payload(
        source_id="sec_edgar",
        source_record_id="0000320193-26-000010",
        event_time=event_time,
        ingest_time=ingest_time,
        payload_format="json",
        raw_payload=payload_a,
        license_name="SEC public data / fair access terms",
        allowed_use=["research", "commercial_risk_analysis"],
        attribution="U.S. Securities and Exchange Commission",
    )
    record_b = RawRecord.from_payload(
        source_id="sec_edgar",
        source_record_id="0000320193-26-000010",
        event_time=event_time,
        ingest_time=ingest_time,
        payload_format="json",
        raw_payload=payload_b,
        license_name="SEC public data / fair access terms",
        allowed_use=["research", "commercial_risk_analysis"],
        attribution="U.S. Securities and Exchange Commission",
    )

    assert record_a.checksum == record_b.checksum == payload_checksum(payload_a)
    assert record_a.raw_id == record_b.raw_id


def test_raw_record_rejects_observed_time_after_ingest_time() -> None:
    with pytest.raises(ValidationError):
        RawRecord.from_payload(
            source_id="sec_edgar",
            source_record_id="late-observed",
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            published_time=datetime(2026, 1, 2, tzinfo=timezone.utc),
            observed_time=datetime(2026, 1, 4, tzinfo=timezone.utc),
            ingest_time=datetime(2026, 1, 3, tzinfo=timezone.utc),
            payload_format="json",
            raw_payload={"ok": True},
            license_name="SEC public data / fair access terms",
            allowed_use=["research"],
        )


def test_raw_record_rejects_non_deterministic_checksum() -> None:
    with pytest.raises(ValidationError):
        RawRecord(
            raw_id="raw:sec_edgar:bad",
            source_id="sec_edgar",
            source_record_id="bad",
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            published_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            observed_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ingest_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            payload_format="json",
            raw_payload={"ok": True},
            checksum="0" * 64,
            license_name="SEC public data / fair access terms",
            allowed_use=["research"],
        )


def test_silver_and_gold_contracts_validate_source_lineage() -> None:
    ref = SourceReference(
        source_id="ofac",
        raw_id="raw:ofac:sdn:abc123",
        source_record_id="sdn:123",
    )
    entity = SilverEntity(
        entity_id="sanctioned_party:ofac:123",
        entity_type="sanctioned_party",
        display_name="Example Listed Entity",
        source_refs=[ref],
        country_code="US",
        confidence=0.95,
    )
    event = SilverEvent(
        event_id="event:ofac:sdn:123",
        event_type="sanctions_listing",
        source_refs=[ref],
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        published_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        observed_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ingest_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        confidence=0.9,
    )
    edge = GoldEdgeEvent(
        edge_event_id="edge_event:ofac:entity-country:123",
        source_entity_id=entity.entity_id,
        target_entity_id="country:US",
        edge_type="jurisdiction",
        event_type="create",
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        published_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        observed_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ingest_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        source_refs=[ref],
        evidence_event_ids=[event.event_id],
        confidence=0.85,
    )

    assert edge.source_refs[0].raw_id == ref.raw_id
