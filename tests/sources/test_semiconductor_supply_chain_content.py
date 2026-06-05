from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from sra_core.geo.terminology import CANONICAL_DISPLAY, CANONICAL_REGION_ID


ROOT = Path(__file__).resolve().parents[2]
CONTENT_PATH = ROOT / "configs" / "sources" / "semiconductor_supply_chain_content.yaml"


REQUIRED_SOURCE_FAMILIES = {
    "national_policy_macro_public",
    "enterprise_public_disclosure",
    "industry_public_fixture",
}

REQUIRED_LAYER_FIELDS = {
    "layer_id",
    "layer_name",
    "stage",
    "role_in_chain",
    "key_inputs",
    "key_outputs",
    "representative_entities",
    "concentration_risk",
    "substitutability",
    "lead_time_or_switching_cost_notes",
    "shock_sensitivity",
    "downstream_impact",
    "evidence_summary",
    "coverage_level",
    "provenance",
}

REQUIRED_ENTITY_FIELDS = {
    "entity_id",
    "name",
    "entity_type",
    "headquarters_country",
    "value_chain_roles",
    "primary_layers",
    "risk_tags",
    "dependency_tags",
    "substitution_notes",
    "evidence_summary",
    "coverage_level",
    "provenance",
}

REQUIRED_CHOKEPOINT_FIELDS = {
    "chokepoint_id",
    "layer_id",
    "title",
    "countries_regions",
    "representative_entities",
    "substitutability",
    "shock_sensitivity",
    "downstream_impact",
    "evidence_summary",
    "provenance",
}


def _load_content() -> dict[str, Any]:
    return yaml.safe_load(CONTENT_PATH.read_text(encoding="utf-8"))


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _assert_no_raw_or_sensitive_payload(value: Any) -> None:
    rendered = _render(value).lower()
    forbidden = [
        "raw_payload",
        "filing_body",
        "article_body",
        "authorization",
        "api_key",
        "secret",
        "cookie",
        "token",
    ]
    assert all(token not in rendered for token in forbidden)


def test_semiconductor_content_fixture_is_public_evidence_first() -> None:
    content = _load_content()

    assert content["data_mode"] == "fixture"
    assert content["graph_mode"] == "promoted_public_evidence"
    assert content["production_status"] == "research_fixture"
    assert content["live_fetch_default"] == "disabled"
    assert content["fixture_required"] is True
    assert content["api_visibility_policy"] == "sanitized_summary_and_lineage_only"
    assert content["source_payload_policy"] == "no_bulk_source_payloads_api_visible"
    assert REQUIRED_SOURCE_FAMILIES <= set(content["source_summaries"])
    _assert_no_raw_or_sensitive_payload(content)


def test_semiconductor_content_has_national_enterprise_and_industry_coverage() -> None:
    content = _load_content()

    assert len(content["country_region_exposures"]) >= 10
    assert len(content["value_chain_layers"]) >= 20
    assert len(content["entity_profiles"]) >= 35
    assert len(content["relationship_edges"]) >= 10
    assert len(content["chokepoints"]) >= 8

    source_summary_text = _render(content["source_summaries"])
    for source_id in (
        "oecd_semiconductor_value_chain_reports",
        "world_bank_macro_indicators_lite",
        "bis_export_controls_lite",
        "federal_register_export_controls_lite",
        "ofac_sanctions_list_lite",
        "consolidated_screening_list_lite",
        "usgs_mineral_commodity_summaries_lite",
        "un_comtrade_semiconductor_trade_lite",
        "wits_trade_tariff_lite",
        "nga_world_port_index_lite",
        "sec_edgar_lite",
        "company_annual_report_manual_upload",
        "eto_cset_advanced_semiconductor_supply_chain",
        "wsts_historical_billings",
        "gdelt_semiconductor_lite",
        "openalex_crossref_literature_lite",
    ):
        assert source_id in source_summary_text


def test_canonical_region_exposure_uses_parent_country_context() -> None:
    content = _load_content()
    exposures = {
        exposure["geo_id"]: exposure
        for exposure in content["country_region_exposures"]
    }

    region = exposures[CANONICAL_REGION_ID]
    assert region["display_name"] == CANONICAL_DISPLAY
    assert region["parent_country_id"] == "country:CN"
    assert region["parent_country_display"] == "中国"
    assert "country:" + "tw" not in _render(content).lower()
    assert "region:" + "tw" not in _render(content).lower()


def test_each_layer_entity_and_chokepoint_is_evidence_bound() -> None:
    content = _load_content()
    layer_ids = {layer["layer_id"] for layer in content["value_chain_layers"]}

    for layer in content["value_chain_layers"]:
        assert REQUIRED_LAYER_FIELDS <= set(layer), layer.get("layer_id")
        assert layer["stage"] in {"upstream", "midstream", "downstream", "support"}
        assert layer["provenance"], layer["layer_id"]
        assert layer["coverage_level"] == "public_evidence_fixture"
        assert layer["representative_entities"], layer["layer_id"]

    for entity in content["entity_profiles"]:
        assert REQUIRED_ENTITY_FIELDS <= set(entity), entity.get("entity_id")
        assert entity["entity_id"].startswith("company:"), entity["entity_id"]
        assert entity["primary_layers"], entity["entity_id"]
        assert set(entity["primary_layers"]) <= layer_ids, entity["entity_id"]
        assert entity["provenance"], entity["entity_id"]
        assert entity["coverage_level"] == "public_evidence_fixture"

    for chokepoint in content["chokepoints"]:
        assert REQUIRED_CHOKEPOINT_FIELDS <= set(chokepoint), chokepoint.get("chokepoint_id")
        assert chokepoint["layer_id"] in layer_ids, chokepoint["chokepoint_id"]
        assert chokepoint["provenance"], chokepoint["chokepoint_id"]
        assert chokepoint["countries_regions"], chokepoint["chokepoint_id"]


def test_relationship_summaries_are_classified_and_have_sources() -> None:
    content = _load_content()
    classes = {edge["relationship_class"] for edge in content["relationship_edges"]}

    assert {"SUPPLY_RELATIONSHIP", "DEMAND_RELATIONSHIP", "PRODUCTION_DEPENDENCY", "EVIDENCE_CONTEXT"} <= classes
    for edge in content["relationship_edges"]:
        assert edge["source_node_id"]
        assert edge["target_node_id"]
        assert edge["edge_type"]
        assert edge["provenance"]
        assert edge["evidence_summary"]
        assert edge["rationale"]
        if edge["relationship_class"] == "EVIDENCE_CONTEXT":
            assert edge.get("not_supply_chain_dependency") is True
        else:
            assert edge["edge_type"] != "evidence_context_link"


def test_stage_layer_source_coverage_is_queryable_from_fixture() -> None:
    content = _load_content()
    layer_ids = {layer["layer_id"] for layer in content["value_chain_layers"]}
    relationship_layer_ids = {
        node_id
        for edge in content["relationship_edges"]
        for node_id in (edge["source_node_id"], edge["target_node_id"], edge["source_id"], edge["target_id"])
        if str(node_id).startswith("vc_")
    }

    assert relationship_layer_ids <= layer_ids
    assert relationship_layer_ids
    for stage in {"upstream", "midstream", "downstream", "support"}:
        stage_layers = [layer for layer in content["value_chain_layers"] if layer["stage"] == stage]
        assert stage_layers, stage
        stage_sources = {source for layer in stage_layers for source in layer["provenance"]}
        assert len(stage_sources) >= 2, stage


def test_content_summary_service_exposes_l0_l11_stage_source_matrix() -> None:
    from services.api.services.semiconductor_content_service import semiconductor_content_summary_payload

    summary = semiconductor_content_summary_payload()
    rows = summary["stage_source_coverage_summary"]

    assert len(rows) == 12
    assert rows[0]["stage_id"] == "L0_policy_macro"
    assert rows[-1]["stage_id"] == "L11_compliance"
    for row in rows:
        assert row["source_count"] >= 2
        assert row["primary_source_count"] >= 1
        assert row["secondary_source_count"] >= 1
        assert {"national_policy_macro_public", "enterprise_public_disclosure", "industry_public_fixture"} <= set(
            row["source_families"]
        )
        assert row["relationship_classes"]
        assert row["source_refs"]
        assert row["live_fetch_default"] == "disabled"
        assert row["fixture_required"] is True
        assert row["calibration_status"] == "fixture_proxy_not_calibrated"
    for family in REQUIRED_SOURCE_FAMILIES:
        assert summary["stage_source_family_counts"][family]["stage_count"] == 12
        assert summary["stage_source_family_counts"][family]["source_count"] >= 1
