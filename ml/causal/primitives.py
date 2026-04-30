"""Dependency-free causal and simulation primitives for graph snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from graph_kernel.events import EdgeKey
from graph_kernel.snapshots import EdgeRecord, GraphSnapshot

from ml.dataset import DatasetRecord


@dataclass(frozen=True)
class GraphIntervention:
    remove_nodes: tuple[str, ...] = ()
    remove_edges: tuple[EdgeKey, ...] = ()
    upsert_edges: tuple[EdgeRecord, ...] = ()
    update_edge_attrs: Mapping[EdgeKey, Mapping[str, float | int | str]] = field(default_factory=dict)


def apply_intervention(snapshot: GraphSnapshot, intervention: GraphIntervention) -> GraphSnapshot:
    removed_nodes = set(intervention.remove_nodes)
    removed_edges = set(intervention.remove_edges)
    upserts = {edge.key: edge for edge in intervention.upsert_edges}
    updates = dict(intervention.update_edge_attrs)

    edge_map: dict[EdgeKey, EdgeRecord] = {}
    for edge in snapshot.edges:
        if edge.source in removed_nodes or edge.target in removed_nodes or edge.key in removed_edges:
            continue
        attrs = dict(edge.attrs)
        if edge.key in updates:
            attrs.update(updates[edge.key])
        edge_map[edge.key] = EdgeRecord(
            source=edge.source,
            target=edge.target,
            kind=edge.kind,
            attrs=attrs,
            effective_at=edge.effective_at,
            observed_at=edge.observed_at,
            event_id=edge.event_id,
        )
    edge_map.update(upserts)

    nodes = set(snapshot.nodes).difference(removed_nodes)
    for edge in edge_map.values():
        nodes.add(edge.source)
        nodes.add(edge.target)
    node_attrs = {
        node: dict(snapshot.node_attrs.get(node, {}))
        for node in nodes
        if node in snapshot.node_attrs
    }
    return GraphSnapshot(
        as_of=snapshot.as_of,
        nodes=tuple(sorted(nodes)),
        edges=tuple(edge_map.values()),
        node_attrs=node_attrs,
    )


def simulate_disruption(
    snapshot: GraphSnapshot,
    *,
    disrupted_nodes: tuple[str, ...] = (),
    reliability_threshold: float | None = None,
) -> GraphSnapshot:
    remove_nodes = set(disrupted_nodes)
    remove_edges: list[EdgeKey] = []
    for edge in snapshot.edges:
        if edge.source in remove_nodes or edge.target in remove_nodes:
            remove_edges.append(edge.key)
            continue
        if reliability_threshold is not None:
            reliability = edge.attrs.get("reliability")
            if reliability is not None and float(reliability) < reliability_threshold:
                remove_edges.append(edge.key)
    return apply_intervention(
        snapshot,
        GraphIntervention(remove_nodes=tuple(sorted(remove_nodes)), remove_edges=tuple(sorted(remove_edges))),
    )


def estimate_ate(
    records: tuple[DatasetRecord, ...],
    *,
    treatment_feature: str,
    threshold: float,
) -> float:
    treated = [
        record.label
        for record in records
        if float(record.features.get(treatment_feature, 0.0)) >= threshold
    ]
    control = [
        record.label
        for record in records
        if float(record.features.get(treatment_feature, 0.0)) < threshold
    ]
    if not treated or not control:
        raise ValueError("both treated and control groups must be non-empty")
    return (sum(treated) / len(treated)) - (sum(control) / len(control))
