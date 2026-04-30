from __future__ import annotations

import pytest

pytest.importorskip("pydantic")
from pydantic import ValidationError

from services.api.main import route_predictions
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
        PredictionRequest(target_id="firm_anchor"),
        request_id="req_predictions",
    )

    assert payload["request_id"] == "req_predictions"
    assert payload["status"] == "success"
    assert payload["data"]
    assert {prediction["target_id"] for prediction in payload["data"]} == {"firm_anchor"}
