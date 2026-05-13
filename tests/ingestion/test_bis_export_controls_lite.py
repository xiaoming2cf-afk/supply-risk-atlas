from __future__ import annotations

from pathlib import Path

from sra_core.ingestion.connectors.base import ConnectorConfig
from sra_core.ingestion.connectors.bis_export_controls_lite import BisExportControlsLiteConnector


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "bis_export_controls_lite_sample.json"


def test_bis_export_controls_lite_promotes_policy_summary_only() -> None:
    connector = BisExportControlsLiteConnector(
        config=ConnectorConfig(mode="fixture", fixture_path=FIXTURE_PATH, max_records=5)
    )
    result = connector.fetch()

    promoted = connector.promote(result.records)
    rendered = str(promoted).lower()

    assert result.status == "ok"
    assert promoted[0]["record_type"] == "export_control_policy_event"
    assert promoted[0]["policy_type"] == "export_control"
    assert "advanced computing chips" in promoted[0]["affected_items"]
    assert "raw_payload" not in rendered
    assert "circumvent" not in rendered
    assert "avoid controls" not in rendered


def test_bis_export_controls_lite_live_mode_is_disabled() -> None:
    connector = BisExportControlsLiteConnector(config=ConnectorConfig(mode="live"))

    result = connector.fetch({"item": "advanced computing chips"})

    assert result.status == "unavailable"
    assert "bis_export_controls_lite_live_fetch_not_implemented" in result.warnings
