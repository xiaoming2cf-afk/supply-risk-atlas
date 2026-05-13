from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CHAIN_PATH = ROOT / "configs" / "ontology" / "semiconductor_chain_layers.yaml"
MATRIX_PATH = ROOT / "configs" / "sources" / "stage_source_coverage_matrix.yaml"


REQUIRED_STAGE_FIELDS = {
    "stage_id",
    "stage_name",
    "business_question",
    "core_node_types",
    "core_edge_types",
    "relationship_classes",
    "required_data_fields",
    "primary_sources",
    "secondary_sources",
    "connector_files",
    "fixture_files",
    "graph_views",
    "charts",
    "tables",
    "risk_model_usage",
    "simulation_usage",
    "source_gaps",
    "priority",
    "current_coverage_status",
}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_stage_source_coverage_matrix_has_all_chain_layers() -> None:
    chain = _load_yaml(CHAIN_PATH)
    matrix = _load_yaml(MATRIX_PATH)

    expected = [layer["layer_id"] for layer in chain["layers"]]
    actual = [stage["stage_id"] for stage in matrix["stages"]]

    assert actual == expected


def test_each_stage_has_source_view_chart_and_table_coverage() -> None:
    matrix = _load_yaml(MATRIX_PATH)

    for stage in matrix["stages"]:
        assert REQUIRED_STAGE_FIELDS <= set(stage), stage["stage_id"]
        sources = set(stage["primary_sources"]) | set(stage["secondary_sources"])
        assert len(sources) >= 2, stage["stage_id"]
        assert stage["graph_views"], stage["stage_id"]
        assert stage["charts"], stage["stage_id"]
        assert stage["tables"], stage["stage_id"]
        assert stage["core_node_types"], stage["stage_id"]
        assert stage["core_edge_types"], stage["stage_id"]
        assert stage["relationship_classes"], stage["stage_id"]
        assert stage["current_coverage_status"] in {"implemented", "partial", "missing", "deferred"}


def test_stage_matrix_records_connector_fixtures_and_gaps() -> None:
    matrix = _load_yaml(MATRIX_PATH)

    for stage in matrix["stages"]:
        assert stage["connector_files"], stage["stage_id"]
        assert stage["fixture_files"], stage["stage_id"]
        assert isinstance(stage["source_gaps"], list), stage["stage_id"]
        assert stage["priority"] in {"P0", "P1", "P2"}


def test_stage_matrix_has_relationship_class_coverage() -> None:
    matrix = _load_yaml(MATRIX_PATH)
    classes = {
        relationship_class
        for stage in matrix["stages"]
        for relationship_class in stage["relationship_classes"]
    }

    assert "SUPPLY_RELATIONSHIP" in classes
    assert "DEMAND_RELATIONSHIP" in classes
    assert "PRODUCTION_DEPENDENCY" in classes
    assert "EVIDENCE_CONTEXT" in classes


def test_stage_matrix_has_no_forbidden_geography_or_production_claim() -> None:
    rendered = json.dumps(_load_yaml(MATRIX_PATH), ensure_ascii=False, sort_keys=True)

    forbidden_tokens = [
        "country:" + "tw",
        "country:" + "TW",
        "country:" + "Tai" + "wan",
        "region:" + "tw",
        "region:" + "TW",
        "region:" + "Tai" + "wan",
        "production-ready",
        "production ready",
    ]
    assert all(token not in rendered for token in forbidden_tokens)
