from __future__ import annotations

from typing import Any

from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.result import ConnectorFetchResult, ConnectorRecord, sanitize_external_text


class UsgsEarthquakeLiteConnector(PublicEvidenceConnector):
    def __init__(self, *, config: ConnectorConfig | None = None) -> None:
        super().__init__("usgs_earthquake_lite", config=config)

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        promoted: list[dict[str, Any]] = []
        for record in records:
            metadata = record.metadata
            promoted.append(
                {
                    "record_type": "natural_hazard_event",
                    "hazard_event_id": f"hazard_event:{record.source_record_id}",
                    "hazard_type": "earthquake",
                    "event_time": sanitize_external_text(metadata.get("event_time")),
                    "latitude": metadata.get("latitude"),
                    "longitude": metadata.get("longitude"),
                    "magnitude": metadata.get("magnitude"),
                    "depth_km": metadata.get("depth_km"),
                    "affected_region": sanitize_external_text(metadata.get("place")),
                    "source_refs": [f"{record.source_id}:{record.source_record_id}"],
                    "source_url": record.provenance_url,
                    "confidence": float(metadata.get("confidence", 0.7)),
                    "payload_hash": record.payload_hash,
                    "evidence_text_summary": record.payload_summary,
                    "warnings": ["hazard_context_not_warning_or_prediction_service"],
                }
            )
        return promoted

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="usgs_earthquake_lite_live_fetch_not_implemented",
            warnings=("live_polling_disabled_by_default", "fixture_mode_required_in_ci"),
        )


def replay_fixture(**kwargs: Any) -> ConnectorFetchResult:
    return UsgsEarthquakeLiteConnector(config=ConnectorConfig(mode="fixture", **kwargs)).fetch()

