from __future__ import annotations

from sra_core.ingestion.connectors.base_semiconductor import SemiconductorFixtureConnector


class GdeltSemiconductorEventsConnector(SemiconductorFixtureConnector):
    def __init__(self) -> None:
        super().__init__("gdelt_semiconductor_events", "gdelt_semiconductor_events_sample.json")


def replay_fixture(**kwargs):
    return GdeltSemiconductorEventsConnector().replay(**kwargs)
