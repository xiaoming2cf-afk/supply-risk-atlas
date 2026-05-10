from __future__ import annotations

from sra_core.ingestion.connectors.base_semiconductor import SemiconductorFixtureConnector


class WstsBillingsConnector(SemiconductorFixtureConnector):
    def __init__(self) -> None:
        super().__init__("wsts_historical_billings", "wsts_billings_sample.json")


def replay_fixture(**kwargs):
    return WstsBillingsConnector().replay(**kwargs)
