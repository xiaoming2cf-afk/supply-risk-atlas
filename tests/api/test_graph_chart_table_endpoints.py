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


def _assert_sanitized_envelope(payload: dict[str, object]) -> dict[str, object]:
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
    ("path", "key"),
    [
        ("/api/v1/graph/timeline", "events"),
        ("/api/v1/graph/geo", "countries"),
        ("/api/v1/graph/matrix", "adjacency_matrix"),
        ("/api/v1/graph/layers", "layers"),
        ("/api/v1/graph/evidence", "evidence_refs"),
        ("/api/v1/graph/scenario-overlay", "affected_nodes"),
        ("/api/v1/graph/node-catalog", "node_catalog"),
        ("/api/v1/graph/source-coverage", "source_coverage"),
    ],
)
def test_additional_graph_view_endpoints_return_bounded_sanitized_data(path: str, key: str) -> None:
    response = _client().get(path)
    data = _assert_sanitized_envelope(response.json())

    assert response.status_code == 200
    assert key in data
    value = data[key]
    if isinstance(value, list):
        assert len(value) <= 500


def test_graph_node_catalog_endpoint_is_table_only_and_source_bound() -> None:
    response = _client().get("/api/v1/graph/node-catalog?limit=20")
    data = _assert_sanitized_envelope(response.json())

    assert response.status_code == 200
    assert len(data["node_catalog"]) <= 20
    assert data["layout_hints"]["table_only"] is True
    assert data["layout_hints"]["does_not_render_full_graph"] is True
    assert all(row["source_candidates"] for row in data["node_catalog"])


def test_graph_source_coverage_endpoint_reports_catalog_coverage() -> None:
    response = _client().get("/api/v1/graph/source-coverage?limit=20")
    data = _assert_sanitized_envelope(response.json())

    assert response.status_code == 200
    coverage = data["source_coverage"]
    assert coverage["source_count"] > 0
    assert len(coverage["rows"]) <= 20
    assert coverage["node_catalog_coverage"]["catalog_node_count"] >= 150
    assert coverage["node_catalog_coverage"]["status"] in {"pass", "partial"}


def test_analytics_charts_endpoint_returns_expected_chart_keys() -> None:
    response = _client().get("/api/v1/analytics/charts?limit=25")
    data = _assert_sanitized_envelope(response.json())

    assert response.status_code == 200
    charts = data["charts"]
    assert isinstance(charts, dict)
    assert "risk_score_ranking" in charts
    assert "source_freshness_table" in charts
    assert data["limit"] == 25


def test_analytics_tables_endpoint_enforces_limit_and_pagination() -> None:
    response = _client().get("/api/v1/analytics/tables?table_id=graph_edges&limit=10&offset=0")
    data = _assert_sanitized_envelope(response.json())

    assert response.status_code == 200
    tables = data["tables"]
    assert isinstance(tables, dict)
    assert "graph_edges" in tables
    assert len(tables["graph_edges"]) <= 10
    assert data["next_offset"] == 10


def test_promoted_graph_additional_views_use_promoted_snapshot(monkeypatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    response = _client().get("/api/v1/graph/geo?limit=20")
    data = _assert_sanitized_envelope(response.json())

    assert response.status_code == 200
    assert data["graph_mode"] == "promoted"
    assert data["data_mode"] == "public_evidence_promoted"
