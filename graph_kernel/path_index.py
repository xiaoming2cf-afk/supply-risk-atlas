from __future__ import annotations

from collections import deque
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from typing import TYPE_CHECKING, Any

from .snapshots import GraphSnapshot

if TYPE_CHECKING:
    from sra_core.contracts.domain import EdgeState as DomainEdgeState


def _path_id(nodes: list[str], edges: list[str]) -> str:
    digest = sha256(("|".join(nodes) + "::" + "|".join(edges)).encode("utf-8")).hexdigest()[:16]
    return f"path_{digest}"


@dataclass(frozen=True)
class Path:
    nodes: tuple[str, ...]
    edge_kinds: tuple[str, ...]

    @property
    def hop_count(self) -> int:
        return len(self.edge_kinds)


@dataclass(frozen=True)
class PathIndex:
    adjacency: dict[str, tuple[tuple[str, str], ...]]

    @classmethod
    def from_snapshot(cls, snapshot: GraphSnapshot) -> "PathIndex":
        adjacency: dict[str, list[tuple[str, str]]] = {node: [] for node in snapshot.nodes}
        for edge in snapshot.edges:
            adjacency.setdefault(edge.source, []).append((edge.target, edge.kind))
            adjacency.setdefault(edge.target, [])
        frozen = {
            node: tuple(sorted(neighbors, key=lambda item: (item[0], item[1])))
            for node, neighbors in sorted(adjacency.items())
        }
        return cls(adjacency=frozen)

    def neighbors(self, node: str) -> tuple[tuple[str, str], ...]:
        return self.adjacency.get(node, ())

    def reachable(self, source: str, *, max_hops: int) -> tuple[str, ...]:
        if max_hops < 0:
            raise ValueError("max_hops must be non-negative")
        seen = {source}
        reached: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(source, 0)])
        while queue:
            node, depth = queue.popleft()
            if depth == max_hops:
                continue
            for neighbor, _kind in self.neighbors(node):
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                reached.add(neighbor)
                queue.append((neighbor, depth + 1))
        return tuple(sorted(reached))

    def shortest_path(self, source: str, target: str, *, max_hops: int | None = None) -> Path | None:
        if source == target:
            return Path(nodes=(source,), edge_kinds=())
        limit = max_hops if max_hops is not None else len(self.adjacency)
        queue: deque[Path] = deque([Path(nodes=(source,), edge_kinds=())])
        while queue:
            path = queue.popleft()
            if path.hop_count >= limit:
                continue
            for neighbor, kind in self.neighbors(path.nodes[-1]):
                if neighbor in path.nodes:
                    continue
                candidate = Path(nodes=path.nodes + (neighbor,), edge_kinds=path.edge_kinds + (kind,))
                if neighbor == target:
                    return candidate
                queue.append(candidate)
        return None

    def paths_between(self, source: str, target: str, *, max_hops: int) -> tuple[Path, ...]:
        if max_hops < 0:
            raise ValueError("max_hops must be non-negative")
        results: list[Path] = []

        def walk(path: Path) -> None:
            if path.hop_count > max_hops:
                return
            if path.nodes[-1] == target and path.hop_count > 0:
                results.append(path)
                return
            if path.hop_count == max_hops:
                return
            for neighbor, kind in self.neighbors(path.nodes[-1]):
                if neighbor in path.nodes:
                    continue
                walk(Path(nodes=path.nodes + (neighbor,), edge_kinds=path.edge_kinds + (kind,)))

        walk(Path(nodes=(source,), edge_kinds=()))
        return tuple(sorted(results, key=lambda path: (path.hop_count, path.nodes, path.edge_kinds)))


def build_path_index(states: list["DomainEdgeState"], max_hops: int = 3) -> list[Any]:
    from sra_core.contracts.domain import PathIndex as DomainPathIndex

    active = [state for state in states if state.valid_to is None]
    outgoing: dict[str, list[DomainEdgeState]] = defaultdict(list)
    for state in active:
        outgoing[state.source_id].append(state)

    paths: list[Any] = []

    def walk(start: str, nodes: list[str], edges: list[DomainEdgeState], depth: int) -> None:
        if depth > max_hops:
            return
        current = nodes[-1]
        for edge in sorted(outgoing.get(current, []), key=lambda item: item.edge_id):
            if edge.target_id in nodes:
                continue
            next_nodes = [*nodes, edge.target_id]
            next_edges = [*edges, edge]
            edge_ids = [item.edge_id for item in next_edges]
            path_weight = 1.0
            path_risk = 0.0
            path_confidence = 1.0
            for item in next_edges:
                path_weight *= item.weight
                path_risk = max(path_risk, item.risk_score)
                path_confidence *= item.confidence
            paths.append(
                DomainPathIndex(
                    path_id=_path_id(next_nodes, edge_ids),
                    source_id=start,
                    target_id=edge.target_id,
                    meta_path=">".join(item.edge_type for item in next_edges),
                    node_sequence=next_nodes,
                    edge_sequence=edge_ids,
                    path_length=len(next_edges),
                    path_weight=path_weight,
                    path_risk=path_risk,
                    path_confidence=path_confidence,
                    valid_from=max(item.valid_from for item in next_edges),
                    valid_to=None,
                )
            )
            walk(start, next_nodes, next_edges, depth + 1)

    for source_id in sorted(outgoing):
        walk(source_id, [source_id], [], 1)
    return sorted(paths, key=lambda path: path.path_id)
