from __future__ import annotations

import pytest

pytest.importorskip("pydantic")
from pydantic import ValidationError

from services.api.main import route_dashboard_page, route_health, route_predictions
from sra_core.api.envelope import make_envelope, make_error_envelope
from sra_core.contracts.domain import PredictionRequest, ReportRequest
from sra_core.pipeline import default_metadata, run_synthetic_pipeline


def test_success_envelope_matches_contract_shape() -> None:
    result = run_synthetic_pipeline()

    payload = make_envelope(
        {"service": "api"},
        metadata=default_metadata(result),
        request_id="req_contract",
    )

    assert payload["request_id"] == "req_contract"
    assert payload["status"] == "success"
    assert payload["data"] == {"service": "api"}
    assert payload["metadata"]["graph_version"] == result.snapshot.graph_version
    assert payload["warnings"] == []
    assert payload["errors"] == []


def test_error_envelope_matches_contract_shape() -> None:
    result = run_synthetic_pipeline()

    payload = make_error_envelope(
        "entity_not_found",
        "Entity not found: missing",
        metadata=default_metadata(result),
        request_id="req_error",
        field="entity_id",
    )

    assert payload["request_id"] == "req_error"
    assert payload["status"] == "error"
    assert payload["data"] is None
    assert payload["errors"] == [
        {
            "code": "entity_not_found",
            "message": "Entity not found: missing",
            "field": "entity_id",
        }
    ]


def test_request_contracts_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        PredictionRequest(target_id="firm_anchor", unknown=True)

    assert ReportRequest(report_type="entity", target_id="firm_anchor").target_id == "firm_anchor"


def test_prediction_route_filters_by_contract_request() -> None:
    payload = route_predictions(
        PredictionRequest(target_id="firm_apple"),
        request_id="req_predictions",
    )

    assert payload["request_id"] == "req_predictions"
    assert payload["status"] == "success"
    assert payload["data"]
    assert payload["metadata"]["data_mode"] == "real"
    assert {prediction["target_id"] for prediction in payload["data"]} == {"firm_apple"}


def test_health_route_exposes_public_real_source_manifest() -> None:
    payload = route_health(request_id="req_real_health")

    assert payload["status"] == "success"
    assert payload["metadata"]["data_mode"] == "real"
    assert payload["metadata"]["source_count"] >= 8
    assert payload["data"]["source_manifest_ref"].startswith("manifest_public_real_")
    assert {source["source_id"] for source in payload["data"]["sources"]} >= {
        "sec_edgar",
        "gleif",
        "gdelt",
        "world_bank",
        "ofac",
        "ourairports",
        "nga_world_port_index",
        "usgs_earthquakes",
    }


def test_path_analysis_dashboard_contract_uses_planned_field_names() -> None:
    payload = route_dashboard_page("path-analysis", request_id="req_path_contract")

    assert payload["request_id"] == "req_path_contract"
    assert payload["status"] == "success"
    assert payload["metadata"]["data_mode"] == "real"

    data = payload["data"]
    assert set(data) >= {"criticalNodes", "transmissionPaths"}
    assert data["criticalNodes"]
    assert data["transmissionPaths"]

    critical_node = data["criticalNodes"][0]
    assert set(critical_node) >= {"id", "label", "kind", "level", "score", "drivers"}
    assert isinstance(critical_node["drivers"], list)

    transmission_path = data["transmissionPaths"][0]
    assert set(transmission_path) >= {
        "id",
        "sourceId",
        "targetId",
        "nodeSequence",
        "edgeSequence",
        "pathRisk",
        "pathConfidence",
    }
    assert len(transmission_path["edgeSequence"]) == len(transmission_path["nodeSequence"]) - 1


def test_country_lens_dashboard_contract_uses_planned_field_names() -> None:
    payload = route_dashboard_page("country-lens", request_id="req_country_contract")

    assert payload["request_id"] == "req_country_contract"
    assert payload["status"] == "success"
    assert payload["metadata"]["data_mode"] == "real"

    data = payload["data"]
    assert set(data) >= {"availableCountries", "countryLens"}
    assert data["availableCountries"]
    assert data["countryLens"]

    country = data["availableCountries"][0]
    assert set(country) >= {"code", "label", "entityCount", "riskScore"}

    lens = data["countryLens"]
    assert set(lens) >= {"countryCode", "countryName", "riskScore", "criticalNodes", "transmissionPaths"}
    assert lens["countryCode"] in {country["code"] for country in data["availableCountries"]}
