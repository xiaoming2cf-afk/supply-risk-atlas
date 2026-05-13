from __future__ import annotations

from collections import Counter, defaultdict, deque
import os
from pathlib import Path
from typing import Any

import yaml

from graph_kernel.graph_diff import diff_edge_states
from graph_kernel.path_index import build_path_index
from graph_kernel.promoted_graph_quality import node_catalog_coverage, source_coverage
from graph_kernel.relationship_builder import (
    DEMAND_RELATIONSHIP_CLASS,
    EVIDENCE_RELATIONSHIP_CLASS,
    PRODUCTION_DEPENDENCY_CLASS,
    SUPPLY_RELATIONSHIP_CLASS,
    classify_edge,
    normalize_relationship_edge,
)
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
    {"id": "hazard", "label": "Hazard", "default_visible": True},
    {"id": "sanctions", "label": "Sanctions", "default_visible": False},
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
    relationship_class: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    selected_nodes = _overview_node_ids(snapshot)
    selected_edges = _filter_edges_by_relationship_class(
        _edges_between(snapshot, selected_nodes),
        relationship_class,
    )[:OVERVIEW_EDGE_CAP]
    payload = _view_payload(
        snapshot,
        mode=mode if mode in {"overview", "geo"} else "overview",
        nodes=selected_nodes,
        edges=[edge.edge_id for edge in selected_edges],
        clusters=_clusters(snapshot),
        node_cap=OVERVIEW_NODE_CAP,
        edge_cap=OVERVIEW_EDGE_CAP,
    )
    if relationship_class:
        payload["relationship_class_filter"] = relationship_class
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_focus(
    node_id: str = "company:tsmc",
    depth: int = 1,
    relationship_class: str | None = None,
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
    selected_edges = _filter_edges_by_relationship_class(
        _edges_between(snapshot, selected_nodes),
        relationship_class,
    )[:FOCUS_EDGE_CAP]
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
    if relationship_class:
        payload["relationship_class_filter"] = relationship_class
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


def route_graph_timeline(
    limit: int = 50,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    rows = []
    for node in snapshot.nodes:
        if node.node_type not in {"risk_event", "hazard_event", "policy_event", "sanctions_event"}:
            continue
        rows.append(
            {
                "node_id": node.node_id,
                "label": node.canonical_name,
                "event_type": node.node_type,
                "event_time": node.valid_from.isoformat(),
                "affected_nodes": _neighbors_for_node(snapshot, node.node_id)[:10],
                "evidence_refs": source_ref_ids(node.source_refs),
            }
        )
    payload = {
        **_base_view_metadata(snapshot, mode="timeline"),
        "events": rows[: _bounded_limit(limit)],
        "layout_hints": {"mode": "timeline", "max_events": _bounded_limit(limit)},
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_geo(
    limit: int = 50,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    countries = [node for node in snapshot.nodes if node.node_type == "country"]
    country_ids = {node.node_id for node in countries}
    edges = [
        edge
        for edge in snapshot.edges
        if edge.source_node_id in country_ids or edge.target_node_id in country_ids
    ]
    payload = {
        **_base_view_metadata(snapshot, mode="geo"),
        "countries": [_node_view(node) for node in countries[: _bounded_limit(limit)]],
        "cross_border_edges": [_edge_view(edge) for edge in edges[: _bounded_limit(limit)]],
        "concentration_metrics": _concentration_metrics(snapshot),
        "layout_hints": {"mode": "geo", "aggregate_by": "country_region"},
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_matrix(
    limit: int = 50,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    node_ids = [node.node_id for node in snapshot.nodes[: _bounded_limit(limit)]]
    node_set = set(node_ids)
    adjacency = [
        {
            "source": edge.source_node_id,
            "target": edge.target_node_id,
            "edge_type": edge.edge_type,
            "weight": edge.weight,
            "confidence": edge.confidence,
        }
        for edge in snapshot.edges
        if edge.source_node_id in node_set and edge.target_node_id in node_set
    ][:_bounded_limit(limit)]
    payload = {
        **_base_view_metadata(snapshot, mode="matrix"),
        "nodes": node_ids,
        "adjacency_matrix": adjacency,
        "dependency_matrix": [row for row in adjacency if row["edge_type"] in {"depends_on", "requires"}],
        "trade_concentration_matrix": [
            row for row in adjacency if row["edge_type"] == "trade_dependency_edge"
        ],
        "policy_exposure_matrix": [
            row for row in adjacency if row["edge_type"] == "policy_restriction_edge"
        ],
        "layout_hints": {"mode": "matrix", "max_nodes": _bounded_limit(limit)},
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_layers(request_id: str | None = None) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    counts = Counter(_layer_for_edge(edge.edge_type) for edge in snapshot.edges)
    payload = {
        **_base_view_metadata(snapshot, mode="layers"),
        "layers": [{**layer, "edge_count": counts.get(layer["id"], 0)} for layer in GRAPH_LAYERS],
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_evidence(
    limit: int = 50,
    source_id: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    rows: list[dict[str, Any]] = []
    for edge in snapshot.edges:
        refs = source_ref_ids(edge.provenance_refs)
        if source_id and source_id not in refs:
            continue
        rows.append(
            {
                "edge_id": edge.edge_id,
                "source_id": refs[0] if refs else "unknown",
                "source_refs": refs,
                "confidence": edge.confidence,
                "evidence_summary": str(edge.evidence_text_summary or "")[:280],
                "provenance_url": None,
                "edge_type": edge.edge_type,
            }
        )
    payload = {
        **_base_view_metadata(snapshot, mode="evidence"),
        "evidence_refs": rows[: _bounded_limit(limit)],
        "limit": _bounded_limit(limit),
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_scenario_overlay(
    run_id: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    payload = {
        **_base_view_metadata(snapshot, mode="scenario-overlay"),
        "run_id": run_id,
        "simulation_version": "semirisk_simulation_overlay_v0.1",
        "affected_nodes": [],
        "affected_paths": [],
        "loss_contributions": [],
        "status": "no_selected_run" if not run_id else "run_not_loaded",
        "warnings": [*semiconductor_fixture_warnings(snapshot), "scenario_overlay_requires_selected_run"],
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=payload["warnings"],
    )


def route_graph_node_catalog(
    limit: int = 50,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    rows = _node_catalog_rows(limit=_bounded_limit(limit))
    payload = {
        **_base_view_metadata(snapshot, mode="node-catalog"),
        "node_catalog": rows,
        "limit": _bounded_limit(limit),
        "layout_hints": {
            "mode": "node-catalog",
            "table_only": True,
            "does_not_render_full_graph": True,
        },
        "evidence_refs": sorted(
            {
                source_id
                for row in rows
                for source_id in row.get("source_candidates", [])
            }
        ),
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_graph_source_coverage(
    limit: int = 50,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    nodes = [node.model_dump(mode="json") for node in snapshot.nodes]
    edges = [edge.model_dump(mode="json") for edge in snapshot.edges]
    coverage = source_coverage(nodes, edges)
    catalog_coverage = node_catalog_coverage(nodes)
    rows = [
        {
            "source_id": source_id,
            "reference_count": count,
        }
        for source_id, count in sorted(
            coverage.get("counts_by_source_id", {}).items(),
            key=lambda item: (-int(item[1]), str(item[0])),
        )
    ][: _bounded_limit(limit)]
    payload = {
        **_base_view_metadata(snapshot, mode="source-coverage"),
        "source_coverage": {
            **coverage,
            "rows": rows,
            "node_catalog_coverage": {
                "catalog_version": catalog_coverage["catalog_version"],
                "status": catalog_coverage["status"],
                "catalog_node_count": catalog_coverage["catalog_node_count"],
                "covered_catalog_node_count": catalog_coverage["covered_catalog_node_count"],
                "coverage_ratio": catalog_coverage["coverage_ratio"],
                "warnings": catalog_coverage["warnings"],
            },
        },
        "limit": _bounded_limit(limit),
        "layout_hints": {
            "mode": "source-coverage",
            "table_only": True,
            "does_not_render_full_graph": True,
        },
        "evidence_refs": [row["source_id"] for row in rows],
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_analytics_charts(
    chart_id: str | None = None,
    limit: int = 50,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    charts = _chart_payloads(snapshot, limit=_bounded_limit(limit))
    payload = {
        **_base_view_metadata(snapshot, mode="analytics-charts"),
        "charts": charts if chart_id is None else {chart_id: charts.get(chart_id, [])},
        "limit": _bounded_limit(limit),
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_analytics_tables(
    table_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    tables = _table_payloads(snapshot)
    bounded_limit = _bounded_limit(limit)
    safe_offset = max(0, offset)
    selected = tables if table_id is None else {table_id: tables.get(table_id, [])}
    paged = {
        key: rows[safe_offset : safe_offset + bounded_limit]
        for key, rows in selected.items()
    }
    payload = {
        **_base_view_metadata(snapshot, mode="analytics-tables"),
        "tables": paged,
        "limit": bounded_limit,
        "offset": safe_offset,
        "next_offset": safe_offset + bounded_limit,
    }
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
            "source_payloads_excluded",
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


def _filter_edges_by_relationship_class(edges: list[Any], relationship_class: str | None) -> list[Any]:
    if not relationship_class:
        return edges
    allowed = {
        SUPPLY_RELATIONSHIP_CLASS,
        DEMAND_RELATIONSHIP_CLASS,
        PRODUCTION_DEPENDENCY_CLASS,
        EVIDENCE_RELATIONSHIP_CLASS,
    }
    requested = relationship_class.strip().upper()
    if requested not in allowed:
        return []
    return [edge for edge in edges if classify_edge(edge.edge_type) == requested]


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
    relationship = normalize_relationship_edge(
        {
            "edge_id": edge.edge_id,
            "source_node_id": edge.source_node_id,
            "target_node_id": edge.target_node_id,
            "edge_type": edge.edge_type,
            "weight": edge.weight,
            "confidence": edge.confidence,
            "attributes": edge.attributes or {},
            "provenance_refs": [
                ref.model_dump(mode="json") if hasattr(ref, "model_dump") else ref
                for ref in edge.provenance_refs
            ],
            "evidence_text_summary": edge.evidence_text_summary,
            "valid_from": edge.valid_from.isoformat() if hasattr(edge.valid_from, "isoformat") else None,
            "valid_to": edge.valid_to.isoformat() if getattr(edge, "valid_to", None) else None,
        }
    )
    relationship_attributes = relationship["attributes"]
    return {
        "id": edge.edge_id,
        "source": edge.source_node_id,
        "target": edge.target_node_id,
        "edge_type": edge.edge_type,
        "relationship_class": relationship_attributes["relationship_class"],
        "layer": layer,
        "weight": edge.weight,
        "confidence": edge.confidence,
        "evidence_summary": str(edge.evidence_text_summary or "")[:280],
        "evidence_refs": source_ref_ids(edge.provenance_refs),
        "metadata": _safe_metadata({**dict(edge.attributes or {}), **relationship_attributes}),
        "not_supply_chain_dependency": relationship_attributes.get("not_supply_chain_dependency") is True,
        "derived_context": relationship_attributes.get("derived_context") is True,
        "user_facing_label": relationship_attributes.get("user_facing_label", edge.edge_type),
        "warning": relationship_attributes.get("warning"),
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
    if edge_type in {"trade_dependency_edge"}:
        return "trade"
    if edge_type in {"routes_through", "located_in"}:
        return "route"
    if edge_type in {"logistics_route_edge"}:
        return "route"
    if edge_type in {"hazard_exposure_edge"}:
        return "hazard"
    if edge_type in {"policy_restriction_edge"}:
        return "policy"
    if edge_type in {"sanctions_screening_event", "compliance_risk"}:
        return "sanctions"
    if edge_type in {"evidence_for"}:
        return "event"
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


def _bounded_limit(limit: int | None) -> int:
    if limit is None:
        return 50
    return max(1, min(int(limit), 500))


def _node_catalog_rows(*, limit: int) -> list[dict[str, Any]]:
    root = Path(__file__).resolve().parents[3]
    catalog_path = root / "configs" / "ontology" / "semiconductor_node_catalog.yaml"
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for node in catalog.get("nodes", [])[:limit]:
        rows.append(
            {
                "node_id": str(node["node_id"]),
                "node_type": str(node["node_type"]),
                "layer": str(node["layer"]),
                "label": str(node["label"]),
                "source_candidates": [str(item) for item in node.get("source_candidates", [])],
                "warnings": ["catalog_seed_not_production_relationship"],
            }
        )
    return rows


def _neighbors_for_node(snapshot: Any, node_id: str) -> list[str]:
    neighbors: set[str] = set()
    for edge in snapshot.edges:
        if edge.source_node_id == node_id:
            neighbors.add(edge.target_node_id)
        if edge.target_node_id == node_id:
            neighbors.add(edge.source_node_id)
    return sorted(neighbors)


def _concentration_metrics(snapshot: Any) -> list[dict[str, Any]]:
    metrics = []
    for edge in snapshot.edges:
        if edge.edge_type != "trade_dependency_edge":
            continue
        attributes = getattr(edge, "attributes", {}) or {}
        metrics.append(
            {
                "edge_id": edge.edge_id,
                "source": edge.source_node_id,
                "target": edge.target_node_id,
                "weight": edge.weight,
                "confidence": edge.confidence,
                "country_product_hhi": attributes.get("country_product_hhi"),
            }
        )
    return metrics[:50]


def _chart_payloads(snapshot: Any, *, limit: int) -> dict[str, list[dict[str, Any]]]:
    nodes = sorted(snapshot.nodes, key=lambda node: (-float(node.confidence), node.node_id))
    edge_counts = Counter(edge.edge_type for edge in snapshot.edges)
    source_counts = Counter(
        source_id
        for edge in snapshot.edges
        for source_id in source_ref_ids(edge.provenance_refs)
    )
    return {
        "risk_score_ranking": [
            {"id": node.node_id, "label": node.canonical_name, "score": node.confidence}
            for node in nodes[:limit]
        ],
        "risk_component_breakdown": [
            {"component": edge_type, "value": count} for edge_type, count in edge_counts.items()
        ][:limit],
        "hhi_concentration_bar": _concentration_metrics(snapshot)[:limit],
        "trade_flow_sankey": [
            _edge_view(edge)
            for edge in snapshot.edges
            if edge.edge_type in {"trade_dependency_edge", "exports_to", "imports_from"}
        ][:limit],
        "country_dependency_heatmap": [
            _edge_view(edge) for edge in snapshot.edges if _layer_for_edge(edge.edge_type) == "trade"
        ][:limit],
        "policy_event_timeline": [
            _node_view(node) for node in snapshot.nodes if node.node_type == "policy_event"
        ][:limit],
        "hazard_exposure_timeline": [
            _node_view(node) for node in snapshot.nodes if node.node_type == "hazard_event"
        ][:limit],
        "monte_carlo_loss_histogram": [],
        "monte_carlo_ecdf": [],
        "cvar_tail": [],
        "resilience_functionality_curve": [],
        "optimizer_before_after": [],
        "validation_ablation_bar": [],
        "source_freshness_table": [
            {"source_id": source_id, "evidence_count": count}
            for source_id, count in sorted(source_counts.items())
        ][:limit],
        "graph_quality_table": [
            {"metric": key, "value": value}
            for key, value in (snapshot.quality_report or {}).items()
            if isinstance(value, (int, float, str))
        ][:limit],
        "evidence_refs_table": _evidence_rows(snapshot, limit=limit),
    }


def _table_payloads(snapshot: Any) -> dict[str, list[dict[str, Any]]]:
    nodes = [_node_view(node) for node in snapshot.nodes]
    edges = [_edge_view(edge) for edge in snapshot.edges]
    evidence = _evidence_rows(snapshot, limit=500)
    return {
        "source_catalog": [],
        "source_status": [],
        "connector_status": [],
        "graph_nodes": nodes,
        "graph_edges": edges,
        "unresolved_entities": [],
        "risk_rankings": [
            {"id": node["id"], "label": node["label"], "score": node["confidence"]}
            for node in nodes
        ],
        "scenario_runs": [],
        "reverse_stress_results": [],
        "optimizer_actions": [],
        "reports": [],
        "validation_artifacts": [],
        "evidence_refs": evidence,
        "trade_flows": [edge for edge in edges if edge["edge_type"] == "trade_dependency_edge"],
        "policy_events": [node for node in nodes if node["kind"] == "policy_event"],
        "hazard_events": [node for node in nodes if node["kind"] == "hazard_event"],
        "logistics_facilities": [node for node in nodes if node["kind"] == "logistics_facility"],
    }


def _evidence_rows(snapshot: Any, *, limit: int) -> list[dict[str, Any]]:
    rows = []
    for edge in snapshot.edges:
        refs = source_ref_ids(edge.provenance_refs)
        rows.append(
            {
                "edge_id": edge.edge_id,
                "edge_type": edge.edge_type,
                "source_refs": refs,
                "confidence": edge.confidence,
                "evidence_summary": str(edge.evidence_text_summary or "")[:280],
            }
        )
    return rows[:limit]
