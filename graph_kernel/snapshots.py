"""Canonical graph snapshots, checksums, and diffs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from .events import EdgeKey, EdgeState


def _canonical_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical_value(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, set):
        return sorted(_canonical_value(item) for item in value)
    return value


def _frozen_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(_canonical_value(value or {}))


@dataclass(frozen=True)
class EdgeRecord:
    source: str
    target: str
    kind: str
    attrs: Mapping[str, Any] = field(default_factory=dict)
    effective_at: int = 0
    observed_at: int = 0
    event_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "attrs", _frozen_mapping(self.attrs))

    @property
    def key(self) -> EdgeKey:
        return EdgeKey(self.source, self.target, self.kind)

    def canonical(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "attrs": _canonical_value(self.attrs),
            "effective_at": self.effective_at,
            "observed_at": self.observed_at,
            "event_id": self.event_id,
        }


@dataclass(frozen=True)
class GraphSnapshot:
    as_of: int
    nodes: tuple[str, ...]
    edges: tuple[EdgeRecord, ...]
    node_attrs: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        nodes = tuple(sorted(dict.fromkeys(self.nodes)))
        edge_nodes = {edge.source for edge in self.edges} | {edge.target for edge in self.edges}
        missing = edge_nodes.difference(nodes)
        if missing:
            nodes = tuple(sorted(set(nodes) | missing))
        edges = tuple(sorted(self.edges, key=lambda edge: edge.key.as_tuple()))
        attrs = {
            node: _frozen_mapping(self.node_attrs.get(node, {}))
            for node in nodes
        }
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "edges", edges)
        object.__setattr__(self, "node_attrs", MappingProxyType(attrs))

    def canonical(self, *, include_as_of: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "nodes": [
                {"id": node, "attrs": _canonical_value(self.node_attrs.get(node, {}))}
                for node in self.nodes
            ],
            "edges": [edge.canonical() for edge in self.edges],
        }
        if include_as_of:
            payload["as_of"] = self.as_of
        return payload

    def edge_map(self) -> dict[EdgeKey, EdgeRecord]:
        return {edge.key: edge for edge in self.edges}


@dataclass(frozen=True)
class EdgeChange:
    before: EdgeRecord
    after: EdgeRecord


@dataclass(frozen=True)
class GraphDiff:
    added_nodes: tuple[str, ...]
    removed_nodes: tuple[str, ...]
    added_edges: tuple[EdgeRecord, ...]
    removed_edges: tuple[EdgeRecord, ...]
    changed_edges: tuple[EdgeChange, ...]

    @property
    def is_empty(self) -> bool:
        return not (
            self.added_nodes
            or self.removed_nodes
            or self.added_edges
            or self.removed_edges
            or self.changed_edges
        )


def snapshot_from_edge_states(
    states: Mapping[EdgeKey, EdgeState],
    as_of: int,
    *,
    node_attrs: Mapping[str, Mapping[str, Any]] | None = None,
) -> GraphSnapshot:
    edges = [
        EdgeRecord(
            source=state.key.source,
            target=state.key.target,
            kind=state.key.kind,
            attrs=state.attrs,
            effective_at=state.effective_at,
            observed_at=state.observed_at,
            event_id=state.event_id,
        )
        for state in states.values()
        if state.active
    ]
    nodes = set(node_attrs or {})
    for edge in edges:
        nodes.add(edge.source)
        nodes.add(edge.target)
    return GraphSnapshot(as_of=as_of, nodes=tuple(nodes), edges=tuple(edges), node_attrs=node_attrs or {})


def snapshot_checksum(snapshot: GraphSnapshot, *, include_as_of: bool = True) -> str:
    body = json.dumps(
        snapshot.canonical(include_as_of=include_as_of),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _edge_signature(edge: EdgeRecord) -> dict[str, Any]:
    return edge.canonical()


def diff_snapshots(before: GraphSnapshot, after: GraphSnapshot) -> GraphDiff:
    before_nodes = set(before.nodes)
    after_nodes = set(after.nodes)
    before_edges = before.edge_map()
    after_edges = after.edge_map()

    added_keys = sorted(set(after_edges).difference(before_edges), key=lambda key: key.as_tuple())
    removed_keys = sorted(set(before_edges).difference(after_edges), key=lambda key: key.as_tuple())
    shared_keys = sorted(set(before_edges).intersection(after_edges), key=lambda key: key.as_tuple())

    changed = tuple(
        EdgeChange(before=before_edges[key], after=after_edges[key])
        for key in shared_keys
        if _edge_signature(before_edges[key]) != _edge_signature(after_edges[key])
    )

    return GraphDiff(
        added_nodes=tuple(sorted(after_nodes.difference(before_nodes))),
        removed_nodes=tuple(sorted(before_nodes.difference(after_nodes))),
        added_edges=tuple(after_edges[key] for key in added_keys),
        removed_edges=tuple(before_edges[key] for key in removed_keys),
        changed_edges=changed,
    )
