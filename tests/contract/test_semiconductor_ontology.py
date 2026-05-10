from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_PATH = ROOT / "configs" / "ontology" / "semiconductor.yaml"

EXPECTED_NODE_TYPES = {
    "company",
    "country",
    "region",
    "facility",
    "process_stage",
    "equipment",
    "material",
    "chemical",
    "component",
    "product_grade",
    "technology_node",
    "policy_event",
    "risk_event",
    "market_indicator",
    "trade_flow",
    "route",
}
EXPECTED_EDGE_TYPES = {
    "participates_in",
    "located_in",
    "requires",
    "produces",
    "supplies",
    "depends_on",
    "substitutable_with",
    "restricted_by",
    "impacted_by",
    "exports_to",
    "imports_from",
    "routes_through",
    "correlated_with",
    "evidence_for",
}
REQUIRED_NODE_FIELDS = {"node_id", "node_type", "canonical_name", "source_refs", "confidence", "valid_from", "valid_to"}
REQUIRED_EDGE_FIELDS = {
    "edge_id",
    "source_node_id",
    "target_node_id",
    "edge_type",
    "weight",
    "confidence",
    "valid_from",
    "valid_to",
    "provenance_refs",
    "evidence_text_summary",
}


def _load_ontology() -> dict:
    return yaml.safe_load(ONTOLOGY_PATH.read_text(encoding="utf-8"))


def test_semiconductor_ontology_declares_exact_foundation_types() -> None:
    payload = _load_ontology()

    assert payload["schema_version"] == "semiconductor_ontology_v0.1"
    assert set(payload["node_types"]) == EXPECTED_NODE_TYPES
    assert set(payload["edge_types"]) == EXPECTED_EDGE_TYPES


def test_node_types_require_provenance_and_temporal_validity() -> None:
    for node_name, node_spec in _load_ontology()["node_types"].items():
        assert node_spec["description"], node_name
        assert REQUIRED_NODE_FIELDS.issubset(node_spec["required_fields"]), node_name
        assert set(node_spec["allowed_edge_directions"]) == {"outgoing", "incoming"}, node_name
        assert node_spec["example"], node_name
        assert node_spec["version"] == "v0.1", node_name


def test_edge_types_require_provenance_temporal_validity_and_valid_directions() -> None:
    payload = _load_ontology()
    node_types = set(payload["node_types"])

    for edge_name, edge_spec in payload["edge_types"].items():
        assert edge_spec["description"], edge_name
        assert REQUIRED_EDGE_FIELDS.issubset(edge_spec["required_fields"]), edge_name
        assert set(edge_spec["source"]).issubset(node_types), edge_name
        assert set(edge_spec["target"]).issubset(node_types), edge_name
        assert edge_spec["allowed_edge_directions"]["source_to_target"] is True, edge_name
        assert edge_spec["example"], edge_name
        assert edge_spec["version"] == "v0.1", edge_name
