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


def _payload(fmt: str = "json") -> dict[str, object]:
    return {"entity_id": "company:tsmc", "include_entity_risk": True, "format": fmt}


def _assert_safe(payload: object) -> None:
    text = json.dumps(payload, sort_keys=True).lower()
    assert '"raw_payload":' not in text
    assert '"private_diagnostics":' not in text
    assert "secret" not in text


def _post_json(base_url: str, path: str, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
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


def test_report_route_generates_json_report() -> None:
    response = main.route_investigation_report(_payload(), request_id="req_report")

    assert response["request_id"] == "req_report"
    assert response["status"] == "success"
    assert response["data"]["report_id"].startswith("report_")
    assert response["data"]["methodology"]["risk_scoring_method"] == "likelihood_impact_vulnerability_framework"
    assert response["data"]["formula_sources"]["formula_refs"]
    assert response["data"]["model_limitations"]
    assert response["data"]["raw_payload_excluded"] is True
    assert response["data"]["private_diagnostics_excluded"] is True
    _assert_safe(response)


def test_fastapi_report_endpoint() -> None:
    app = main.create_app()
    assert app is not None
    client = TestClient(app)

    response = client.post("/api/v1/reports/investigation", json=_payload("markdown"))

    assert response.status_code == 200
    assert response.json()["data"]["format"] == "markdown"
    assert "markdown" in response.json()["data"]
    _assert_safe(response.json())


def test_dev_server_report_endpoint(dev_server_base_url: str) -> None:
    status, body = _post_json(dev_server_base_url, "/api/v1/reports/investigation", _payload())

    assert status == 200
    assert body["status"] == "success"
    assert body["data"]["report_id"].startswith("report_")
    _assert_safe(body)
