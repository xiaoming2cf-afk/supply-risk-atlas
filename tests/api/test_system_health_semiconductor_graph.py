from __future__ import annotations

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from services.api import main
from services.api.dev_server import Handler

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient


def _assert_no_raw_payload(payload: object) -> None:
    text = json.dumps(payload, sort_keys=True)
    assert "raw_payload" not in text
    assert "article body" not in text.lower()


def _get_json(base_url: str, path: str) -> tuple[int, dict[str, object]]:
    with urllib.request.urlopen(f"{base_url}{path}", timeout=10) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


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


def test_fastapi_semiconductor_graph_endpoints_are_registered() -> None:
    app = main.create_app()
    assert app is not None
    client = TestClient(app)

    snapshot = client.get("/api/v1/graph/snapshot", headers={"x-request-id": "req_http_snapshot"})
    neighborhood = client.get(
        "/api/v1/graph/neighborhood?node_id=company:tsmc&depth=1",
        headers={"x-request-id": "req_http_neighborhood"},
    )

    assert snapshot.status_code == 200
    assert snapshot.json()["request_id"] == "req_http_snapshot"
    assert snapshot.json()["data"]["graph_version"].startswith("semirisk_kg_v0_1_")
    assert neighborhood.status_code == 200
    assert neighborhood.json()["request_id"] == "req_http_neighborhood"
    assert neighborhood.json()["data"]["node_id"] == "company:tsmc"


def test_system_health_reports_semiconductor_graph_metadata() -> None:
    payload = main.route_dashboard_page("system-health-center", request_id="req_semirisk_health")

    assert payload["request_id"] == "req_semirisk_health"
    assert payload["status"] == "success"
    graph = payload["data"]["semiconductorGraph"]
    assert graph["label"] == "SemiRisk-KG v0.1 fixture graph"
    assert graph["fixtureGraph"] is True
    assert graph["graphVersion"].startswith("semirisk_kg_v0_1_")
    assert graph["sourceManifestId"].startswith("semirisk_fixture_manifest_")
    assert graph["nodeCount"] >= 20
    assert graph["edgeCount"] >= 30
    assert graph["registryReady"] is True
    assert graph["ontologyReady"] is True
    assert graph["fixtureGraphReady"] is True
    assert "fixture_graph:not_production_ready" in graph["warnings"]
    warning_text = " ".join(graph["warnings"])
    assert "graphVersion" in warning_text
    assert graph["graphVersion"] in warning_text
    assert "sourceManifestId" in warning_text
    assert graph["sourceManifestId"] in warning_text
    assert "nodeCount" in warning_text
    assert "edgeCount" in warning_text
    assert "registryReady=true" in warning_text
    assert "ontologyReady=true" in warning_text
    assert "fixtureGraph: true" in warning_text
    readiness = payload["data"]["sourceRegistryReadiness"]
    assert readiness["registry_version"] == "semiconductor-source-registry-v0.2"
    assert readiness["source_count"] == 23
    assert readiness["enabled_count"] == 4
    assert readiness["live_default_count"] == 0
    assert readiness["connector_status_counts"]["fixture_connector"] == 4
    assert "live_fetch_disabled_by_default" in readiness["warnings"]
    _assert_no_raw_payload(payload)


def test_semiconductor_graph_snapshot_endpoint_returns_envelope() -> None:
    payload = main.route_semiconductor_graph_snapshot(request_id="req_semirisk_snapshot")

    assert payload["request_id"] == "req_semirisk_snapshot"
    assert payload["status"] == "success"
    assert payload["source_status"] == "partial"
    assert payload["metadata"]["graph_version"] == payload["data"]["graph_version"]
    assert payload["metadata"]["source_manifest_ref"] == payload["data"]["source_manifest_id"]
    assert payload["data"]["node_count"] >= 20
    assert payload["data"]["edge_count"] >= 30
    _assert_no_raw_payload(payload)


def test_semiconductor_graph_neighborhood_endpoint_returns_neighbors() -> None:
    payload = main.route_semiconductor_graph_neighborhood(
        node_id="company:tsmc",
        depth=1,
        request_id="req_semirisk_neighborhood",
    )

    assert payload["request_id"] == "req_semirisk_neighborhood"
    assert payload["status"] == "success"
    assert payload["metadata"]["graph_version"] == payload["data"]["graph_version"]
    assert payload["data"]["node_id"] == "company:tsmc"
    assert any(node["node_id"] == "company:tsmc" for node in payload["data"]["nodes"])
    assert payload["data"]["edges"]
    _assert_no_raw_payload(payload)


def test_semiconductor_graph_neighborhood_missing_node_is_explicit_error() -> None:
    payload = main.route_semiconductor_graph_neighborhood(
        node_id="company:missing",
        request_id="req_semirisk_missing",
    )

    assert payload["request_id"] == "req_semirisk_missing"
    assert payload["status"] == "error"
    assert payload["errors"][0]["code"] == "semiconductor_graph_node_not_found"
    assert payload["warnings"] == ["fixture_graph:not_production_ready"]


def test_dev_server_semirisk_graph_and_health_routes(dev_server_base_url: str) -> None:
    health_status, health = _get_json(dev_server_base_url, "/api/v1/dashboard/system-health-center")
    snapshot_status, snapshot = _get_json(dev_server_base_url, "/api/v1/graph/snapshot")
    neighborhood_status, neighborhood = _get_json(
        dev_server_base_url,
        "/api/v1/graph/neighborhood?node_id=company:tsmc&depth=1",
    )

    assert health_status == 200
    assert snapshot_status == 200
    assert neighborhood_status == 200
    assert health["data"]["semiconductorGraph"]["graphVersion"].startswith("semirisk_kg_v0_1_")
    assert snapshot["data"]["graph_version"] == health["data"]["semiconductorGraph"]["graphVersion"]
    assert neighborhood["data"]["node_id"] == "company:tsmc"
    _assert_no_raw_payload(health)
    _assert_no_raw_payload(snapshot)
    _assert_no_raw_payload(neighborhood)
