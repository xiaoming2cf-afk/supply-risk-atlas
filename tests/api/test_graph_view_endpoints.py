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


def _assert_view_shape(payload: dict[str, object]) -> dict[str, object]:
    assert payload["status"] == "success"
    data = payload["data"]
    assert isinstance(data, dict)
    for key in (
        "nodes",
        "edges",
        "layout_hints",
        "layers",
        "legend",
        "graph_version",
        "source_manifest_id",
        "warnings",
    ):
        assert key in data
    assert data["graph_version"]
    assert data["source_manifest_id"]
    return data


def test_graph_view_endpoint_returns_capped_sanitized_overview() -> None:
    client = _client()

    response = client.get("/api/v1/graph/view", headers={"x-request-id": "req_graph_view"})
    payload = response.json()
    data = _assert_view_shape(payload)

    assert response.status_code == 200
    assert payload["request_id"] == "req_graph_view"
    assert len(data["nodes"]) <= 20
    assert len(data["edges"]) <= 35
    assert data["layout_hints"]["edge_labels_visible"] is False
    assert any(layer["id"] == "dependency" for layer in data["layers"])
    rendered = json.dumps(payload, sort_keys=True).lower()
    assert "raw_id" not in rendered
    assert "payload_hash" not in rendered
    assert "private_diagnostic" not in rendered
    assert "secret" not in rendered


def test_graph_focus_endpoint_returns_selected_node_with_cap() -> None:
    client = _client()

    response = client.get("/api/v1/graph/focus?node_id=company:tsmc&depth=2")
    data = _assert_view_shape(response.json())

    assert response.status_code == 200
    assert len(data["nodes"]) <= 25
    assert len(data["edges"]) <= 40
    assert data["layout_hints"]["selected_node_id"] == "company:tsmc"
    assert any(node["id"] == "company:tsmc" for node in data["nodes"])


def test_graph_clusters_endpoint_returns_aggregates_not_dense_graph() -> None:
    client = _client()

    response = client.get("/api/v1/graph/clusters")
    data = _assert_view_shape(response.json())

    assert response.status_code == 200
    assert data["clusters"]
    assert len(data["nodes"]) <= 20
    assert len(data["edges"]) <= 35
    assert data["layout_hints"]["uses_clusters"] is True


def test_graph_path_view_only_returns_path_nodes_and_edges() -> None:
    client = _client()

    response = client.get(
        "/api/v1/graph/path-view?source_node_id=company:tsmc&target_node_id=product_grade:advanced_logic"
    )
    data = _assert_view_shape(response.json())

    assert response.status_code == 200
    assert data["path"]["node_sequence"] == ["company:tsmc", "product_grade:advanced_logic"]
    assert data["path"]["edge_sequence"] == ["edge:tsmc:produces:advanced_logic"]
    assert {edge["id"] for edge in data["edges"]} == set(data["path"]["edge_sequence"])
    assert {node["id"] for node in data["nodes"]} == set(data["path"]["node_sequence"])
    assert all(edge.get("derived_context") is False for edge in data["edges"])
    assert all(not str(edge["id"]).startswith("search-context") for edge in data["edges"])

