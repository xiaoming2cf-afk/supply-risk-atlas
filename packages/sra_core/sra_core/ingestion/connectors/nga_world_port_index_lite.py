from __future__ import annotations

from typing import Any

from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.result import ConnectorFetchResult, ConnectorRecord, sanitize_external_text


class NgaWorldPortIndexLiteConnector(PublicEvidenceConnector):
    def __init__(self, *, config: ConnectorConfig | None = None) -> None:
        super().__init__("nga_world_port_index_lite", config=config)

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        promoted: list[dict[str, Any]] = []
        for record in records:
            metadata = record.metadata
            promoted.append(
                {
                    "record_type": "logistics_facility",
                    "logistics_node_id": f"logistics_node:{record.source_record_id}",
                    "node_type": "port",
                    "name": sanitize_external_text(metadata.get("port_name")),
                    "country_code": sanitize_external_text(metadata.get("country_code")),
                    "latitude": metadata.get("latitude"),
                    "longitude": metadata.get("longitude"),
                    "facilities_summary": record.payload_summary,
                    "port_characteristics": sanitize_external_text(
                        metadata.get("port_characteristics")
                    ),
                    "source_refs": [f"{record.source_id}:{record.source_record_id}"],
                    "source_url": record.provenance_url,
                    "confidence": float(metadata.get("confidence", 0.6)),
                    "payload_hash": record.payload_hash,
                    "warnings": ["logistics_context_not_navigational_decision_support"],
                }
            )
        return promoted

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="nga_world_port_index_lite_live_fetch_not_implemented",
            warnings=("live_fetch_disabled_by_default", "fixture_mode_required_in_ci"),
        )


def replay_fixture(**kwargs: Any) -> ConnectorFetchResult:
    return NgaWorldPortIndexLiteConnector(config=ConnectorConfig(mode="fixture", **kwargs)).fetch()

