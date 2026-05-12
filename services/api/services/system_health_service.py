from __future__ import annotations

from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from sra_core.sources import source_registry_readiness
from sra_core.contracts.semiconductor import DEFAULT_SEMIRISK_AS_OF_TIME

from services.api.services.common import (
    semiconductor_default_time,
    semiconductor_fixture_warnings,
)


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
    }


def semiconductor_graph_health_payload() -> dict[str, Any]:
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
            "warnings": [f"fixture_graph_unavailable:{type(exc).__name__}"],
        }
    warnings = semiconductor_fixture_warnings(snapshot)
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
        "warnings": warnings,
    }
