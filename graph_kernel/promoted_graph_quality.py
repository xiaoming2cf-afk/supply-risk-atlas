from __future__ import annotations

from collections import Counter
from typing import Any


def quality_report(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    missing_node_refs = 0
    missing_edge_refs = 0
    for node in nodes:
        if not node.get("source_refs"):
            missing_node_refs += 1
    for edge in edges:
        if not edge.get("provenance_refs"):
            missing_edge_refs += 1
    status = "pass" if missing_node_refs == 0 and missing_edge_refs == 0 else "degraded"
    return {
        "status": status,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "node_count_by_type": dict(Counter(node["node_type"] for node in nodes)),
        "edge_count_by_type": dict(Counter(edge["edge_type"] for edge in edges)),
        "missing_node_provenance_count": missing_node_refs,
        "missing_edge_provenance_count": missing_edge_refs,
        "warnings": [] if status == "pass" else ["promoted_graph_provenance_incomplete"],
    }


def source_coverage(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    for node in nodes:
        for ref in node.get("source_refs", []):
            counts[_source_id(ref)] += 1
    for edge in edges:
        for ref in edge.get("provenance_refs", []):
            counts[_source_id(ref)] += 1
    return {
        "source_count": len(counts),
        "counts_by_source_id": dict(sorted(counts.items())),
    }


def _source_id(ref: Any) -> str:
    if isinstance(ref, dict):
        return str(ref.get("source_id", "unknown"))
    return str(ref).split(":", 1)[0]
