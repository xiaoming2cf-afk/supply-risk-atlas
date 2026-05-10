from __future__ import annotations

from sra_core.ingestion.connectors.base_semiconductor import SemiconductorFixtureConnector


class EtoSupplyChainConnector(SemiconductorFixtureConnector):
    def __init__(self) -> None:
        super().__init__(
            "eto_cset_advanced_semiconductor_supply_chain",
            "eto_supply_chain_sample.json",
        )


def replay_fixture(**kwargs):
    return EtoSupplyChainConnector().replay(**kwargs)
