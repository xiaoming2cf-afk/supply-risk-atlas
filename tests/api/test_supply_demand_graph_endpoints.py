from __future__ import annotations

import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api.main import create_app


def _client() -> TestClient:
    app = create_app()
    assert app is not None
    return TestClient(app)


def _assert_graph_relationship_envelope(payload: dict[str, object]) -> dict[str, object]:
    assert payload["status"] == "success"
    data = payload["data"]
    assert isinstance(data, dict)
    for key in ("graph_version", "source_manifest_id", "data_mode", "graph_mode", "warnings"):
        assert key in data
    rendered = json.dumps(payload, sort_keys=True).lower()
    assert "raw_payload" not in rendered
    assert "article_body" not in rendered
    assert "filing_body" not in rendered
    assert "authorization" not in rendered
    assert "api_key" not in rendered
    return data


@pytest.mark.parametrize(
    ("path", "expected_class"),
    [
        ("/api/v1/graph/supply-relationships?limit=20", "SUPPLY_RELATIONSHIP"),
        ("/api/v1/graph/demand-relationships?limit=20", "DEMAND_RELATIONSHIP"),
        ("/api/v1/graph/production-dependencies?limit=20", "PRODUCTION_DEPENDENCY"),
    ],
)
def test_relationship_graph_endpoints_return_bounded_relationship_rows(
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    expected_class: str,
) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    response = _client().get(path)
    data = _assert_graph_relationship_envelope(response.json())

    assert response.status_code == 200
    assert data["relationship_class"] == expected_class
    assert len(data["relationships"]) <= 20
    assert data["layout_hints"]["does_not_render_full_graph"] is True
    assert data["evidence_refs"]
    assert data["calibration_status"] == "fixture_or_promoted_calibration_not_validated"
    assert data["source_status"] == "fixture_or_promoted_public_evidence"
    assert all(row["relationship_class"] == expected_class for row in data["relationships"])
    rendered_relationships = json.dumps(data["relationships"], sort_keys=True)
    assert "EVIDENCE_CONTEXT" not in rendered_relationships
    assert "evidence_context_link" not in rendered_relationships
    for row in data["relationships"]:
        for key in (
            "edge_type",
            "source_node_id",
            "target_node_id",
            "source_id",
            "target_id",
            "source_refs",
            "evidence_refs",
            "confidence",
            "valid_from",
            "valid_to",
            "graph_version",
            "source_manifest_id",
            "data_mode",
            "graph_mode",
            "source_status",
            "calibration_status",
        ):
            assert key in row
        assert row["source_id"] == row["source_node_id"]
        assert row["target_id"] == row["target_node_id"]
        assert row["graph_version"] == data["graph_version"]
        assert row["source_manifest_id"] == data["source_manifest_id"]
        assert row["data_mode"] == data["data_mode"]
        assert row["graph_mode"] == data["graph_mode"]
        assert row["source_status"] == data["source_status"]
        assert row["relationship_class"] != "EVIDENCE_CONTEXT"
        assert row["edge_type"] != "evidence_context_link"
        assert isinstance(row["source_refs"], list)
        assert isinstance(row["evidence_refs"], list)
        assert isinstance(row["warnings"], list)
        assert row["calibration_status"] == "fixture_or_promoted_calibration_not_validated"
        assert row["confidence"] is None or isinstance(row["confidence"], (int, float))
        assert "valid_from" in row
        assert "valid_to" in row
    if expected_class == "SUPPLY_RELATIONSHIP":
        assert all(row.get("supplied_item_id") for row in data["relationships"])
    if expected_class == "DEMAND_RELATIONSHIP":
        assert all(row.get("demand_proxy_type") for row in data["relationships"])
    if expected_class == "PRODUCTION_DEPENDENCY":
        assert all("criticality" in row and "substitutability" in row for row in data["relationships"])
        assert all(isinstance(row["criticality"], (int, float)) for row in data["relationships"])
        assert all(isinstance(row["substitutability"], (int, float)) for row in data["relationships"])


def test_supply_relationship_endpoint_includes_concentration_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    response = _client().get("/api/v1/graph/supply-relationships?limit=20")
    data = _assert_graph_relationship_envelope(response.json())

    assert response.status_code == 200
    assert data["supplier_concentration"]
    assert all("hhi_component" in row for row in data["supplier_concentration"])


def test_supply_demand_balance_endpoint_returns_product_grade_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    response = _client().get("/api/v1/graph/supply-demand-balance?limit=20")
    data = _assert_graph_relationship_envelope(response.json())

    assert response.status_code == 200
    assert data["relationship_class"] == "SUPPLY_DEMAND_BALANCE"
    assert len(data["balance_rows"]) <= 20
    assert data["layout_hints"]["table_only"] is True
    assert data["evidence_refs"]
    assert data["calibration_status"] == "fixture_or_promoted_calibration_not_validated"
    assert any(row["demand_edge_count"] >= 1 for row in data["balance_rows"])
    for row in data["balance_rows"]:
        assert row["relationship_class"] == "SUPPLY_DEMAND_BALANCE"
        assert row["row_type"] == "aggregate"
        assert row["not_supply_chain_dependency"] is True
        assert row.get("edge_type") != "evidence_context_link"
        assert row["source_refs"]
        assert row["evidence_refs"]
        assert row["calibration_status"] == "fixture_or_promoted_calibration_not_validated"
        assert "supply_demand_balance_is_aggregate_not_dependency_edge" in row["warnings"]
    serialized = json.dumps(data, sort_keys=True)
    assert "EVIDENCE_CONTEXT" not in serialized
    assert "evidence_context_link" not in serialized


@pytest.mark.parametrize("relationship_class", ["SUPPLY_RELATIONSHIP", " supply_relationship "])
def test_graph_view_filters_by_relationship_class(relationship_class: str) -> None:
    response = _client().get("/api/v1/graph/view", params={"relationship_class": relationship_class})
    data = _assert_graph_relationship_envelope(response.json())

    assert response.status_code == 200
    assert data["relationship_class_filter"] == "SUPPLY_RELATIONSHIP"
    assert all(edge["relationship_class"] == "SUPPLY_RELATIONSHIP" for edge in data["edges"])


def test_graph_view_rejects_unknown_relationship_class_filter() -> None:
    response = _client().get("/api/v1/graph/view?relationship_class=not_a_class")
    data = _assert_graph_relationship_envelope(response.json())

    assert response.status_code == 200
    assert data.get("relationship_class_filter") is None
    assert data["edges"] == []
