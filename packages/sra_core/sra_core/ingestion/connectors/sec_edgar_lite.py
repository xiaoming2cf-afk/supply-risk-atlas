from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from sra_core.contracts.semiconductor import SemiconductorRawRecord
from sra_core.ingestion.connectors.base import ConnectorRequest, PublicEvidenceConnector
from sra_core.ingestion.connectors.base_semiconductor import default_fixture_dir, source_terms_ref
from sra_core.ingestion.connectors.errors import ConnectorPolicyError, ConnectorUnavailableError


SEC_EDGAR_LITE_REQUIRED_FIELDS = {
    "company_identifier",
    "filing_date",
    "disclosure_type",
    "risk_factor_summary",
    "supply_chain_keywords",
    "source_url",
    "confidence",
}


class SecEdgarLiteConnector(PublicEvidenceConnector):
    def __init__(self) -> None:
        super().__init__("sec_edgar")

    def load_fixture(self, fixture_dir: str | Path | None = None) -> dict[str, Any]:
        base = Path(fixture_dir) if fixture_dir else default_fixture_dir()
        payload = json.loads((base / "sec_edgar_lite_sample.json").read_text(encoding="utf-8"))
        if payload.get("source_id") != self.source_id:
            raise ConnectorPolicyError("SEC EDGAR lite fixture source_id mismatch")
        return payload

    def replay_fixture(
        self,
        *,
        fixture_dir: str | Path | None = None,
        registry_path: str | Path | None = None,
    ) -> list[SemiconductorRawRecord]:
        fixture = self.load_fixture(fixture_dir)
        terms_ref = source_terms_ref(self.source_id, registry_path)
        return [
            SemiconductorRawRecord.from_fixture(
                source_id="sec_edgar",
                row=row,
                license_or_terms_ref=terms_ref,
            )
            for row in fixture.get("records", [])
        ]

    def promote_fixture(self, **kwargs: Any) -> dict[str, Any]:
        records = self.replay_fixture(**kwargs)
        events = [event for record in records for event in record.payload.get("events", [])]
        entities = [node for record in records for node in record.payload.get("entities", [])]
        edges = [edge for record in records for edge in record.payload.get("edges", [])]
        for record in records:
            missing = SEC_EDGAR_LITE_REQUIRED_FIELDS - set(record.payload)
            if missing:
                raise ConnectorPolicyError(
                    f"SEC EDGAR lite fixture record missing required fields: {sorted(missing)}"
                )
        return {
            "source_id": self.source_id,
            "raw_record_count": len(records),
            "raw_records": [record.model_dump(mode="json") for record in records],
            "silver_events": events,
            "graph_nodes": entities,
            "graph_edges": edges,
            "warnings": ["sec_edgar_lite:fixture_mode", "raw_filing_body_excluded"],
        }

    def fetch_live(self, request: ConnectorRequest):
        if os.getenv("SUPPLY_RISK_SEC_EDGAR_LIVE_ENABLED") != "1":
            raise ConnectorUnavailableError("SEC EDGAR lite live mode is disabled by default.")
        if not os.getenv("SUPPLY_RISK_SEC_EDGAR_USER_AGENT"):
            raise ConnectorPolicyError("SEC EDGAR live mode requires SUPPLY_RISK_SEC_EDGAR_USER_AGENT.")
        raise ConnectorUnavailableError("SEC EDGAR lite live fetch is not implemented in this phase.")


def replay_fixture(**kwargs: Any) -> list[SemiconductorRawRecord]:
    return SecEdgarLiteConnector().replay_fixture(**kwargs)
