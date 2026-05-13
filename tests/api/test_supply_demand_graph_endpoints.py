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
    assert all(row["relationship_class"] == expected_class for row in data["relationships"])


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
    assert any(row["demand_edge_count"] >= 1 for row in data["balance_rows"])


def test_graph_view_filters_by_relationship_class() -> None:
    response = _client().get("/api/v1/graph/view?relationship_class=SUPPLY_RELATIONSHIP")
    data = _assert_graph_relationship_envelope(response.json())

    assert response.status_code == 200
    assert data["relationship_class_filter"] == "SUPPLY_RELATIONSHIP"
    assert all(edge["relationship_class"] == "SUPPLY_RELATIONSHIP" for edge in data["edges"])
