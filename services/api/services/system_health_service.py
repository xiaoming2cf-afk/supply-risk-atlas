from __future__ import annotations

import os
from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from sra_core.sources import source_registry_readiness
from sra_core.contracts.semiconductor import DEFAULT_SEMIRISK_AS_OF_TIME

from services.api.storage.sqlite_store import configured_storage_mode
from services.api.services.common import (
    semiconductor_default_time,
    semiconductor_fixture_warnings,
)
from services.api.services.version_service import build_version_payload


def source_registry_readiness_payload() -> dict[str, Any]:
    try:
        return source_registry_readiness()
    except Exception as exc:
        return {
            "registry_version": "unavailable",
            "generated_at": None,
            "status": "unavailable",
            "source_count": 0,
            "enabled_count": 0,
            "disabled_count": 0,
            "live_default_count": 0,
            "terms_review_count": 0,
            "deferred_count": 0,
            "source_status_counts": {},
            "connector_status_counts": {},
            "source_tier_counts": {},
            "sources": [],
            "warnings": [f"source_registry_unavailable:{type(exc).__name__}"],
        }


def semiconductor_only_system_health_payload(exc: Exception) -> dict[str, Any]:
    graph_health = semiconductor_graph_health_payload()
    registry_readiness = source_registry_readiness_payload()
    platform_status = platform_status_payload(graph_health, registry_readiness)
    now = semiconductor_default_time().isoformat()
    return {
        "services": [
            {
                "id": "semirisk-fixture-graph",
                "service": "SemiRisk-KG fixture graph",
                "owner": "platform",
                "status": "degraded" if graph_health["status"] != "unavailable" else "down",
                "latencyMs": 0,
                "freshnessMinutes": 0,
                "errorRate": 0.0 if graph_health["status"] != "unavailable" else 1.0,
            },
            {
                "id": "public-real-pipeline",
                "service": "Public evidence graph pipeline",
                "owner": "platform",
                "status": "down",
                "latencyMs": 0,
                "freshnessMinutes": 0,
                "errorRate": 1.0,
            },
        ],
        "stages": [
            {
                "id": "stage-semiconductor-fixture",
                "label": "SemiRisk fixture graph build",
                "status": "complete" if graph_health["status"] != "unavailable" else "blocked",
                "processed": 1 if graph_health["status"] != "unavailable" else 0,
                "total": 1,
            },
            {
                "id": "stage-public-real",
                "label": "Public evidence graph pipeline",
                "status": "blocked",
                "processed": 0,
                "total": 1,
            },
        ],
        "logs": [
            f"{now} semirisk fixture graph readiness returned while public pipeline was unavailable",
            f"{now} public_real_pipeline_unavailable:{type(exc).__name__}",
        ],
        "sourceRegistry": {
            "manifestRef": graph_health["sourceManifestId"],
            "checksum": graph_health["sourceManifestId"],
            "asOfTime": now,
            "catalogSource": "semirisk_fixture_graph",
            "promotedGraph": {"status": "partial", "manifest": None},
            "sourceCount": 0,
            "rawRecordCount": 0,
            "silverEntityCount": 0,
            "silverEventCount": 0,
            "goldEdgeEventCount": 0,
            "dataNodeCount": 0,
            "sources": [],
        },
        "sourceRegistryReadiness": source_registry_readiness_payload(),
        "entityResolution": {
            "totalEntities": 0,
            "averageConfidence": 0.0,
            "byEntityType": [],
            "bySource": [],
        },
        "evidenceLineage": {
            "manifestRef": graph_health["sourceManifestId"],
            "checksum": graph_health["sourceManifestId"],
            "asOfTime": now,
            "rawRecordCount": 0,
            "silverEventCount": 0,
            "goldEdgeEventCount": 0,
            "records": [],
        },
        "semiconductorGraph": graph_health,
        "platformStatus": platform_status,
    }


def semiconductor_graph_health_payload() -> dict[str, Any]:
    graph_mode = configured_graph_mode()
    data_mode = configured_data_mode(graph_mode)
    production_status = production_status_for_mode(graph_mode)
    try:
        snapshot = build_semiconductor_fixture_snapshot()
    except Exception as exc:
        return {
            "label": "SemiRisk-KG v0.1 fixture graph",
            "status": "unavailable",
            "fixtureGraph": True,
            "registryReady": False,
            "ontologyReady": False,
            "fixtureManifestReady": False,
            "fixtureGraphReady": False,
            "graphVersion": "unavailable",
            "ontologyVersion": "unavailable",
            "sourceManifestId": "unavailable",
            "asOfTime": DEFAULT_SEMIRISK_AS_OF_TIME,
            "nodeCount": 0,
            "edgeCount": 0,
            "nodeCountByType": {},
            "edgeCountByType": {},
            "missingProvenanceCount": 0,
            "unresolvedEntityCount": 0,
            "staleSourceCount": 0,
            "dataMode": data_mode,
            "graphMode": graph_mode,
            "productionStatus": production_status,
            "notProductionReady": True,
            "calibrationStatus": "fixture_proxy_not_calibrated;not_financial_loss",
            "warnings": [
                f"fixture_graph_unavailable:{type(exc).__name__}",
                "not_production_ready",
                "calibration_status:fixture_proxy_not_calibrated",
                "calibration_status:not_financial_loss",
            ],
        }
    warnings = semiconductor_fixture_warnings(snapshot)
    env_graph_mode = configured_graph_mode()
    snapshot_graph_mode = getattr(snapshot, "graph_mode", graph_mode)
    graph_mode = "promoted" if env_graph_mode == "promoted" else snapshot_graph_mode
    data_mode = configured_data_mode(graph_mode, getattr(snapshot, "data_mode", None))
    production_status = production_status_for_mode(graph_mode)
    return {
        "label": "SemiRisk-KG v0.1 fixture graph",
        "status": "ready"
        if snapshot.quality_report.get("status") == "pass" and snapshot.stale_source_count == 0
        else "degraded",
        "fixtureGraph": True,
        "registryReady": True,
        "ontologyReady": True,
        "fixtureManifestReady": True,
        "fixtureGraphReady": True,
        "graphVersion": snapshot.graph_version,
        "ontologyVersion": snapshot.ontology_version,
        "sourceManifestId": snapshot.source_manifest_id,
        "asOfTime": snapshot.as_of_time.isoformat(),
        "nodeCount": snapshot.node_count,
        "edgeCount": snapshot.edge_count,
        "nodeCountByType": snapshot.node_count_by_type,
        "edgeCountByType": snapshot.edge_count_by_type,
        "missingProvenanceCount": snapshot.missing_provenance_count,
        "unresolvedEntityCount": snapshot.unresolved_entity_count,
        "staleSourceCount": snapshot.stale_source_count,
        "dataMode": data_mode,
        "graphMode": graph_mode,
        "productionStatus": production_status,
        "notProductionReady": True,
        "calibrationStatus": "fixture_proxy_not_calibrated;not_financial_loss",
        "warnings": warnings,
    }


def configured_graph_mode() -> str:
    mode = os.getenv("SUPPLY_RISK_GRAPH_MODE", "fixture").strip().lower()
    return mode if mode in {"fixture", "promoted"} else "fixture"


def configured_data_mode(graph_mode: str, snapshot_data_mode: str | None = None) -> str:
    explicit = os.getenv("SUPPLY_RISK_DATA_MODE", "").strip().lower()
    allowed = {"fixture", "promoted", "live_disabled", "live_enabled", "public_evidence_promoted"}
    if explicit in allowed:
        return "promoted" if explicit == "public_evidence_promoted" else explicit
    if snapshot_data_mode == "public_evidence_promoted":
        return "promoted"
    if snapshot_data_mode in allowed:
        return snapshot_data_mode
    if graph_mode == "promoted":
        return "promoted"
    return "fixture"


def production_status_for_mode(graph_mode: str) -> str:
    return "public_evidence_promoted" if graph_mode == "promoted" else "research_fixture"


def platform_status_payload(
    graph_health: dict[str, Any] | None = None,
    registry_readiness: dict[str, Any] | None = None,
) -> dict[str, Any]:
    graph_health = graph_health or semiconductor_graph_health_payload()
    registry_readiness = registry_readiness or source_registry_readiness_payload()
    graph_mode = str(graph_health.get("graphMode") or configured_graph_mode())
    data_mode = configured_data_mode(graph_mode, str(graph_health.get("dataMode") or ""))
    storage_mode = configured_storage_mode()
    connector_counts = registry_readiness.get("connector_status_counts", {})
    enabled_connectors = sum(int(value) for value in connector_counts.values()) if isinstance(connector_counts, dict) else 0
    live_default_count = int(registry_readiness.get("live_default_count") or 0)
    registry_status = str(registry_readiness.get("status") or "unavailable")
    graph_status = str(graph_health.get("status") or "unavailable")
    version = build_version_payload()

    warnings = [
        "not_production_ready",
        "fixture_proxy_not_calibrated",
        "not_financial_loss",
        "storage_path_redacted",
        "live_fetch_disabled_by_default",
    ]
    warnings.extend(str(warning) for warning in graph_health.get("warnings", []) if warning)
    warnings.extend(str(warning) for warning in registry_readiness.get("warnings", []) if warning)
    warnings.extend(str(warning) for warning in version.get("warnings", []) if warning)

    return {
        "apiReadiness": "ready",
        "graphReadiness": "ready" if graph_status == "ready" else "degraded",
        "sourceRegistryReadiness": registry_status,
        "connectorReadiness": "ready" if enabled_connectors > 0 else "unavailable",
        "storageReadiness": {
            "status": "ready" if storage_mode == "sqlite" else "memory_fallback",
            "storageMode": storage_mode,
            "pathRedacted": True,
            "path": "redacted",
        },
        "modelReadiness": "fixture_ready" if graph_status != "unavailable" else "unavailable",
        "deploymentVersionReadiness": {
            "status": "reported" if version["git_commit"] != "unknown" else "not_verified",
            "apiVersion": str(version["app_version"]),
            "apiGitCommit": str(version.get("api_commit") or version["git_commit"]),
            "apiBuildTime": str(version["build_time"]),
            "webVersion": "not_verified",
            "webGitCommit": str(version.get("web_commit") or "not_verified"),
            "commitMismatch": bool(version.get("commit_mismatch")),
            "environment": str(version["environment"]),
            "warnings": version["warnings"],
        },
        "dataMode": data_mode,
        "graphMode": graph_mode,
        "productionStatus": production_status_for_mode(graph_mode),
        "notProductionReady": True,
        "calibrationStatus": ["fixture_proxy_not_calibrated", "not_financial_loss"],
        "sourceManifestId": str(graph_health.get("sourceManifestId") or "unavailable"),
        "graphVersion": str(graph_health.get("graphVersion") or "unavailable"),
        "connectorStatusCounts": connector_counts if isinstance(connector_counts, dict) else {},
        "sourceStatusCounts": registry_readiness.get("source_status_counts", {}),
        "sourceCount": int(registry_readiness.get("source_count") or 0),
        "enabledSourceCount": int(registry_readiness.get("enabled_count") or 0),
        "liveDefaultCount": live_default_count,
        "warnings": sorted(set(warnings)),
    }
