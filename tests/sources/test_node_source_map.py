from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CHAIN_PATH = ROOT / "configs" / "ontology" / "semiconductor_chain_layers.yaml"
MAP_PATH = ROOT / "configs" / "sources" / "semiconductor_node_source_map.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_every_chain_layer_has_at_least_two_source_candidates() -> None:
    chain = load_yaml(CHAIN_PATH)
    source_map = load_yaml(MAP_PATH)

    expected_layers = {layer["layer_id"] for layer in chain["layers"]}
    layer_candidates = source_map["layer_source_candidates"]

    assert set(layer_candidates) == expected_layers
    for layer_id, candidates in layer_candidates.items():
        assert len(set(candidates)) >= 2, layer_id


def test_every_chain_node_type_has_a_source_candidate() -> None:
    chain = load_yaml(CHAIN_PATH)
    source_map = load_yaml(MAP_PATH)
    expected_node_types = {
        node_type
        for layer in chain["layers"]
        for node_type in layer["node_types"]
    }
    mapped_node_types = {
        node_type
        for source in source_map["sources"]
        for node_type in source["node_types"]
    }

    assert expected_node_types <= mapped_node_types


def test_every_source_has_graph_outputs_and_live_fetch_disabled() -> None:
    source_map = load_yaml(MAP_PATH)

    for source in source_map["sources"]:
        assert source["graph_outputs"], source["source_id"]
        assert source["relationship_classes"], source["source_id"]
        assert source["live_fetch_default"] == "disabled"
        assert source["fixture_required"] is True
        assert source["priority"] in {"P0", "P1", "P2"}
        assert source["api_visibility_policy"] == "sanitized_summary_only"


def test_supply_demand_dependency_and_evidence_classes_have_source_candidates() -> None:
    source_map = load_yaml(MAP_PATH)
    coverage = source_map["relationship_class_source_candidates"]

    assert set(coverage) == {
        "SUPPLY_RELATIONSHIP",
        "DEMAND_RELATIONSHIP",
        "PRODUCTION_DEPENDENCY",
        "EVIDENCE_CONTEXT",
    }
    for relationship_class, candidates in coverage.items():
        assert len(candidates) >= 1, relationship_class


def test_geographic_source_entries_require_normalization() -> None:
    source_map = load_yaml(MAP_PATH)
    geographic_node_types = {"country", "region", "mining_country", "refining_country", "port", "airport", "customs_region"}

    for source in source_map["sources"]:
        if geographic_node_types & set(source["node_types"]):
            assert source["geography_normalization_required"] is True


def test_node_source_map_uses_research_status_only() -> None:
    source_map = load_yaml(MAP_PATH)

    assert source_map["production_status"] == "research_fixture"
    assert source_map["calibration_status"] == "fixture_proxy_not_calibrated"
    assert "production-ready" not in str(source_map).lower()
