from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
EDGE_PATH = ROOT / "configs" / "ontology" / "semiconductor_edge_catalog.yaml"

REQUIRED_EDGE_TYPES = {
    "located_in", "participates_in", "requires", "produces", "supplies", "depends_on",
    "substitutable_with", "restricted_by", "impacted_by", "exports_to", "imports_from",
    "trade_dependency", "routes_through", "exposed_to_hazard", "uses_equipment",
    "uses_material", "uses_chemical", "uses_ip", "designed_by", "manufactured_by",
    "packaged_by", "tested_by", "serves_downstream_sector", "evidence_for",
    "evidence_context_link",
}


def load_edge_catalog() -> dict:
    return yaml.safe_load(EDGE_PATH.read_text(encoding="utf-8"))


def test_edge_catalog_has_required_edge_types_and_provenance() -> None:
    catalog = load_edge_catalog()
    edges = {entry["edge_type"]: entry for entry in catalog["edge_types"]}

    assert REQUIRED_EDGE_TYPES <= set(edges)
    for edge_type in REQUIRED_EDGE_TYPES:
        edge = edges[edge_type]
        assert edge["source_type"]
        assert edge["target_type"]
        assert edge["direction"]
        assert edge["required_provenance"]
        assert "source_id" in edge["required_provenance"]
        assert "provenance_url" in edge["required_provenance"]


def test_evidence_context_link_is_semantically_separate_from_dependency_edges() -> None:
    catalog = load_edge_catalog()
    edges = {entry["edge_type"]: entry for entry in catalog["edge_types"]}
    evidence_context = edges["evidence_context_link"]

    assert evidence_context["derived_context"] is True
    assert evidence_context["not_supply_chain_dependency"] is True
    assert evidence_context["user_facing_label"] == "evidence-context link"
    assert "not a supply-chain dependency edge" in evidence_context["description"].lower()


def test_edge_catalog_does_not_include_evasion_guidance() -> None:
    catalog_text = EDGE_PATH.read_text(encoding="utf-8").lower()
    forbidden = ["circumvention advice", "bypass controls", "illegal rerouting"]

    for phrase in forbidden:
        assert phrase not in catalog_text
