from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api import main
from services.api.security.headers import cors_origins


def test_security_headers_are_present_on_api_response() -> None:
    app = main.create_app()
    assert app is not None
    response = TestClient(app).get("/api/v1/health")

    assert response.headers["content-security-policy"]
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["cross-origin-opener-policy"] == "same-origin"


def test_production_cors_defaults_do_not_use_wildcard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_ENV", "production")
    monkeypatch.delenv("SUPPLY_RISK_CORS_ORIGINS", raising=False)

    assert cors_origins() == ["https://supply-risk-atlas-web.onrender.com"]


def test_configured_cors_origins_are_used(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_CORS_ORIGINS", "https://example.test, https://web.example.test")

    assert cors_origins() == ["https://example.test", "https://web.example.test"]
