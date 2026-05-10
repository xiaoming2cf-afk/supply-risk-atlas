from __future__ import annotations

from typing import Any

from sra_core.contracts.semiconductor import SemiriskGraphSnapshot, payload_hash


def lineage_for_node(snapshot: SemiriskGraphSnapshot | dict[str, Any], node_id: str) -> dict[str, Any]:
    graph = _snapshot_dict(snapshot)
    nodes = {node["node_id"]: node for node in graph.get("nodes", [])}
    if node_id not in nodes:
        return _missing("node", node_id, graph)
    incident_edges = [
        edge
        for edge in graph.get("edges", [])
        if edge["source_node_id"] == node_id or edge["target_node_id"] == node_id
    ]
    source_refs = _unique_refs(
        [*nodes[node_id].get("source_refs", []), *[ref for edge in incident_edges for ref in edge.get("provenance_refs", [])]]
    )
    payload = {
        "graph_version": graph["graph_version"],
        "source_manifest_id": graph["source_manifest_id"],
        "node_id": node_id,
        "source_refs": source_refs,
        "incident_edge_ids": [edge["edge_id"] for edge in incident_edges],
    }
    return {
        "status": "success",
        **payload,
        "node_type": nodes[node_id]["node_type"],
        "lineage_ref": f"semirisk_lineage_{payload_hash(payload)[:12]}",
    }


def lineage_for_edge(snapshot: SemiriskGraphSnapshot | dict[str, Any], edge_id: str) -> dict[str, Any]:
    graph = _snapshot_dict(snapshot)
    edges = {edge["edge_id"]: edge for edge in graph.get("edges", [])}
    if edge_id not in edges:
        return _missing("edge", edge_id, graph)
    edge = edges[edge_id]
    source_refs = _unique_refs(edge.get("provenance_refs", []))
    payload = {
        "graph_version": graph["graph_version"],
        "source_manifest_id": graph["source_manifest_id"],
        "edge_id": edge_id,
        "source_refs": source_refs,
    }
    return {
        "status": "success",
        **payload,
        "edge_type": edge["edge_type"],
        "source_node_id": edge["source_node_id"],
        "target_node_id": edge["target_node_id"],
        "lineage_ref": f"semirisk_lineage_{payload_hash(payload)[:12]}",
    }


def _snapshot_dict(snapshot: SemiriskGraphSnapshot | dict[str, Any]) -> dict[str, Any]:
    if isinstance(snapshot, dict):
        return snapshot
    return snapshot.model_dump(mode="json")


def _missing(kind: str, identifier: str, graph: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "error",
        "error": f"unknown {kind}_id: {identifier}",
        "graph_version": graph.get("graph_version"),
        "source_manifest_id": graph.get("source_manifest_id"),
    }


def _unique_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {
        (
            ref.get("source_id"),
            ref.get("source_record_id"),
            ref.get("payload_hash"),
        ): ref
        for ref in refs
    }
    return [by_key[key] for key in sorted(by_key)]
