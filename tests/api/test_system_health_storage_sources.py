from __future__ import annotations

import json

from services.api import main


def _response_text(payload: object) -> str:
    return json.dumps(payload, sort_keys=True)


def test_system_health_exposes_storage_source_and_connector_readiness_without_paths() -> None:
    payload = main.route_dashboard_page("system-health-center", request_id="req_health_modes")

    assert payload["status"] == "success"
    data = payload["data"]
    platform = data["platformStatus"]

    assert platform["apiReadiness"] == "ready"
    assert platform["graphReadiness"] in {"ready", "degraded"}
    assert platform["sourceRegistryReadiness"] in {"ready", "degraded", "unavailable"}
    assert platform["connectorReadiness"] in {"ready", "unavailable"}
    assert platform["modelReadiness"] in {"fixture_ready", "unavailable"}
    assert platform["deploymentVersionReadiness"]["status"] in {"reported", "not_verified"}
    assert platform["deploymentVersionReadiness"]["apiVersion"] == "0.1.0"
    assert platform["deploymentVersionReadiness"]["apiGitCommit"]
    assert platform["dataMode"] in {"fixture", "promoted", "live_disabled", "live_enabled"}
    assert platform["graphMode"] in {"fixture", "promoted"}
    assert platform["productionStatus"] in {"research_fixture", "public_evidence_promoted"}
    assert platform["notProductionReady"] is True
    assert "fixture_proxy_not_calibrated" in platform["calibrationStatus"]
    assert "not_financial_loss" in platform["calibrationStatus"]
    assert platform["storageReadiness"]["storageMode"] in {"memory", "sqlite"}
    assert platform["storageReadiness"]["pathRedacted"] is True
    assert platform["storageReadiness"]["path"] == "redacted"
    assert platform["connectorStatusCounts"]
    assert platform["sourceStatusCounts"]
    assert platform["liveDefaultCount"] == 0

    text = _response_text(payload)
    assert "supply_risk_atlas.db" not in text
    assert "data/runtime" not in text.replace("\\", "/")
    assert "Authorization" not in text


def test_system_health_graph_mode_promoted_transparency(monkeypatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    payload = main.route_dashboard_page("system-health-center", request_id="req_health_promoted")
    platform = payload["data"]["platformStatus"]

    assert platform["graphMode"] == "promoted"
    assert platform["dataMode"] == "promoted"
    assert platform["productionStatus"] == "public_evidence_promoted"
    assert platform["notProductionReady"] is True
