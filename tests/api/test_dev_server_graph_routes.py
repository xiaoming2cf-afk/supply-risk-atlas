from __future__ import annotations

import json
import socket
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from typing import Any

from services.api.dev_server import Handler


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _fetch_json(base_url: str, path: str) -> dict[str, Any]:
    with urllib.request.urlopen(f"{base_url}{path}", timeout=20) as response:  # noqa: S310
        body = response.read(250_000).decode("utf-8")
    parsed = json.loads(body)
    assert isinstance(parsed, dict)
    return parsed


def test_dev_server_exposes_relationship_graph_routes() -> None:
    port = _free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{port}"
        expected_classes = {
            "/api/v1/graph/supply-relationships?limit=2": "SUPPLY_RELATIONSHIP",
            "/api/v1/graph/demand-relationships?limit=2": "DEMAND_RELATIONSHIP",
            "/api/v1/graph/production-dependencies?limit=2": "PRODUCTION_DEPENDENCY",
        }
        for path, expected_class in expected_classes.items():
            payload = _fetch_json(base_url, path)
            assert payload["status"] == "success"
            assert payload["data"]["relationship_class"] == expected_class
            assert payload["data"]["layout_hints"]["does_not_render_full_graph"] is True
            rendered = json.dumps(payload, sort_keys=True)
            assert "raw_payload" not in rendered
            assert "evidence_context_link" not in rendered

        balance_payload = _fetch_json(base_url, "/api/v1/graph/supply-demand-balance?limit=2")
        assert balance_payload["status"] == "success"
        assert balance_payload["data"]["relationship_class"] == "SUPPLY_DEMAND_BALANCE"
        assert balance_payload["data"]["layout_hints"]["does_not_render_full_graph"] is True
        assert all(row["row_type"] == "aggregate" for row in balance_payload["data"]["balance_rows"])
        assert all(row["not_supply_chain_dependency"] is True for row in balance_payload["data"]["balance_rows"])
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)


def test_dev_server_exposes_stage_graph_and_named_analytics_routes() -> None:
    port = _free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{port}"

        stage_payload = _fetch_json(base_url, "/api/v1/stage-graph/L5_fabrication?limit=5")
        assert stage_payload["status"] == "success"
        assert stage_payload["data"]["stage_id"] == "L5_fabrication"
        assert stage_payload["data"]["source_family_coverage"]

        source_payload = _fetch_json(base_url, "/api/v1/stage-graph/L5_fabrication/source-coverage")
        assert source_payload["status"] == "success"
        assert source_payload["data"]["source_coverage"]

        table_payload = _fetch_json(base_url, "/api/v1/analytics/tables/supply-relationships?limit=2")
        assert table_payload["status"] == "success"
        assert table_payload["data"]["table_id"] == "supply_relationships"

        export_payload = _fetch_json(base_url, "/api/v1/analytics/export/supply-relationships?format=json&limit=2")
        assert export_payload["status"] == "success"
        assert export_payload["data"]["table_id"] == "supply_relationships"
        rendered = json.dumps(export_payload, sort_keys=True)
        assert "raw_payload" not in rendered
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
