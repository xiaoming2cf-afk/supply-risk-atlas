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
    node_types = load_yaml(ontology_dir / "node_types.yaml")["node_types"]
    edge_types = load_yaml(ontology_dir / "edge_types.yaml")["edge_types"]
    node_types.update(_CURATED_NODE_TYPE_EXTENSIONS)
    edge_types.update(_CURATED_EDGE_TYPE_EXTENSIONS)
    return Ontology(
        node_types=node_types,
        edge_types=edge_types,
        event_types=load_yaml(ontology_dir / "event_types.yaml")["event_types"],
        labels=load_yaml(ontology_dir / "risk_labels.yaml")["labels"],
    )


_CURATED_NODE_TYPE_EXTENSIONS: dict[str, dict[str, Any]] = {
    "component": {"description": "Intermediate component or bill-of-material node.", "required_fields": ["canonical_id", "name"], "temporal": True},
    "product_grade": {"description": "Qualified grade or variant of a product.", "required_fields": ["canonical_id", "name"], "temporal": True},
    "supplier_tier": {"description": "Tier taxonomy for direct and upstream suppliers.", "required_fields": ["canonical_id", "name"], "temporal": False},
    "route_lane": {"description": "Named logistics lane across route legs.", "required_fields": ["canonical_id", "name"], "temporal": True},
    "carrier": {"description": "Ocean, air, rail, or trucking carrier.", "required_fields": ["canonical_id", "name"], "temporal": True},
}


_CURATED_EDGE_TYPE_EXTENSIONS: dict[str, dict[str, Any]] = {
    "component_of": {"source": "component", "target": "product", "directed": True, "temporal": True, "required_fields": ["weight", "confidence", "valid_from"], "features": ["bom_share", "qualification_status"]},
    "input_to": {"source": "raw_material", "target": "component", "directed": True, "temporal": True, "required_fields": ["weight", "confidence", "valid_from"], "features": ["input_share", "dependency_ratio"]},
    "material_processed_into": {"source": "raw_material", "target": "component", "directed": True, "temporal": True, "required_fields": ["weight", "confidence", "valid_from"], "features": ["yield", "processing_location"]},
    "manufactured_at": {"source": "product", "target": "factory", "directed": True, "temporal": True, "required_fields": ["weight", "confidence", "valid_from"], "features": ["capacity_share", "utilization"]},
    "stored_at": {"source": "component", "target": "warehouse", "directed": True, "temporal": True, "required_fields": ["weight", "confidence", "valid_from"], "features": ["inventory_days", "buffer_stock"]},
    "ships_to": {"source": "factory", "target": "warehouse", "directed": True, "temporal": True, "required_fields": ["weight", "confidence", "valid_from"], "features": ["lead_time", "volume"]},
    "route_leg": {"source": "route_lane", "target": "port", "directed": True, "temporal": True, "required_fields": ["weight", "confidence", "valid_from"], "features": ["sequence", "distance"]},
    "handled_at": {"source": "carrier", "target": "route_lane", "directed": True, "temporal": True, "required_fields": ["weight", "confidence", "valid_from"], "features": ["capacity_share", "service_frequency"]},
    "used_by": {"source": "factory", "target": "firm", "directed": True, "temporal": True, "required_fields": ["weight", "confidence", "valid_from"], "features": ["capacity_share", "ownership_signal"]},
    "qualified_alternative_to": {"source": "product_grade", "target": "product", "directed": True, "temporal": True, "required_fields": ["weight", "confidence", "valid_from"], "features": ["qualification_time", "substitutability"]},
}
