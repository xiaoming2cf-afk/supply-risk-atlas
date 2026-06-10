from __future__ import annotations

import importlib
import urllib.request

import pytest


def test_connector_imports_do_not_open_network(monkeypatch) -> None:
    calls: list[object] = []

    def fail_urlopen(*args, **kwargs):  # pragma: no cover - should never be reached
        calls.append((args, kwargs))
        raise AssertionError("network call during connector import")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)

    importlib.import_module("sra_core.ingestion.connectors.base")
    importlib.import_module("sra_core.ingestion.connectors.http_client")
    importlib.import_module("sra_core.ingestion.connectors.cache")
    importlib.import_module("sra_core.ingestion.connectors.rate_limit")

    assert calls == []


def test_connector_instantiation_does_not_open_network(monkeypatch) -> None:
    calls: list[object] = []

    def fail_urlopen(*args, **kwargs):  # pragma: no cover - should never be reached
        calls.append((args, kwargs))
        raise AssertionError("network call during connector init")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)

    from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector

    PublicEvidenceConnector("sec_edgar_lite", config=ConnectorConfig(mode="live_disabled"))

    assert calls == []


def test_api_app_startup_and_health_do_not_open_network(monkeypatch) -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    calls: list[object] = []

    def fail_urlopen(*args, **kwargs):  # pragma: no cover - should never be reached
        calls.append((args, kwargs))
        raise AssertionError("network call during API startup or health request")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)
    monkeypatch.setenv("SUPPLY_RISK_DATA_MODE", "live_enabled")
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    from services.api import main

    app = main.create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        system_response = client.get("/api/v1/system-health")

    assert response.status_code == 200
    assert system_response.status_code == 200
    platform = system_response.json()["data"]["platformStatus"]
    assert platform["requestedDataMode"] == "live_enabled"
    assert platform["dataMode"] == "promoted"
    assert platform["liveFetchRequested"] is True
    assert platform["liveFetchEffective"] is False
    assert platform["liveDefaultCount"] == 0
    assert "live_fetch_requested_but_disabled_by_registry_defaults" in platform["warnings"]
    assert calls == []
