from __future__ import annotations

import json

from services.api import main
from services.api.services.system_health_service import platform_status_payload


READY_CONNECTOR_STATUSES = {
    "fixture_connector",
    "promoted_connector",
    "live_connector_available",
}


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
    assert platform["deploymentVersionReadiness"]["status"] in {
        "api_commit_reported",
        "commit_reported",
        "stale_or_unverified",
        "unavailable",
    }
    assert platform["deploymentVersionReadiness"]["apiVersion"] == "0.1.0"
    assert platform["deploymentVersionReadiness"]["apiGitCommit"]
    assert platform["deploymentVersionReadiness"]["deploymentState"] == platform["deploymentVersionReadiness"]["status"]
    assert isinstance(platform["deploymentVersionReadiness"]["staleOrUnverified"], bool)
    assert isinstance(platform["deploymentVersionReadiness"]["unavailable"], bool)
    assert platform["deploymentVersionReadiness"]["lastCheckedAt"]
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
    assert platform["readyConnectorCount"] == sum(
        int(platform["connectorStatusCounts"].get(status) or 0)
        for status in READY_CONNECTOR_STATUSES
    )
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


def test_platform_connector_readiness_counts_only_ready_connector_statuses() -> None:
    graph_health = {
        "status": "ready",
        "graphMode": "fixture",
        "dataMode": "fixture",
        "sourceManifestId": "fixture_manifest",
        "graphVersion": "fixture_graph",
        "warnings": [],
    }
    blocked_registry = {
        "status": "degraded",
        "connector_status_counts": {
            "disabled_review_required": 8,
            "deferred_not_allowed": 3,
            "live_connector_unavailable": 2,
        },
        "source_status_counts": {
            "disabled_review_required": 8,
            "deferred_paid_or_proprietary": 3,
            "unavailable_terms_review": 2,
        },
        "source_count": 13,
        "enabled_count": 0,
        "live_default_count": 0,
        "warnings": [],
    }

    blocked = platform_status_payload(graph_health, blocked_registry)

    assert blocked["connectorReadiness"] == "unavailable"
    assert blocked["readyConnectorCount"] == 0

    ready_registry = {
        **blocked_registry,
        "connector_status_counts": {
            "fixture_connector": 1,
            "promoted_connector": 1,
            "live_connector_available": 1,
            "disabled_review_required": 8,
            "deferred_not_allowed": 3,
        },
    }

    ready = platform_status_payload(graph_health, ready_registry)

    assert ready["connectorReadiness"] == "ready"
    assert ready["readyConnectorCount"] == 3
