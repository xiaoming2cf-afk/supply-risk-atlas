from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml


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


def node_catalog_coverage(
    nodes: list[dict[str, Any]],
    *,
    catalog_path: Path | None = None,
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    catalog_path = catalog_path or root / "configs" / "ontology" / "semiconductor_node_catalog.yaml"
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    catalog_nodes = {str(node["node_id"]): node for node in catalog.get("nodes", [])}
    graph_node_ids = {str(node["node_id"]) for node in nodes}
    covered = sorted(catalog_nodes.keys() & graph_node_ids)
    missing = sorted(catalog_nodes.keys() - graph_node_ids)
    catalog_type_counts = Counter(str(node["node_type"]) for node in catalog_nodes.values())
    graph_type_counts = Counter(str(node.get("node_type", "unknown")) for node in nodes)
    return {
        "catalog_version": catalog.get("catalog_version"),
        "status": "partial" if missing else "pass",
        "catalog_node_count": len(catalog_nodes),
        "graph_node_count": len(graph_node_ids),
        "covered_catalog_node_count": len(covered),
        "coverage_ratio": round(len(covered) / max(1, len(catalog_nodes)), 4),
        "covered_catalog_node_ids": covered,
        "missing_catalog_node_ids": missing,
        "catalog_node_count_by_type": dict(sorted(catalog_type_counts.items())),
        "graph_node_count_by_type": dict(sorted(graph_type_counts.items())),
        "warnings": ["node_catalog_is_broader_than_fixture_promoted_graph"] if missing else [],
    }


def _source_id(ref: Any) -> str:
    if isinstance(ref, dict):
        return str(ref.get("source_id", "unknown"))
    return str(ref).split(":", 1)[0]
