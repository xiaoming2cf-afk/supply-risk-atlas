from __future__ import annotations

import importlib

import pytest

from sra_core.ingestion.connectors.base import ConnectorRequest, PublicEvidenceConnector
from sra_core.ingestion.connectors.errors import ConnectorPolicyError, ConnectorUnavailableError


def _request(mode: str, fixture_payload: dict[str, object] | None = None) -> ConnectorRequest:
    return ConnectorRequest(
        source_id="test_source",
        source_url="https://example.org/source",
        provenance_url="https://example.org/provenance",
        license_ref="https://example.org/terms",
        mode=mode,  # type: ignore[arg-type]
        fixture_payload=fixture_payload,
    )


def test_connector_import_does_not_fetch_network(monkeypatch) -> None:
    called = False

    def fail_fetch(*args, **kwargs):  # pragma: no cover - should never run
        nonlocal called
        called = True
        raise AssertionError("network fetch should not run during import")

    monkeypatch.setattr("urllib.request.urlopen", fail_fetch)
    importlib.reload(importlib.import_module("sra_core.ingestion.connectors.base"))

    assert called is False


def test_connector_fixture_dry_run_and_unavailable_modes() -> None:
    connector = PublicEvidenceConnector("test_source")

    fixture = connector.fetch(_request("fixture", {"hello": "world"}))
    dry_run = connector.fetch(_request("dry_run"))
    unavailable = connector.fetch(_request("unavailable"))

    assert fixture.status == "fixture"
    assert fixture.payload == {"hello": "world"}
    assert fixture.metadata()["raw_payload_stored"] is False
    assert dry_run.status == "dry_run"
    assert dry_run.payload is None
    assert unavailable.status == "unavailable"


def test_connector_live_mode_is_disabled_by_default() -> None:
    connector = PublicEvidenceConnector("test_source")

    with pytest.raises(ConnectorUnavailableError):
        connector.fetch(_request("live"))


def test_connector_rejects_unbounded_request() -> None:
    connector = PublicEvidenceConnector("test_source")
    request = ConnectorRequest(
        source_id="test_source",
        source_url="https://example.org/source",
        provenance_url="https://example.org/provenance",
        license_ref="https://example.org/terms",
        mode="dry_run",
        timeout_seconds=120,
    )

    with pytest.raises(ConnectorPolicyError):
        connector.fetch(request)

