from __future__ import annotations

from collections import Counter, defaultdict, deque
import os
from typing import Any

from graph_kernel.graph_diff import diff_edge_states
from graph_kernel.path_index import build_path_index
from graph_kernel.semiconductor_snapshot import (
    build_semiconductor_fixture_snapshot,
    neighborhood as semiconductor_neighborhood,
)
from sra_core.api.envelope import make_envelope, make_error_envelope
from sra_core.contracts.domain import VersionMetadata
from sra_core.real_pipeline import real_metadata, run_public_real_pipeline
from services.api.runtime.cache import SnapshotCache
from services.api.services.common import (
    semiconductor_fixture_warnings,
    semiconductor_metadata,
    source_ref_ids,
)


SNAPSHOT_CACHE = SnapshotCache(max_items=8)
GRAPH_VIEW_VERSION = "semirisk_graph_view_v0.1"
OVERVIEW_NODE_CAP = 20
OVERVIEW_EDGE_CAP = 35
FOCUS_NODE_CAP = 25
FOCUS_EDGE_CAP = 40

GRAPH_LAYERS = [
    {"id": "dependency", "label": "Dependency", "default_visible": True},
    {"id": "supply", "label": "Supply", "default_visible": True},
    {"id": "policy", "label": "Policy", "default_visible": True},
    {"id": "event", "label": "Event", "default_visible": True},
    {"id": "substitution", "label": "Substitution", "default_visible": False},
    {"id": "trade", "label": "Trade", "default_visible": True},
    {"id": "route", "label": "Route", "default_visible": True},
    {"id": "simulation_trace", "label": "Simulation trace", "default_visible": False},
]

GRAPH_LEGEND = [
    {"id": "real_edge", "label": "Fixture graph relationship", "semantics": "graph_relationship"},
    {"id": "active_path", "label": "Selected transmission path", "semantics": "path_only"},
    {"id": "cluster", "label": "Aggregated overview cluster", "semantics": "aggregate"},
]


def _build_active_semiconductor_snapshot() -> Any:
    if os.getenv("SUPPLY_RISK_GRAPH_MODE", "fixture").strip().lower() == "promoted":
        from graph_kernel.promoted_pipeline import build_promoted_graph_snapshot

        return build_promoted_graph_snapshot()
    return build_semiconductor_fixture_snapshot()


def metadata_for_result(result: Any) -> VersionMetadata:
    return real_metadata(result)


def route_graph_snapshots(request_id: str | None = None) -> dict[str, Any]:
    result = run_public_real_pipeline()
    as_of_time = result.snapshot.as_of_time.isoformat()

    def build_payload() -> dict[str, Any]:
        paths = build_path_index(result.edge_states)
        return {
            "snapshot": result.snapshot.model_dump(mode="json"),
            "edge_states": [edge.model_dump(mode="json") for edge in result.edge_states],
            "path_index": [path.model_dump(mode="json") for path in paths[:20]],
            "source_manifest": {
                "manifest_ref": result.real.source_manifest_ref,
                "checksum": result.real.source_manifest_checksum,
                "sources": [source.source_id for source in result.real.sources],
                "freshness": [item.as_dict() for item in result.real.freshness],
            },
        }

    return make_envelope(
        SNAPSHOT_CACHE.get_or_set(
            graph_version=result.snapshot.graph_version,
            as_of_time=as_of_time,
            factory=build_payload,
        ),
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_graph_diff(request_id: str | None = None) -> dict[str, Any]:
    earlier = run_public_real_pipeline()
    later = run_public_real_pipeline()
    return make_envelope(
        diff_edge_states(earlier.edge_states, later.edge_states),
        metadata=metadata_for_result(later),
        request_id=request_id,
    )


def route_semiconductor_graph_snapshot(request_id: str | None = None) -> dict[str, Any]:
    try:
        snapshot = _build_active_semiconductor_snapshot()
    except Exception as exc:
        return make_error_envelope(
            "semiconductor_graph_unavailable",
            "SemiRisk-KG fixture graph could not be built.",
            metadata=semiconductor_metadata(),
            request_id=request_id,
            warnings=[f"fixture_graph_build_failed:{type(exc).__name__}"],
        )
    payload = SNAPSHOT_CACHE.get_or_set(
        graph_version=snapshot.graph_version,
        as_of_time=snapshot.as_of_time.isoformat(),
        factory=lambda: snapshot.model_dump(mode="json"),
    )
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_semiconductor_graph_neighborhood(
    node_id: str = "company:tsmc",
    depth: int = 1,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = _build_active_semiconductor_snapshot()
        payload = semiconductor_neighborhood(snapshot, node_id=node_id, depth=depth)
    except KeyError as exc:
        return make_error_envelope(
            "semiconductor_graph_node_not_found",
            str(exc),
            metadata=semiconductor_metadata(),
            request_id=request_id,
            field="node_id",
            warnings=["fixture_graph:not_production_ready"],
        )
    except Exception as exc:
        return make_error_envelope(
            "semiconductor_graph_unavailable",
            "SemiRisk-KG fixture graph neighborhood could not be built.",
            metadata=semiconductor_metadata(),
            request_id=request_id,
            warnings=[f"fixture_graph_build_failed:{type(exc).__name__}"],
        )
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_view(
    mode: str = "overview",
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    selected_nodes = _overview_node_ids(snapshot)
    selected_edges = _edges_between(snapshot, selected_nodes)[:OVERVIEW_EDGE_CAP]
    payload = _view_payload(
        snapshot,
        mode=mode if mode in {"overview", "geo"} else "overview",
        nodes=selected_nodes,
        edges=[edge.edge_id for edge in selected_edges],
        clusters=_clusters(snapshot),
        node_cap=OVERVIEW_NODE_CAP,
        edge_cap=OVERVIEW_EDGE_CAP,
    )
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_focus(
    node_id: str = "company:tsmc",
    depth: int = 1,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    node_ids = {node.node_id for node in snapshot.nodes}
    if node_id not in node_ids:
        return make_error_envelope(
            "semiconductor_graph_node_not_found",
            f"Node not found: {node_id}",
            metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
            request_id=request_id,
            field="node_id",
            warnings=["fixture_graph:not_production_ready"],
        )
    selected_nodes = _focus_node_ids(snapshot, node_id=node_id, depth=max(0, min(depth, 2)))
    selected_edges = _edges_between(snapshot, selected_nodes)[:FOCUS_EDGE_CAP]
    payload = _view_payload(
        snapshot,
        mode="focus",
        nodes=selected_nodes,
        edges=[edge.edge_id for edge in selected_edges],
        clusters=[],
        node_cap=FOCUS_NODE_CAP,
        edge_cap=FOCUS_EDGE_CAP,
        selected_node_id=node_id,
    )
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_clusters(request_id: str | None = None) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    clusters = _clusters(snapshot)
    payload = {
        **_base_view_metadata(snapshot, mode="overview"),
        "nodes": [_cluster_node(cluster) for cluster in clusters[:OVERVIEW_NODE_CAP]],
        "edges": _cluster_edges(snapshot)[:OVERVIEW_EDGE_CAP],
        "clusters": clusters,
        "layout_hints": {
            "mode": "overview",
            "uses_clusters": True,
            "max_nodes": OVERVIEW_NODE_CAP,
            "max_edges": OVERVIEW_EDGE_CAP,
            "edge_labels_visible": False,
        },
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_path_view(
    source_node_id: str = "company:tsmc",
    target_node_id: str = "product_grade:advanced_logic",
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    path_edges = _find_directed_path(snapshot, source_node_id, target_node_id)
    path_node_ids: list[str] = []
    if path_edges:
        path_node_ids.append(path_edges[0].source_node_id)
        path_node_ids.extend(edge.target_node_id for edge in path_edges)
    payload = _view_payload(
        snapshot,
        mode="path",
        nodes=path_node_ids,
        edges=[edge.edge_id for edge in path_edges],
        clusters=[],
        node_cap=max(2, len(path_node_ids)),
        edge_cap=max(1, len(path_edges)),
        selected_node_id=source_node_id,
    )
    payload["path"] = {
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "node_sequence": path_node_ids,
        "edge_sequence": [edge.edge_id for edge in path_edges],
        "evidence_refs": sorted(
            set(ref for edge in path_edges for ref in source_ref_ids(edge.provenance_refs))
        ),
    }
    payload["layout_hints"]["mode"] = "path"
    payload["layout_hints"]["path_only"] = True
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def _base_view_metadata(snapshot: Any, *, mode: str) -> dict[str, Any]:
    graph_mode = getattr(snapshot, "graph_mode", "fixture")
    data_mode = getattr(snapshot, "data_mode", "fixture")
    return {
        "view_version": GRAPH_VIEW_VERSION,
        "mode": mode,
        "graph_version": snapshot.graph_version,
        "source_manifest_id": snapshot.source_manifest_id,
        "as_of_time": snapshot.as_of_time.isoformat(),
        "data_mode": data_mode,
        "graph_mode": graph_mode,
        "layers": GRAPH_LAYERS,
        "legend": GRAPH_LEGEND,
        "warnings": semiconductor_fixture_warnings(snapshot),
        "fixture_limitations": [
            "fixture_graph:not_production_ready",
            "proxy_methodology:not_production_calibrated",
            "raw_payloads_excluded",
        ],
    }


def _view_payload(
    snapshot: Any,
    *,
    mode: str,
    nodes: list[str],
    edges: list[str],
    clusters: list[dict[str, Any]],
    node_cap: int,
    edge_cap: int,
    selected_node_id: str | None = None,
) -> dict[str, Any]:
    node_map = {node.node_id: node for node in snapshot.nodes}
    edge_map = {edge.edge_id: edge for edge in snapshot.edges}
    node_ids = nodes[:node_cap]
    edge_ids = edges[:edge_cap]
    return {
        **_base_view_metadata(snapshot, mode=mode),
        "nodes": [_node_view(node_map[node_id]) for node_id in node_ids if node_id in node_map],
        "edges": [_edge_view(edge_map[edge_id]) for edge_id in edge_ids if edge_id in edge_map],
        "clusters": clusters,
        "layout_hints": {
            "mode": mode,
            "selected_node_id": selected_node_id,
            "max_nodes": node_cap,
            "max_edges": edge_cap,
            "rendered_node_count": len(node_ids),
            "rendered_edge_count": len(edge_ids),
            "edge_labels_visible": False,
            "no_dense_default": True,
        },
    }


def _overview_node_ids(snapshot: Any) -> list[str]:
    degree = Counter()
    for edge in snapshot.edges:
        degree[edge.source_node_id] += 1
        degree[edge.target_node_id] += 1
    ordered = sorted(
        snapshot.nodes,
        key=lambda node: (
            -degree[node.node_id],
            -_node_type_priority(node.node_type),
            node.node_id,
        ),
    )
    return [node.node_id for node in ordered[:OVERVIEW_NODE_CAP]]


def _focus_node_ids(snapshot: Any, *, node_id: str, depth: int) -> list[str]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in snapshot.edges:
        adjacency[edge.source_node_id].add(edge.target_node_id)
        adjacency[edge.target_node_id].add(edge.source_node_id)
    seen = {node_id}
    queue: deque[tuple[str, int]] = deque([(node_id, 0)])
    while queue and len(seen) < FOCUS_NODE_CAP:
        current, current_depth = queue.popleft()
        if current_depth >= depth:
            continue
        for neighbor in sorted(adjacency[current]):
            if neighbor in seen:
                continue
            seen.add(neighbor)
            queue.append((neighbor, current_depth + 1))
            if len(seen) >= FOCUS_NODE_CAP:
                break
    return [node_id, *sorted(seen - {node_id})]


def _edges_between(snapshot: Any, selected_nodes: list[str]) -> list[Any]:
    selected = set(selected_nodes)
    return sorted(
        [
            edge
            for edge in snapshot.edges
            if edge.source_node_id in selected and edge.target_node_id in selected
        ],
        key=lambda edge: (-float(edge.weight), edge.edge_id),
    )


def _find_directed_path(snapshot: Any, source_node_id: str, target_node_id: str) -> list[Any]:
    edges_by_source: dict[str, list[Any]] = defaultdict(list)
    edge_map = {edge.edge_id: edge for edge in snapshot.edges}
    for edge in snapshot.edges:
        edges_by_source[edge.source_node_id].append(edge)
    queue: deque[tuple[str, list[str]]] = deque([(source_node_id, [])])
    seen = {source_node_id}
    while queue:
        node_id, edge_ids = queue.popleft()
        if node_id == target_node_id:
            return [edge_map[edge_id] for edge_id in edge_ids]
        if len(edge_ids) >= 5:
            continue
        for edge in sorted(edges_by_source[node_id], key=lambda item: item.edge_id):
            if edge.target_node_id in seen:
                continue
            seen.add(edge.target_node_id)
            queue.append((edge.target_node_id, [*edge_ids, edge.edge_id]))
    return []


def _clusters(snapshot: Any) -> list[dict[str, Any]]:
    counts = Counter(node.node_type for node in snapshot.nodes)
    return [
        {
            "id": f"cluster:{node_type}",
            "label": node_type.replace("_", " ").title(),
            "node_type": node_type,
            "node_count": count,
            "top_nodes": [
                node.node_id
                for node in sorted(
                    [candidate for candidate in snapshot.nodes if candidate.node_type == node_type],
                    key=lambda candidate: candidate.node_id,
                )[:5]
            ],
        }
        for node_type, count in sorted(counts.items())
    ]


def _cluster_node(cluster: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": cluster["id"],
        "label": cluster["label"],
        "kind": "cluster",
        "node_count": cluster["node_count"],
        "node_type": cluster["node_type"],
        "evidence_refs": [],
    }


def _cluster_edges(snapshot: Any) -> list[dict[str, Any]]:
    node_type_by_id = {node.node_id: node.node_type for node in snapshot.nodes}
    counts: Counter[tuple[str, str, str]] = Counter()
    for edge in snapshot.edges:
        source_type = node_type_by_id.get(edge.source_node_id, "unknown")
        target_type = node_type_by_id.get(edge.target_node_id, "unknown")
        counts[(source_type, target_type, _layer_for_edge(edge.edge_type))] += 1
    return [
        {
            "id": f"cluster-edge:{source_type}:{target_type}:{layer}",
            "source": f"cluster:{source_type}",
            "target": f"cluster:{target_type}",
            "layer": layer,
            "edge_count": count,
            "not_supply_chain_dependency": layer not in {"dependency", "supply"},
        }
        for (source_type, target_type, layer), count in sorted(counts.items())
    ]


def _node_view(node: Any) -> dict[str, Any]:
    attributes = _safe_metadata(node.attributes or {})
    return {
        "id": node.node_id,
        "label": node.canonical_name,
        "kind": node.node_type,
        "country_code": attributes.get("country_code"),
        "confidence": node.confidence,
        "evidence_refs": source_ref_ids(node.source_refs),
        "metadata": attributes,
    }


def _edge_view(edge: Any) -> dict[str, Any]:
    layer = _layer_for_edge(edge.edge_type)
    return {
        "id": edge.edge_id,
        "source": edge.source_node_id,
        "target": edge.target_node_id,
        "edge_type": edge.edge_type,
        "layer": layer,
        "weight": edge.weight,
        "confidence": edge.confidence,
        "evidence_summary": str(edge.evidence_text_summary or "")[:280],
        "evidence_refs": source_ref_ids(edge.provenance_refs),
        "metadata": _safe_metadata(edge.attributes or {}),
        "not_supply_chain_dependency": layer not in {"dependency", "supply"},
        "derived_context": False,
    }


def _safe_metadata(attributes: dict[str, Any]) -> dict[str, Any]:
    blocked_parts = ("raw", "payload", "secret", "token", "private", "cookie", "authorization")
    clean: dict[str, Any] = {}
    for key, value in attributes.items():
        lowered = str(key).lower()
        if any(part in lowered for part in blocked_parts):
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            clean[str(key)] = value
        elif isinstance(value, list):
            clean[str(key)] = [str(item)[:80] for item in value[:10]]
    return clean


def _layer_for_edge(edge_type: str) -> str:
    if edge_type in {"depends_on", "requires"}:
        return "dependency"
    if edge_type in {"supplies", "produces", "participates_in"}:
        return "supply"
    if edge_type in {"restricted_by"}:
        return "policy"
    if edge_type in {"impacted_by", "correlated_with"}:
        return "event"
    if edge_type in {"exports_to", "imports_from"}:
        return "trade"
    if edge_type in {"routes_through", "located_in"}:
        return "route"
    return "substitution"


def _node_type_priority(node_type: str) -> int:
    priorities = {
        "company": 8,
        "facility": 7,
        "product_grade": 6,
        "equipment": 5,
        "process_stage": 4,
        "country": 3,
    }
    return priorities.get(node_type, 1)
