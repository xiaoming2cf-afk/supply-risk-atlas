from __future__ import annotations

from sra_core.ingestion.connectors.base_semiconductor import SemiconductorFixtureConnector


class GtaExportControlsConnector(SemiconductorFixtureConnector):
    def __init__(self) -> None:
        super().__init__(
            "global_trade_alert_semiconductor_export_controls",
            "gta_export_controls_sample.json",
        )


def replay_fixture(**kwargs):
    return GtaExportControlsConnector().replay(**kwargs)
