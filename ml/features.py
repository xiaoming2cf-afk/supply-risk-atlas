"""Config-driven feature generation from graph snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Mapping

from graph_kernel.path_index import PathIndex
from graph_kernel.snapshots import EdgeRecord, GraphSnapshot


@dataclass(frozen=True)
class FeatureSpec:
    features: tuple[str, ...] = (
        "active_in_degree",
        "active_out_degree",
        "active_total_degree",
        "reachable_downstream_count",
        "mean_out_lead_time_days",
        "min_out_reliability",
    )
    max_hops: int = 2
    edge_kinds: tuple[str, ...] = ("supplies", "used_by", "ships_to")
    reliability_default: float = 1.0

    def __post_init__(self) -> None:
        if self.max_hops < 0:
            raise ValueError("max_hops must be non-negative")


def load_feature_spec(path: str | Path) -> FeatureSpec:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return FeatureSpec(
        features=tuple(payload.get("features", FeatureSpec.features)),
        max_hops=int(payload.get("max_hops", FeatureSpec.max_hops)),
        edge_kinds=tuple(payload.get("edge_kinds", FeatureSpec.edge_kinds)),
        reliability_default=float(payload.get("reliability_default", FeatureSpec.reliability_default)),
    )


class FeatureFactory:
    """Build deterministic node-level features from a snapshot only."""

    def __init__(self, spec: FeatureSpec | None = None) -> None:
        self.spec = spec or FeatureSpec()

    @property
    def feature_names(self) -> tuple[str, ...]:
        names: list[str] = []
        for name in self.spec.features:
            if name == "out_edge_kind_counts":
                names.extend(f"out_kind_{kind}_count" for kind in self.spec.edge_kinds)
            else:
                names.append(name)
        return tuple(names)

    def build(self, snapshot: GraphSnapshot) -> dict[str, dict[str, float]]:
        incoming, outgoing = _edge_adjacency(snapshot)
        path_index = PathIndex.from_snapshot(snapshot)
        rows: dict[str, dict[str, float]] = {}
        for node in snapshot.nodes:
            values = self._build_node(node, incoming, outgoing, path_index)
            rows[node] = {name: values[name] for name in self.feature_names}
        return rows

    def _build_node(
        self,
        node: str,
        incoming: Mapping[str, tuple[EdgeRecord, ...]],
        outgoing: Mapping[str, tuple[EdgeRecord, ...]],
        path_index: PathIndex,
    ) -> dict[str, float]:
        in_edges = incoming.get(node, ())
        out_edges = outgoing.get(node, ())
        lead_times = [_numeric(edge.attrs.get("lead_time_days")) for edge in out_edges if "lead_time_days" in edge.attrs]
        reliabilities = [
            _numeric(edge.attrs.get("reliability"), self.spec.reliability_default)
            for edge in out_edges
        ]
        values: dict[str, float] = {
            "active_in_degree": float(len(in_edges)),
            "active_out_degree": float(len(out_edges)),
            "active_total_degree": float(len(in_edges) + len(out_edges)),
            "reachable_downstream_count": float(len(path_index.reachable(node, max_hops=self.spec.max_hops))),
            "mean_out_lead_time_days": float(mean(lead_times)) if lead_times else 0.0,
            "min_out_reliability": float(min(reliabilities)) if reliabilities else self.spec.reliability_default,
        }
        for kind in self.spec.edge_kinds:
            values[f"out_kind_{kind}_count"] = float(sum(1 for edge in out_edges if edge.kind == kind))
        unknown = set(self.feature_names).difference(values)
        if unknown:
            raise ValueError(f"unknown feature names: {sorted(unknown)}")
        return values


def _edge_adjacency(
    snapshot: GraphSnapshot,
) -> tuple[dict[str, tuple[EdgeRecord, ...]], dict[str, tuple[EdgeRecord, ...]]]:
    incoming: dict[str, list[EdgeRecord]] = {node: [] for node in snapshot.nodes}
    outgoing: dict[str, list[EdgeRecord]] = {node: [] for node in snapshot.nodes}
    for edge in snapshot.edges:
        incoming.setdefault(edge.target, []).append(edge)
        outgoing.setdefault(edge.source, []).append(edge)
    return (
        {node: tuple(sorted(edges, key=lambda edge: edge.key.as_tuple())) for node, edges in incoming.items()},
        {node: tuple(sorted(edges, key=lambda edge: edge.key.as_tuple())) for node, edges in outgoing.items()},
    )


def _numeric(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
