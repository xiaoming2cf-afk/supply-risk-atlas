from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CHAIN_PATH = ROOT / "configs" / "ontology" / "semiconductor_chain_layers.yaml"
MATRIX_PATH = ROOT / "configs" / "sources" / "stage_source_coverage_matrix.yaml"
SOURCE_REGISTRY_PATH = ROOT / "configs" / "sources" / "semiconductor.yaml"


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
    "source_families",
    "connector_files",
    "fixture_files",
    "live_fetch_default",
    "fixture_required",
    "source_payload_policy",
    "graph_views",
    "charts",
    "tables",
    "risk_model_usage",
    "simulation_usage",
    "source_gaps",
    "proxy_limitations",
    "priority",
    "current_coverage_status",
    "source_status",
    "evidence_ref_count",
    "calibration_status",
    "failure_reason",
    "required_narrow_patch_if_failed",
}

ALLOWED_SOURCE_STATUSES = {
    "fixture_promoted_public_evidence",
    "incomplete_fixture_proxy",
    "unavailable_controlled",
    "deferred_registry_only",
}

REQUIRED_SOURCE_FAMILIES = {
    "national_policy_macro_public",
    "enterprise_public_disclosure",
    "industry_public_fixture",
}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_stage_source_coverage_matrix_has_all_chain_layers() -> None:
    chain = _load_yaml(CHAIN_PATH)
    matrix = _load_yaml(MATRIX_PATH)

    expected = [layer["layer_id"] for layer in chain["layers"]]
    actual = [stage["stage_id"] for stage in matrix["stages"]]

    assert actual == expected


def test_stage_source_coverage_matrix_records_fixture_defaults() -> None:
    matrix = _load_yaml(MATRIX_PATH)

    assert matrix["production_status"] == "research_fixture"
    assert matrix["data_mode"] == "fixture"
    assert matrix["defaults"]["live_fetch_default"] == "disabled"
    assert matrix["defaults"]["fixture_required"] is True
    assert matrix["defaults"]["api_visibility_policy"] == "sanitized_summary_and_lineage_only"
    assert matrix["defaults"]["source_payload_policy"] == "no_raw_source_records"
    assert matrix["defaults"]["coverage_counting_policy"] == "authoritative_source_records_only"
    assert matrix["defaults"]["unavailable_preview_counted_as_coverage"] is False
    assert matrix["defaults"]["relationship_unavailable_counted_as_stage_coverage"] is False
    assert REQUIRED_SOURCE_FAMILIES <= set(matrix["source_family_definitions"])


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
        assert stage["source_families"], stage["stage_id"]
        assert set(stage["source_families"]) <= set(matrix["source_family_definitions"]), stage["stage_id"]
        assert stage["live_fetch_default"] == "disabled", stage["stage_id"]
        assert stage["fixture_required"] is True, stage["stage_id"]
        assert stage["source_payload_policy"] == matrix["defaults"]["source_payload_policy"], stage["stage_id"]
        assert stage["current_coverage_status"] in {"implemented", "partial", "missing", "deferred"}
        assert stage["source_status"] in ALLOWED_SOURCE_STATUSES, stage["stage_id"]
        assert isinstance(stage["evidence_ref_count"], int), stage["stage_id"]
        assert stage["evidence_ref_count"] >= 0, stage["stage_id"]
        assert isinstance(stage["proxy_limitations"], list), stage["stage_id"]
        assert stage["proxy_limitations"], stage["stage_id"]
        assert "production" not in str(stage["calibration_status"]).lower(), stage["stage_id"]
        if stage["current_coverage_status"] in {"partial", "missing", "deferred"}:
            assert stage["failure_reason"] not in {"", "none"}, stage["stage_id"]
            assert stage["required_narrow_patch_if_failed"] not in {"", "none"}, stage["stage_id"]


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


def test_stage_matrix_has_source_family_coverage() -> None:
    matrix = _load_yaml(MATRIX_PATH)
    families = {
        source_family
        for stage in matrix["stages"]
        for source_family in stage["source_families"]
    }

    assert REQUIRED_SOURCE_FAMILIES <= families


def test_stage_matrix_sources_are_registered_fixture_first_and_live_disabled() -> None:
    matrix = _load_yaml(MATRIX_PATH)
    registry = _load_yaml(SOURCE_REGISTRY_PATH)
    sources_by_id = {source["source_id"]: source for source in registry["sources"]}
    matrix_sources = {
        source_id
        for stage in matrix["stages"]
        for source_id in stage["primary_sources"] + stage["secondary_sources"]
    }

    assert matrix_sources <= set(sources_by_id)
    for source_id in matrix_sources:
        source = sources_by_id[source_id]
        assert source["live_fetch_default"] is False, source_id
        assert source["raw_payload_storage_policy"] == "hash_and_summary_only", source_id
        assert source["api_visibility_policy"] in {"summary_and_lineage_only", "registry_only"}, source_id


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
        "official",
        "production_verified",
        "source_status: official",
        "production_status: production",
    ]
    assert all(token not in rendered for token in forbidden_tokens)


def test_stage_source_docs_define_statuses_and_unavailable_preview_policy() -> None:
    matrix = _load_yaml(MATRIX_PATH)
    doc_text = (ROOT / "docs" / "data" / "stage-source-coverage-matrix.md").read_text(encoding="utf-8")

    assert "Source Status Legend" in doc_text
    assert "`unavailable_preview` UI states and unavailable relationship endpoints never count as stage coverage" in doc_text
    for status in ALLOWED_SOURCE_STATUSES:
        assert f"`{status}`" in doc_text
    for stage in matrix["stages"]:
        assert f"| {stage['stage_id'].split('_', 1)[0]}" in doc_text
        assert f"`{stage['source_status']}`" in doc_text


def test_stage_source_docs_have_no_expanded_production_claims() -> None:
    docs = [
        ROOT / "docs" / "data" / "stage-source-coverage-matrix.md",
        ROOT / "docs" / "data" / "connector-stage-coverage-audit.md",
    ]
    forbidden = [
        "production-ready",
        "production ready",
        "official",
        "production_verified",
        "authoritative live data",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text, f"{path} contains {token!r}"
