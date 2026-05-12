from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api.main import create_app


def test_graph_view_serves_promoted_graph_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")
    app = create_app()
    assert app is not None
    client = TestClient(app)

    response = client.get("/api/v1/graph/view")
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "success"
    assert payload["data"]["graph_mode"] == "promoted"
    assert payload["data"]["data_mode"] == "public_evidence_promoted"
    assert payload["data"]["graph_version"].startswith("promoted_public_evidence_v0_1_")
    assert "promoted_public_evidence:not_production_ready" in payload["warnings"]
