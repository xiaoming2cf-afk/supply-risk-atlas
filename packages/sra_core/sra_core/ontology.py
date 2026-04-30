from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Ontology:
    node_types: dict[str, dict[str, Any]]
    edge_types: dict[str, dict[str, Any]]
    event_types: dict[str, dict[str, Any]]
    labels: dict[str, dict[str, Any]]

    def validate(self) -> list[str]:
        errors: list[str] = []
        for edge_type, spec in self.edge_types.items():
            source = spec.get("source")
            target = spec.get("target")
            if source not in self.node_types:
                errors.append(f"edge_type {edge_type} references unknown source node type {source}")
            if target not in self.node_types:
                errors.append(f"edge_type {edge_type} references unknown target node type {target}")
            required = set(spec.get("required_fields", []))
            for field in ("confidence", "valid_from"):
                if field not in required:
                    errors.append(f"edge_type {edge_type} must require {field}")
        return errors


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML file {path} must contain a mapping")
    return data


def load_ontology(root: Path) -> Ontology:
    ontology_dir = root / "configs" / "ontology"
    return Ontology(
        node_types=load_yaml(ontology_dir / "node_types.yaml")["node_types"],
        edge_types=load_yaml(ontology_dir / "edge_types.yaml")["edge_types"],
        event_types=load_yaml(ontology_dir / "event_types.yaml")["event_types"],
        labels=load_yaml(ontology_dir / "risk_labels.yaml")["labels"],
    )
