from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
RAW_SCHEMA_DIR = ROOT / "data_contracts" / "raw_schema"
SILVER_SCHEMA_DIR = ROOT / "data_contracts" / "silver_schema"
GRAPH_SCHEMA_DIR = ROOT / "data_contracts" / "graph_schema"
SOURCE_REGISTRY_PATH = ROOT / "configs" / "sources" / "semiconductor.yaml"

REQUIRED_RAW_SCHEMAS = [
    "sec_edgar_lite_raw.schema.json",
    "gdelt_semiconductor_lite_raw.schema.json",
    "un_comtrade_semiconductor_trade_raw.schema.json",
    "wits_trade_tariff_raw.schema.json",
    "usgs_earthquake_raw.schema.json",
    "nga_world_port_index_raw.schema.json",
    "ofac_sanctions_list_raw.schema.json",
    "bis_export_controls_raw.schema.json",
]

REQUIRED_SILVER_SCHEMAS = [
    "company_disclosure_event.schema.json",
    "semiconductor_risk_event.schema.json",
    "semiconductor_trade_flow.schema.json",
    "trade_tariff_indicator.schema.json",
    "natural_hazard_event.schema.json",
    "logistics_facility.schema.json",
    "sanctions_screening_event.schema.json",
    "export_control_policy_event.schema.json",
]

REQUIRED_GRAPH_SCHEMAS = [
    "evidence_context_link.schema.json",
    "trade_dependency_edge.schema.json",
    "logistics_route_edge.schema.json",
    "policy_restriction_edge.schema.json",
    "hazard_exposure_edge.schema.json",
]

RAW_REQUIRED_FIELDS = {
    "source_id",
    "source_record_id",
    "retrieved_at",
    "as_of_time",
    "payload_hash",
    "provenance_url",
    "raw_payload_summary",
    "license_or_terms_ref",
}

SILVER_REQUIRED_FIELDS = {
    "source_refs",
    "confidence",
    "valid_from",
    "valid_to",
    "evidence_text_summary",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_required_raw_source_contracts_are_summary_hash_and_lineage_only() -> None:
    for filename in REQUIRED_RAW_SCHEMAS:
        schema = _load_json(RAW_SCHEMA_DIR / filename)
        required = set(schema["required"])
        properties = schema["properties"]

        assert RAW_REQUIRED_FIELDS <= required
        assert "raw_payload" not in properties
        assert "article_body" not in properties
        assert "filing_body" not in properties
        assert properties["payload_hash"]["pattern"] == "^[a-f0-9]{64}$"
        assert properties["raw_payload_summary"]["type"] == "string"


def test_required_silver_contracts_keep_source_refs_confidence_and_validity() -> None:
    for filename in REQUIRED_SILVER_SCHEMAS:
        schema = _load_json(SILVER_SCHEMA_DIR / filename)
        required = set(schema["required"])

        assert SILVER_REQUIRED_FIELDS <= required
        assert schema["properties"]["source_refs"]["minItems"] == 1
        assert schema["properties"]["confidence"]["minimum"] == 0
        assert schema["properties"]["confidence"]["maximum"] == 1


def test_required_graph_contracts_have_explicit_semantics_and_provenance() -> None:
    for filename in REQUIRED_GRAPH_SCHEMAS:
        schema = _load_json(GRAPH_SCHEMA_DIR / filename)
        required = set(schema["required"])

        assert "provenance_refs" in required
        assert "evidence_text_summary" in required
        assert "user_facing_label" in required
        assert schema["properties"]["confidence"]["maximum"] == 1


def test_source_registry_contract_references_exist() -> None:
    registry = yaml.safe_load(SOURCE_REGISTRY_PATH.read_text(encoding="utf-8"))

    for source in registry["sources"]:
        for field in ("raw_contract", "silver_contract", "graph_contract"):
            path = ROOT / source[field]
            assert path.exists(), f"{source['source_id']} missing {field}: {path}"

