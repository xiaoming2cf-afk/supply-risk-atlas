from __future__ import annotations

from typing import Any

from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.result import (
    ConnectorFetchResult,
    ConnectorRecord,
    sanitize_external_text,
)


ALLOWED_QUERY_HINTS = {
    "semiconductor",
    "chip supply chain",
    "lithography",
    "wafer fab",
    "photoresist",
    "export control",
    "earthquake semiconductor region",
    "power outage semiconductor",
    "hbm demand spike",
    "port disruption chip supply chain",
}


class GdeltSemiconductorLiteConnector(PublicEvidenceConnector):
    def __init__(self, *, config: ConnectorConfig | None = None) -> None:
        super().__init__("gdelt_semiconductor_lite", config=config)

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        promoted: list[dict[str, Any]] = []
        for record in records:
            metadata = record.metadata
            promoted.append(
                {
                    "record_type": "risk_event",
                    "event_id": f"risk_event:{record.source_record_id}",
                    "event_time": sanitize_external_text(metadata.get("event_time")),
                    "event_type": sanitize_external_text(metadata.get("event_type")),
                    "location": metadata.get("location") or {},
                    "affected_entities": [
                        sanitize_external_text(entity)
                        for entity in metadata.get("affected_entities", [])
                    ],
                    "evidence_url": record.provenance_url,
                    "source_name": sanitize_external_text(metadata.get("source_name") or "GDELT"),
                    "confidence": float(metadata.get("confidence", 0.55)),
                    "tone_or_severity_proxy": metadata.get("tone_or_severity_proxy"),
                    "payload_hash": record.payload_hash,
                    "source_refs": [f"{record.source_id}:{record.source_record_id}"],
                    "license_or_terms_ref": record.license_or_terms_ref,
                    "evidence_text_summary": record.payload_summary,
                }
            )
        return promoted

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        query = sanitize_external_text(params.get("query", "")).lower()
        if query and all(hint not in query for hint in ALLOWED_QUERY_HINTS):
            return ConnectorFetchResult.unavailable(
                source_id=self.source_id,
                mode="live",
                reason="query_scope_not_allowed",
                warnings=("narrow_semiconductor_query_required",),
            )
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="gdelt_semiconductor_lite_live_fetch_not_implemented",
            warnings=("live_fetch_disabled_by_default", "fixture_mode_required_in_ci"),
        )


def replay_fixture(**kwargs: Any) -> ConnectorFetchResult:
    config = ConnectorConfig(mode="fixture", **kwargs)
    return GdeltSemiconductorLiteConnector(config=config).fetch()
