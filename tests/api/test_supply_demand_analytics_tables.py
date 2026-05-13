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


def _assert_table_payload(payload: dict[str, object]) -> dict[str, object]:
    assert payload["status"] == "success"
    data = payload["data"]
    assert isinstance(data, dict)
    for key in ("graph_version", "source_manifest_id", "data_mode", "graph_mode", "rows"):
        assert key in data
    rendered = json.dumps(payload, sort_keys=True).lower()
    assert "raw_payload" not in rendered
    assert "authorization" not in rendered
    assert "api_key" not in rendered
    return data


@pytest.mark.parametrize(
    "table_id",
    [
        "supply-relationships",
        "demand-relationships",
        "production-dependencies",
        "supplier-concentration",
        "product-demand",
        "critical-inputs",
        "supply-demand-balance",
    ],
)
def test_supply_demand_analytics_tables_are_bounded_and_sanitized(
    monkeypatch: pytest.MonkeyPatch,
    table_id: str,
) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    response = _client().get(f"/api/v1/analytics/tables/{table_id}?limit=20&offset=0")
    data = _assert_table_payload(response.json())

    assert response.status_code == 200
    assert len(data["rows"]) <= 20
    assert data["limit"] == 20
    assert data["next_offset"] == 20


def test_supply_demand_analytics_export_is_bounded_and_sanitized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    response = _client().get("/api/v1/analytics/export/supply-demand-balance?format=json&limit=20")
    payload = response.json()
    data = payload["data"]

    assert response.status_code == 200
    assert payload["status"] == "success"
    assert data["table_id"] == "supply_demand_balance"
    assert data["row_count"] <= 20
    assert "raw_payload" not in json.dumps(payload, sort_keys=True).lower()
