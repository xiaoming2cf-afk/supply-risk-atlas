from __future__ import annotations

from typing import Any

from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.result import ConnectorFetchResult, ConnectorRecord, sanitize_external_text


class BisExportControlsLiteConnector(PublicEvidenceConnector):
    def __init__(self, *, config: ConnectorConfig | None = None) -> None:
        super().__init__("bis_export_controls_lite", config=config)

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        promoted: list[dict[str, Any]] = []
        for record in records:
            metadata = record.metadata
            promoted.append(
                {
                    "record_type": "export_control_policy_event",
                    "policy_event_id": f"export_control_policy:{record.source_record_id}",
                    "jurisdiction": sanitize_external_text(metadata.get("jurisdiction")),
                    "policy_type": sanitize_external_text(metadata.get("policy_type")),
                    "policy_title": sanitize_external_text(metadata.get("policy_title")),
                    "publication_date": sanitize_external_text(metadata.get("publication_date")),
                    "affected_items": [
                        sanitize_external_text(item) for item in metadata.get("affected_items", [])
                    ],
                    "compliance_summary": record.payload_summary,
                    "source_refs": [f"{record.source_id}:{record.source_record_id}"],
                    "source_url": record.provenance_url,
                    "confidence": float(metadata.get("confidence", 0.6)),
                    "payload_hash": record.payload_hash,
                    "warnings": ["export_control_summary_only_compliance_context"],
                }
            )
        return promoted

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="bis_export_controls_lite_live_fetch_not_implemented",
            warnings=("live_fetch_disabled_by_default", "fixture_mode_required_in_ci"),
        )


def replay_fixture(**kwargs: Any) -> ConnectorFetchResult:
    return BisExportControlsLiteConnector(config=ConnectorConfig(mode="fixture", **kwargs)).fetch()
