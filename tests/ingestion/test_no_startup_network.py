from __future__ import annotations

import importlib
import urllib.request


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
