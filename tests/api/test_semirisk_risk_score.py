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
    assert "private_diagnostics" not in text


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


def test_semirisk_entity_risk_route_returns_envelope() -> None:
    payload = main.route_semirisk_entity_risk("company:tsmc", request_id="req_risk_tsmc")

    assert payload["request_id"] == "req_risk_tsmc"
    assert payload["status"] == "success"
    assert payload["source_status"] == "partial"
    assert payload["metadata"]["feature_version"] == "semirisk_risk_score_v0.1"
    assert payload["metadata"]["graph_version"] == payload["data"]["graph_version"]
    assert payload["metadata"]["source_manifest_ref"] == payload["data"]["source_manifest_id"]
    assert payload["data"]["node_id"] == "company:tsmc"
    assert payload["data"]["score"] == 58.33
    assert payload["data"]["level"] == "elevated"
    assert payload["data"]["evidence_refs"]
    assert "fixture_graph:not_production_ready" in payload["warnings"]
    warning_text = " ".join(payload["warnings"])
    assert "semirisk_risk_score_metadata" in warning_text
    assert "company:tsmc" in warning_text
    assert "score=58.33" in warning_text
    assert "level=elevated" in warning_text
    assert "evidence_refs=" in warning_text
    assert "feature_version=semirisk_risk_score_v0.1" in warning_text
    assert f"graph_version={payload['data']['graph_version']}" in warning_text
    assert f"source_manifest_id={payload['data']['source_manifest_id']}" in warning_text
    _assert_no_raw_payload(payload)


def test_semirisk_portfolio_route_is_ranked_and_fixture_labeled() -> None:
    payload = main.route_semirisk_risk_portfolio(
        node_type="company",
        limit=3,
        request_id="req_risk_portfolio",
    )

    assert payload["request_id"] == "req_risk_portfolio"
    assert payload["status"] == "success"
    scores = payload["data"]["scores"]
    assert len(scores) == 3
    assert scores[0]["node_id"] == "company:tsmc"
    assert payload["data"]["fixture_graph"] is True
    assert payload["data"]["feature_version"] == "semirisk_risk_score_v0.1"
    _assert_no_raw_payload(payload)


def test_semirisk_missing_entity_is_controlled_error() -> None:
    payload = main.route_semirisk_entity_risk("company:missing", request_id="req_risk_missing")

    assert payload["request_id"] == "req_risk_missing"
    assert payload["status"] == "error"
    assert payload["errors"][0]["code"] == "semirisk_risk_score_unavailable"
    assert payload["errors"][0]["field"] == "entity_id"
    assert payload["data"] is None
    assert "fixture_graph:not_production_ready" in payload["warnings"]
    _assert_no_raw_payload(payload)


def test_fastapi_risk_endpoints_are_registered() -> None:
    app = main.create_app()
    assert app is not None
    client = TestClient(app)

    entity = client.get("/api/v1/risk/entities/company:tsmc", headers={"x-request-id": "req_http_risk"})
    portfolio = client.get("/api/v1/risk/portfolio?node_type=company&limit=2")

    assert entity.status_code == 200
    assert entity.json()["request_id"] == "req_http_risk"
    assert entity.json()["data"]["node_id"] == "company:tsmc"
    assert portfolio.status_code == 200
    assert portfolio.json()["data"]["scores"][0]["node_id"] == "company:tsmc"
    _assert_no_raw_payload(entity.json())
    _assert_no_raw_payload(portfolio.json())


def test_dev_server_risk_endpoints_are_registered(dev_server_base_url: str) -> None:
    entity_status, entity = _get_json(dev_server_base_url, "/api/v1/risk/entities/company:tsmc")
    portfolio_status, portfolio = _get_json(dev_server_base_url, "/api/v1/risk/portfolio?node_type=company&limit=3")

    assert entity_status == 200
    assert portfolio_status == 200
    assert entity["data"]["node_id"] == "company:tsmc"
    assert entity["data"]["score"] == 58.33
    assert entity["data"]["level"] == "elevated"
    assert portfolio["data"]["scores"][0]["node_id"] == "company:tsmc"
    _assert_no_raw_payload(entity)
    _assert_no_raw_payload(portfolio)
