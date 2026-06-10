from __future__ import annotations

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from typing import Any

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api import main
from services.api.dev_server import Handler
from services.api.services import semiconductor_content_service as content_service
from sra_core.geo.terminology import CANONICAL_DISPLAY, CANONICAL_REGION_ID


def _client() -> TestClient:
    app = main.create_app()
    assert app is not None
    return TestClient(app)


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _assert_content_envelope(payload: dict[str, Any]) -> dict[str, Any]:
    assert payload["status"] == "success"
    data = payload["data"]
    for key in (
        "content_version",
        "graph_version",
        "source_manifest_id",
        "data_mode",
        "graph_mode",
        "source_status",
        "calibration_status",
        "fixture_required",
        "live_fetch_default",
        "warnings",
        "audit",
    ):
        assert key in data
    assert data["fixture_required"] is True
    assert data["live_fetch_default"] == "disabled"
    assert data["data_mode"] in {"fixture", "promoted"}
    assert data["graph_mode"] in {"fixture", "promoted", "promoted_public_evidence"}
    rendered = _render(payload).lower()
    for forbidden in ("raw_payload", "filing_body", "article_body", "authorization", "api_key", "secret"):
        assert forbidden not in rendered
    assert "country:" + "tw" not in rendered
    assert "region:" + "tw" not in rendered
    return data


@pytest.fixture()
def dev_server_base_url() -> str:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _get_json(base_url: str, path: str) -> tuple[int, dict[str, Any]]:
    with urllib.request.urlopen(f"{base_url}{path}", timeout=10) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _conflict_relationship_fixture() -> dict[str, Any]:
    return {
        "content_version": "test_conflict_relationships_v0",
        "source_manifest_id": "test_manifest",
        "data_mode": "fixture",
        "graph_mode": "fixture",
        "coverage_level": "test_fixture",
        "generated_at": "2026-05-12T00:00:00+00:00",
        "fixture_required": True,
        "live_fetch_default": "disabled",
        "warnings": ["test_fixture:not_production_ready"],
        "api_visibility_policy": "public_fields_only",
        "source_payload_policy": "source_payloads_excluded",
        "production_status": "test_fixture_not_production_ready",
        "country_region_exposures": [],
        "value_chain_layers": [
            {
                "layer_id": "vc_test_source",
                "layer_name": "Test source",
                "stage": "upstream",
                "coverage_level": "test_fixture",
                "provenance": ["eto_cset_advanced_semiconductor_supply_chain"],
            },
            {
                "layer_id": "vc_test_target",
                "layer_name": "Test target",
                "stage": "midstream",
                "coverage_level": "test_fixture",
                "provenance": ["eto_cset_advanced_semiconductor_supply_chain"],
            },
        ],
        "entity_profiles": [],
        "relationship_edges": [
            {
                "edge_id": "edge:valid-production-dependency",
                "source_id": "vc_test_source",
                "source_node_id": "vc_test_source",
                "target_id": "vc_test_target",
                "target_node_id": "vc_test_target",
                "relationship_type": "depends_on",
                "relationship_class": "PRODUCTION_DEPENDENCY",
                "edge_type": "depends_on",
                "confidence": "fixture_high",
                "rationale": "Valid test dependency.",
                "evidence_summary": "Public fixture evidence supports the dependency.",
                "provenance": ["eto_cset_advanced_semiconductor_supply_chain"],
            },
            {
                "edge_id": "edge:explicit-evidence-context-conflict",
                "source_id": "evidence:test_context",
                "source_node_id": "evidence:test_context",
                "target_id": "vc_test_target",
                "target_node_id": "vc_test_target",
                "relationship_type": "depends_on",
                "relationship_class": "EVIDENCE_CONTEXT",
                "edge_type": "depends_on",
                "confidence": "fixture_high",
                "rationale": "Depends-on syntax is context-only for this row.",
                "evidence_summary": "Public fixture evidence marks this as context.",
                "provenance": ["eto_cset_advanced_semiconductor_supply_chain"],
            },
            {
                "edge_id": "edge:not-supply-chain-dependency-conflict",
                "source_id": "evidence:test_context_flag",
                "source_node_id": "evidence:test_context_flag",
                "target_id": "vc_test_target",
                "target_node_id": "vc_test_target",
                "relationship_type": "depends_on",
                "relationship_class": "PRODUCTION_DEPENDENCY",
                "edge_type": "depends_on",
                "not_supply_chain_dependency": True,
                "confidence": "fixture_high",
                "rationale": "The explicit non-dependency flag makes this context-only.",
                "evidence_summary": "Public fixture evidence marks this as non-propagating context.",
                "provenance": ["eto_cset_advanced_semiconductor_supply_chain"],
            },
        ],
        "chokepoints": [],
        "source_summaries": {
            "industry_public_fixture": {
                "source_count": 1,
                "status": "fixture",
            }
        },
        "coverage_gaps": [],
    }


def test_semiconductor_coverage_overview_endpoint_returns_counts_and_sources() -> None:
    response = _client().get("/api/v1/semiconductor/coverage", headers={"x-request-id": "req_content"})
    assert response.status_code == 200
    payload = response.json()
    data = _assert_content_envelope(payload)

    assert payload["request_id"] == "req_content"
    assert data["coverage_counts"]["country_region_count"] >= 10
    assert data["coverage_counts"]["value_chain_layer_count"] >= 20
    assert data["coverage_counts"]["entity_profile_count"] >= 35
    assert data["coverage_counts"]["relationship_edge_count"] >= 10
    assert data["coverage_counts"]["chokepoint_count"] >= 8
    assert {"national_policy_macro_public", "enterprise_public_disclosure", "industry_public_fixture"} <= set(
        data["source_summaries"]
    )
    assert data["representative_country_region_exposures"]
    assert data["representative_value_chain_layers"]
    assert data["representative_entities"]
    assert data["representative_chokepoints"]
    assert len(data["stage_source_coverage_summary"]) == 12
    assert {"national_policy_macro_public", "enterprise_public_disclosure", "industry_public_fixture"} <= set(
        data["stage_source_family_counts"]
    )
    for row in data["stage_source_coverage_summary"]:
        assert row["stage_id"].startswith("L")
        assert row["source_count"] >= 2
        assert row["primary_source_count"] >= 1
        assert row["secondary_source_count"] >= 1
        assert {"national_policy_macro_public", "enterprise_public_disclosure", "industry_public_fixture"} <= set(
            row["source_families"]
        )
        assert row["relationship_classes"]
        assert row["graph_views"]
        assert row["charts"]
        assert row["tables"]
        assert isinstance(row["failure_reason"], str)
        assert isinstance(row["required_narrow_patch_if_failed"], str)
        assert row["live_fetch_default"] == "disabled"
        assert row["fixture_required"] is True
        if row["coverage_status"] != "implemented":
            assert row["failure_reason"] != "none"
            assert row["required_narrow_patch_if_failed"] != "none"


def test_value_chain_layer_endpoint_filters_by_stage() -> None:
    response = _client().get("/api/v1/semiconductor/value-chain/layers?stage=upstream&limit=50")
    assert response.status_code == 200
    data = _assert_content_envelope(response.json())

    assert data["filters"]["stage"] == "upstream"
    assert data["layers"]
    assert all(layer["stage"] == "upstream" for layer in data["layers"])
    assert all(layer["provenance"] for layer in data["layers"])


def test_country_region_exposure_endpoint_normalizes_canonical_region() -> None:
    response = _client().get(f"/api/v1/semiconductor/country-exposures?geo_id={CANONICAL_REGION_ID}")
    assert response.status_code == 200
    data = _assert_content_envelope(response.json())

    assert data["total"] == 1
    [region] = data["country_region_exposures"]
    assert region["geo_id"] == CANONICAL_REGION_ID
    assert region["display_name"] == CANONICAL_DISPLAY
    assert region["parent_country_id"] == "country:CN"
    assert region["parent_country_display"] == "中国"


def test_entity_profile_endpoint_returns_enterprise_supply_chain_role() -> None:
    response = _client().get("/api/v1/semiconductor/entities/company:TSMC")
    assert response.status_code == 200
    data = _assert_content_envelope(response.json())

    assert data["total"] == 1
    [profile] = data["entity_profiles"]
    assert profile["entity_id"] == "company:TSMC"
    assert profile["value_chain_roles"]
    assert profile["primary_layers"]
    assert profile["dependency_tags"]
    assert profile["provenance"]
    assert profile["headquarters_country"] == CANONICAL_REGION_ID


def test_entity_profile_endpoint_supports_stage_and_source_filters() -> None:
    response = _client().get(
        "/api/v1/semiconductor/entities?stage=midstream&source_id=company_annual_report_manual_upload&limit=50"
    )
    assert response.status_code == 200
    data = _assert_content_envelope(response.json())

    assert data["filters"]["stage"] == "midstream"
    assert data["filters"]["source_id"] == "company_annual_report_manual_upload"
    assert data["entity_profiles"]
    assert all("company_annual_report_manual_upload" in row["provenance"] for row in data["entity_profiles"])


def test_chokepoint_endpoint_filters_by_stage() -> None:
    response = _client().get("/api/v1/semiconductor/chokepoints?stage=midstream&limit=50")
    assert response.status_code == 200
    data = _assert_content_envelope(response.json())

    assert data["filters"]["stage"] == "midstream"
    assert data["chokepoints"]
    assert all(chokepoint["provenance"] for chokepoint in data["chokepoints"])


def test_relationship_endpoint_returns_standardized_supply_rows() -> None:
    response = _client().get(
        "/api/v1/semiconductor/relationships?relationship_class=SUPPLY_RELATIONSHIP&limit=20"
    )
    assert response.status_code == 200
    data = _assert_content_envelope(response.json())

    assert data["filters"]["relationship_class"] == "SUPPLY_RELATIONSHIP"
    assert data["relationships"]
    assert set(data["relationship_class_counts"]) == {"SUPPLY_RELATIONSHIP"}
    for row in data["relationships"]:
        assert row["relationship_class"] == "SUPPLY_RELATIONSHIP"
        assert row["supplied_item_id"]
        assert row["supplier_id"] == row["source_node_id"]
        assert row["source_refs"]
        assert row["evidence_refs"]
        assert row["valid_from"]
        assert row["valid_to"] is None
        assert row["can_propagate_risk"] is True
        assert row["edge_type"] != "evidence_context_link"


def test_relationship_endpoint_keeps_evidence_context_non_propagating() -> None:
    response = _client().get(
        "/api/v1/semiconductor/relationships?relationship_class=EVIDENCE_CONTEXT&limit=20"
    )
    assert response.status_code == 200
    data = _assert_content_envelope(response.json())

    assert data["relationships"]
    for row in data["relationships"]:
        assert row["relationship_class"] == "EVIDENCE_CONTEXT"
        assert row["not_supply_chain_dependency"] is True
        assert row["can_propagate_risk"] is False
        assert row["warning"] == "This is not a supply-chain dependency edge."


def test_relationship_endpoint_keeps_conflict_context_out_of_dependency_propagation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(content_service, "_content_fixture", _conflict_relationship_fixture)

    dependency_response = _client().get(
        "/api/v1/semiconductor/relationships?relationship_class=PRODUCTION_DEPENDENCY&limit=20"
    )
    dependency_data = _assert_content_envelope(dependency_response.json())

    assert dependency_response.status_code == 200
    assert {row["edge_id"] for row in dependency_data["relationships"]} == {
        "edge:valid-production-dependency"
    }
    assert dependency_data["relationship_class_counts"] == {"PRODUCTION_DEPENDENCY": 1}
    assert all(row["can_propagate_risk"] is True for row in dependency_data["relationships"])

    evidence_response = _client().get(
        "/api/v1/semiconductor/relationships?relationship_class=EVIDENCE_CONTEXT&edge_type=depends_on&limit=20"
    )
    evidence_data = _assert_content_envelope(evidence_response.json())
    evidence_rows = evidence_data["relationships"]

    assert evidence_response.status_code == 200
    assert {row["edge_id"] for row in evidence_rows} == {
        "edge:explicit-evidence-context-conflict",
        "edge:not-supply-chain-dependency-conflict",
    }
    assert evidence_data["relationship_class_counts"] == {"EVIDENCE_CONTEXT": 2}
    for row in evidence_rows:
        assert row["relationship_class"] == "EVIDENCE_CONTEXT"
        assert row["edge_type"] == "depends_on"
        assert row["not_supply_chain_dependency"] is True
        assert row["can_propagate_risk"] is False


def test_source_coverage_endpoint_summarizes_layer_support() -> None:
    response = _client().get("/api/v1/semiconductor/source-coverage?stage=midstream&limit=50")
    assert response.status_code == 200
    data = _assert_content_envelope(response.json())

    assert data["filters"]["stage"] == "midstream"
    assert data["stage_source_coverage"]
    assert data["source_family_counts"]
    assert data["relationship_class_counts"]
    for row in data["stage_source_coverage"]:
        assert row["stage"] == "midstream"
        assert row["source_refs"]
        assert row["source_families"]
        assert row["connector_status"] == "fixture_required_live_disabled"
        assert row["live_fetch_default"] == "disabled"


def test_system_health_and_entity_risk_include_semiconductor_content_summaries() -> None:
    client = _client()
    health = client.get("/api/v1/dashboard/system-health-center").json()
    risk = client.get("/api/v1/risk/entities/company%3Atsmc").json()

    assert health["status"] == "success"
    content = health["data"]["semiconductorContentCoverage"]
    assert content["counts"]["country_region_count"] >= 10
    assert content["counts"]["entity_profile_count"] >= 35
    assert content["counts"]["source_family_count"] >= 3
    assert len(content["stage_source_coverage_summary"]) == 12
    assert content["stage_source_coverage_summary"][0]["stage_id"] == "L0_policy_macro"
    assert content["stage_source_coverage_summary"][-1]["stage_id"] == "L11_compliance"
    assert content["stage_source_family_counts"]["national_policy_macro_public"]["stage_count"] == 12
    assert content["stage_source_family_counts"]["enterprise_public_disclosure"]["stage_count"] == 12
    assert content["stage_source_family_counts"]["industry_public_fixture"]["stage_count"] == 12
    assert risk["status"] == "success"
    profile = risk["data"]["semiconductor_profile"]
    assert profile["entity_id"] == "company:TSMC"
    assert profile["headquarters_country"] == CANONICAL_REGION_ID
    assert profile["value_chain_roles"]
    assert profile["provenance"]
    _assert_content_envelope(main.route_semiconductor_coverage_overview())


def test_dev_server_serves_semiconductor_content_routes(dev_server_base_url: str) -> None:
    coverage_status, coverage = _get_json(dev_server_base_url, "/api/v1/semiconductor/coverage")
    entity_status, entity = _get_json(dev_server_base_url, "/api/v1/semiconductor/entities/company:TSMC")
    relationship_status, relationships = _get_json(
        dev_server_base_url,
        "/api/v1/semiconductor/relationships?relationship_class=SUPPLY_RELATIONSHIP&limit=5",
    )

    assert coverage_status == 200
    assert entity_status == 200
    assert relationship_status == 200
    assert coverage["data"]["coverage_counts"]["value_chain_layer_count"] >= 20
    assert entity["data"]["entity_profiles"][0]["entity_id"] == "company:TSMC"
    assert relationships["data"]["relationships"]
    _assert_content_envelope(coverage)
    _assert_content_envelope(entity)
    _assert_content_envelope(relationships)
