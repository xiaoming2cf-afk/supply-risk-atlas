from __future__ import annotations

from typing import Any

from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.result import ConnectorFetchResult, ConnectorRecord, sanitize_external_text


class UsgsMineralsLiteConnector(PublicEvidenceConnector):
    def __init__(self, *, config: ConnectorConfig | None = None) -> None:
        super().__init__("usgs_mineral_commodity_summaries_lite", config=config)

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        promoted: list[dict[str, Any]] = []
        for record in records:
            metadata = record.metadata
            promoted.append(
                {
                    "record_type": "mineral_supply_indicator",
                    "indicator_id": f"mineral_supply:{record.source_record_id}",
                    "mineral": sanitize_external_text(metadata.get("mineral")),
                    "country": sanitize_external_text(metadata.get("country")),
                    "period": sanitize_external_text(metadata.get("period")),
                    "production_summary": record.payload_summary,
                    "import_reliance_proxy": metadata.get("import_reliance_proxy"),
                    "source_refs": [f"{record.source_id}:{record.source_record_id}"],
                    "source_url": record.provenance_url,
                    "confidence": float(metadata.get("confidence", 0.6)),
                    "payload_hash": record.payload_hash,
                    "evidence_text_summary": record.payload_summary,
                    "warnings": ["mineral_statistics_are_public_proxy_indicators"],
                }
            )
        return promoted

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="usgs_minerals_lite_live_fetch_not_implemented",
            warnings=("live_fetch_disabled_by_default", "fixture_mode_required_in_ci"),
        )


def replay_fixture(**kwargs: Any) -> ConnectorFetchResult:
    return UsgsMineralsLiteConnector(config=ConnectorConfig(mode="fixture", **kwargs)).fetch()
