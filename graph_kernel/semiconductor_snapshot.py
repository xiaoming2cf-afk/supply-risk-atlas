from __future__ import annotations

from collections import Counter, deque
from datetime import datetime
from typing import Any

from sra_core.contracts.semiconductor import (
    DEFAULT_SEMIRISK_AS_OF_TIME,
    SEMIRISK_GRAPH_SCHEMA_VERSION,
    SEMIRISK_ONTOLOGY_VERSION,
    SemiconductorPromotionResult,
    SemiriskEdge,
    SemiriskGraphSnapshot,
    SemiriskNode,
    parse_semirisk_time,
    payload_hash,
)
from sra_core.ingestion.semiconductor_promote import promote_semiconductor_fixtures

from .quality import semiconductor_quality_report


def build_semiconductor_fixture_snapshot(
    *,
    as_of_time: datetime | str = DEFAULT_SEMIRISK_AS_OF_TIME,
) -> SemiriskGraphSnapshot:
    promotion = promote_semiconductor_fixtures(as_of_time=as_of_time)
    return build_semiconductor_snapshot(promotion)


def build_semiconductor_snapshot(
    promotion: SemiconductorPromotionResult,
    *,
    ontology_version: str = SEMIRISK_ONTOLOGY_VERSION,
) -> SemiriskGraphSnapshot:
    as_of = promotion.as_of_time
    nodes = sorted(
        [node for node in promotion.graph_nodes if _active(node.valid_from, node.valid_to, as_of)],
        key=lambda item: item.node_id,
    )
    edges = sorted(
        [edge for edge in promotion.graph_edges if _active(edge.valid_from, edge.valid_to, as_of)],
        key=lambda item: edge_sort_key(item),
    )
    quality_basis = {
        "nodes": [node.model_dump(mode="json") for node in nodes],
        "edges": [edge.model_dump(mode="json") for edge in edges],
    }
    quality = semiconductor_quality_report(quality_basis)
    stamp = as_of.strftime("%Y%m%dT%H%M%SZ")
    version_basis = {
        "schema_version": SEMIRISK_GRAPH_SCHEMA_VERSION,
        "ontology_version": ontology_version,
        "source_manifest_id": promotion.source_manifest_id,
        "as_of_time": as_of.isoformat(),
        "nodes": quality_basis["nodes"],
        "edges": quality_basis["edges"],
    }
    graph_version = f"semirisk_kg_v0_1_{stamp}_{payload_hash(version_basis)[:12]}"
    return SemiriskGraphSnapshot(
        graph_version=graph_version,
        ontology_version=ontology_version,
        source_manifest_id=promotion.source_manifest_id,
        as_of_time=as_of,
        node_count=len(nodes),
        edge_count=len(edges),
        node_count_by_type=dict(sorted(Counter(node.node_type for node in nodes).items())),
        edge_count_by_type=dict(sorted(Counter(edge.edge_type for edge in edges).items())),
        missing_provenance_count=quality["missing_provenance_count"],
        unresolved_entity_count=quality["unresolved_entity_count"],
        stale_source_count=int(promotion.source_manifest.get("stale_source_count") or 0),
        nodes=nodes,
        edges=edges,
        quality_report=quality,
    )


def snapshot_payload(snapshot: SemiriskGraphSnapshot) -> dict[str, Any]:
    return snapshot.model_dump(mode="json")


def neighborhood(
    snapshot: SemiriskGraphSnapshot,
    *,
    node_id: str,
    depth: int = 1,
) -> dict[str, Any]:
    depth = max(0, min(depth, 3))
    node_by_id = {node.node_id: node for node in snapshot.nodes}
    if node_id not in node_by_id:
        raise KeyError(f"unknown node_id: {node_id}")
    adjacency: dict[str, list[SemiriskEdge]] = {}
    for edge in snapshot.edges:
        adjacency.setdefault(edge.source_node_id, []).append(edge)
        adjacency.setdefault(edge.target_node_id, []).append(edge)

    visited = {node_id}
    queue: deque[tuple[str, int]] = deque([(node_id, 0)])
    edge_ids: set[str] = set()
    while queue:
        current, distance = queue.popleft()
        if distance >= depth:
            continue
        for edge in adjacency.get(current, []):
            edge_ids.add(edge.edge_id)
            other = edge.target_node_id if edge.source_node_id == current else edge.source_node_id
            if other not in visited:
                visited.add(other)
                queue.append((other, distance + 1))

    edges = [edge for edge in snapshot.edges if edge.edge_id in edge_ids]
    nodes = [node_by_id[node] for node in sorted(visited)]
    return {
        "graph_version": snapshot.graph_version,
        "source_manifest_id": snapshot.source_manifest_id,
        "as_of_time": snapshot.as_of_time.isoformat(),
        "node_id": node_id,
        "depth": depth,
        "nodes": [node.model_dump(mode="json") for node in nodes],
        "edges": [edge.model_dump(mode="json") for edge in edges],
        "warnings": ["fixture_graph:not_production_ready"],
    }


def edge_sort_key(edge: SemiriskEdge) -> tuple[str, str, str, str]:
    return (edge.source_node_id, edge.target_node_id, edge.edge_type, edge.edge_id)


def _active(valid_from: datetime, valid_to: datetime | None, as_of_time: datetime) -> bool:
    return valid_from <= as_of_time and (valid_to is None or as_of_time <= valid_to)
