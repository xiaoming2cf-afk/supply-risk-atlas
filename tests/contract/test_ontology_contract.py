from pathlib import Path

from sra_core.ontology import load_ontology


ROOT = Path(__file__).resolve().parents[2]


def test_ontology_references_are_valid() -> None:
    ontology = load_ontology(ROOT)
    assert ontology.validate() == []


def test_required_core_types_exist() -> None:
    ontology = load_ontology(ROOT)
    for node_type in ["firm", "port", "product", "country", "risk_event", "policy"]:
        assert node_type in ontology.node_types
    for edge_type in ["supplies_to", "ships_through", "event_affects", "risk_transmits_to"]:
        assert edge_type in ontology.edge_types
    for label in ["firm_risk_7d", "firm_risk_30d", "edge_disruption_30d"]:
        assert label in ontology.labels
