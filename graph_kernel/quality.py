from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

import yaml


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_semiconductor_ontology(path: str | Path | None = None) -> dict[str, Any]:
    ontology_path = Path(path) if path else project_root() / "configs" / "ontology" / "semiconductor.yaml"
    return yaml.safe_load(ontology_path.read_text(encoding="utf-8"))


def semiconductor_quality_report(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    ontology = load_semiconductor_ontology()
    node_types = ontology["node_types"]
    edge_types = ontology["edge_types"]
    nodes = [_as_dict(node) for node in snapshot.get("nodes", [])]
    edges = [_as_dict(edge) for edge in snapshot.get("edges", [])]
    node_by_id = {node["node_id"]: node for node in nodes}
    errors: list[str] = []
    warnings: list[str] = []

    _duplicates([node["node_id"] for node in nodes], "node", errors)
    _duplicates([edge["edge_id"] for edge in edges], "edge", errors)

    for node in nodes:
        node_id = node["node_id"]
        node_type = node.get("node_type")
        if node_type not in node_types:
            errors.append(f"node {node_id}: invalid node_type {node_type}")
        if not node.get("source_refs"):
            warnings.append(f"node {node_id}: missing source_refs")
        _check_temporal(node, f"node {node_id}", errors)

    for edge in edges:
        edge_id = edge["edge_id"]
        edge_type = edge.get("edge_type")
        source_node_id = edge.get("source_node_id")
        target_node_id = edge.get("target_node_id")
        source_node = node_by_id.get(source_node_id)
        target_node = node_by_id.get(target_node_id)
        if source_node is None:
            errors.append(f"edge {edge_id}: unresolved source_node_id {source_node_id}")
        if target_node is None:
            errors.append(f"edge {edge_id}: unresolved target_node_id {target_node_id}")
        if edge_type not in edge_types:
            errors.append(f"edge {edge_id}: invalid edge_type {edge_type}")
        elif source_node and target_node:
            spec = edge_types[edge_type]
            if source_node["node_type"] not in spec["source"]:
                errors.append(
                    f"edge {edge_id}: invalid source direction {source_node['node_type']}->{edge_type}"
                )
            if target_node["node_type"] not in spec["target"]:
                errors.append(
                    f"edge {edge_id}: invalid target direction {edge_type}->{target_node['node_type']}"
                )
        if not edge.get("provenance_refs"):
            warnings.append(f"edge {edge_id}: missing provenance_refs")
        _check_temporal(edge, f"edge {edge_id}", errors)

    missing_provenance_count = sum(1 for node in nodes if not node.get("source_refs")) + sum(
        1 for edge in edges if not edge.get("provenance_refs")
    )
    unresolved_entity_count = sum(
        1
        for edge in edges
        if edge.get("source_node_id") not in node_by_id or edge.get("target_node_id") not in node_by_id
    )
    return {
        "status": "fail" if errors else "warn" if warnings else "pass",
        "errors": sorted(errors),
        "warnings": sorted(warnings),
        "missing_provenance_count": missing_provenance_count,
        "unresolved_entity_count": unresolved_entity_count,
        "metrics": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "node_type_count": len({node["node_type"] for node in nodes}),
            "edge_type_count": len({edge["edge_type"] for edge in edges}),
        },
    }


def assert_semiconductor_quality(snapshot: Mapping[str, Any]) -> None:
    report = semiconductor_quality_report(snapshot)
    if report["errors"]:
        raise ValueError("; ".join(report["errors"]))


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    raise TypeError(f"Expected graph item mapping, got {type(value)!r}")


def _duplicates(values: list[str], label: str, errors: list[str]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    for value in sorted(duplicates):
        errors.append(f"duplicate {label} id {value}")


def _check_temporal(record: Mapping[str, Any], label: str, errors: list[str]) -> None:
    valid_from = _parse_time(record.get("valid_from"))
    valid_to = _parse_time(record.get("valid_to"))
    if valid_from is None:
        errors.append(f"{label}: valid_from is required")
    if valid_from is not None and valid_to is not None and valid_from > valid_to:
        errors.append(f"{label}: valid_from must be <= valid_to")


def _parse_time(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
