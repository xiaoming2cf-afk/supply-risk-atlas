from __future__ import annotations

from datetime import datetime
from typing import Any

from sra_core.contracts.domain import VersionMetadata
from sra_core.contracts.semiconductor import DEFAULT_SEMIRISK_AS_OF_TIME


def semiconductor_default_time() -> datetime:
    return datetime.fromisoformat(DEFAULT_SEMIRISK_AS_OF_TIME.replace("Z", "+00:00"))


def semiconductor_metadata(
    snapshot: Any | None = None,
    *,
    feature_version: str = "semirisk_features_unavailable",
) -> VersionMetadata:
    graph_version = snapshot.graph_version if snapshot is not None else "semirisk_kg_unavailable"
    source_manifest_id = (
        snapshot.source_manifest_id
        if snapshot is not None
        else "semirisk_fixture_manifest_unavailable"
    )
    as_of_time = snapshot.as_of_time if snapshot is not None else semiconductor_default_time()
    return VersionMetadata(
        graph_version=graph_version,
        feature_version=feature_version,
        label_version="semirisk_labels_unavailable",
        model_version="semirisk_model_unavailable",
        as_of_time=as_of_time,
        audit_ref="semirisk_fixture_graph_v0.1",
        lineage_ref=source_manifest_id,
        data_mode="real",
        freshness_status="partial",
        source_count=4,
        source_manifest_ref=source_manifest_id,
    )


def semiconductor_fixture_warnings(snapshot: Any) -> list[str]:
    warnings = [
        "fixture_graph:not_production_ready",
        (
            "semirisk_fixture_metadata: "
            f"graphVersion={snapshot.graph_version}; "
            f"sourceManifestId={snapshot.source_manifest_id}; "
            f"nodeCount={snapshot.node_count}; "
            f"edgeCount={snapshot.edge_count}; "
            "registryReady=true; "
            "ontologyReady=true; "
            "fixtureGraph: true"
        ),
    ]
    if snapshot.stale_source_count:
        warnings.append(f"fixture_source_freshness_degraded:{snapshot.stale_source_count}")
    if snapshot.missing_provenance_count:
        warnings.append(f"missing_graph_provenance:{snapshot.missing_provenance_count}")
    if snapshot.unresolved_entity_count:
        warnings.append(f"unresolved_graph_entities:{snapshot.unresolved_entity_count}")
    quality_status = (snapshot.quality_report or {}).get("status")
    if quality_status not in {None, "pass"}:
        warnings.append(f"graph_quality_{quality_status}")
    return warnings


def source_ref_ids(refs: Any) -> list[str]:
    ids: list[str] = []
    for ref in refs or []:
        source_id = getattr(ref, "source_id", None)
        if source_id:
            ids.append(str(source_id))
    return sorted(set(ids))

