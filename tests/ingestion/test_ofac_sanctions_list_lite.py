from __future__ import annotations

from pathlib import Path

from sra_core.ingestion.connectors.base import ConnectorConfig
from sra_core.ingestion.connectors.ofac_sanctions_list_lite import OfacSanctionsListLiteConnector


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "ofac_sanctions_list_lite_sample.json"


def test_ofac_sanctions_list_lite_promotes_compliance_risk_summary_only() -> None:
    connector = OfacSanctionsListLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=5)
    )
    result = connector.fetch()

    promoted = connector.promote(result.records)
    rendered = str(promoted).lower()

    assert result.status == "ok"
    assert promoted[0]["record_type"] == "sanctions_screening_event"
    assert promoted[0]["list_type"] == "SDN"
    assert "compliance-risk awareness" in promoted[0]["evidence_text_summary"].lower()
    assert "raw_payload" not in rendered
    assert "reroute" not in rendered
    assert "avoid sanctions" not in rendered


def test_ofac_sanctions_list_lite_live_mode_is_disabled() -> None:
    connector = OfacSanctionsListLiteConnector(config=ConnectorConfig(mode="live"))

    result = connector.fetch({"name": "Example"})

    assert result.status == "unavailable"
    assert "ofac_sanctions_list_lite_live_fetch_not_implemented" in result.warnings
