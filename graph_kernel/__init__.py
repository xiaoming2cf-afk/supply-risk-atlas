"""Temporal heterogeneous graph kernel."""

from .events import EdgeEvent, EdgeKey, EdgeState, materialize_edge_state
from .path_index import Path, PathIndex
from .snapshots import (
    EdgeChange,
    EdgeRecord,
    GraphDiff,
    GraphSnapshot,
    diff_snapshots,
    snapshot_checksum,
    snapshot_from_edge_states,
)
from .synthetic import SyntheticGraphSpec, generate_synthetic_edge_events

__all__ = [
    "EdgeChange",
    "EdgeEvent",
    "EdgeKey",
    "EdgeRecord",
    "EdgeState",
    "GraphDiff",
    "GraphSnapshot",
    "Path",
    "PathIndex",
    "SyntheticGraphSpec",
    "build_graph_snapshot",
    "diff_snapshots",
    "generate_synthetic_edge_events",
    "materialize_edge_state",
    "snapshot_checksum",
    "snapshot_from_edge_states",
]


def __getattr__(name: str):
    if name == "build_graph_snapshot":
        from graph_kernel.snapshot_builder import build_graph_snapshot

        return build_graph_snapshot
    raise AttributeError(name)
