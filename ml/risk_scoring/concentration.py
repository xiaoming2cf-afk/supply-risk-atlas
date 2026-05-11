from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from sra_core.contracts.semiconductor import SemiriskEdge, SemiriskGraphSnapshot

from .weighting import clamp01


OECD_DERIVED_HHI_THRESHOLDS = {
    "scale": "0_to_1",
    "low": "<0.20",
    "moderate": "0.20-<0.40",
    "high": ">=0.40",
}


def hhi(values_or_shares: Iterable[float]) -> float:
    values = [max(0.0, float(value)) for value in values_or_shares]
    if not values:
        return 0.0
    total = sum(values)
    if total <= 0:
        return 0.0
    shares = values if abs(total - 1.0) <= 1e-6 else [value / total for value in values]
    return round(sum(share * share for share in shares), 6)


def normalized_hhi(values_or_shares: Iterable[float]) -> float:
    values = [max(0.0, float(value)) for value in values_or_shares]
    raw = hhi(values)
    n = len([value for value in values if value > 0])
    if n <= 1:
        return 1.0 if raw > 0 else 0.0
    minimum = 1.0 / n
    return round(max(0.0, min(1.0, (raw - minimum) / (1.0 - minimum))), 6)


def concentration_level(value: float, policy: str = "oecd_derived_supply_chain") -> str:
    if policy != "oecd_derived_supply_chain":
        raise ValueError(f"unsupported concentration threshold policy: {policy}")
    score = clamp01(value)
    if score < 0.20:
        return "low"
    if score < 0.40:
        return "moderate"
    return "high"


def significant_dependency(country_level_hhi: float, global_reference_hhi: float) -> bool:
    country_hhi = clamp01(country_level_hhi)
    reference_hhi = clamp01(global_reference_hhi)
    return country_hhi >= 0.40 and reference_hhi >= 0.20 and country_hhi > 2 * reference_hhi


def source_concentration_by_node(snapshot: SemiriskGraphSnapshot, node_id: str) -> dict[str, Any]:
    edges = _dependency_edges(snapshot, node_id)
    supplier_values: dict[str, float] = defaultdict(float)
    for edge in edges:
        supplier = edge.source_node_id if edge.target_node_id == node_id else edge.target_node_id
        supplier_values[supplier] += max(0.01, float(edge.weight) * float(edge.confidence))
    values = list(supplier_values.values())
    raw_hhi = hhi(values)
    refs = _unique_refs([ref for edge in edges for ref in _edge_refs(edge)])
    warnings = ["fixture_proxy_supplier_shares"] if values else ["source_concentration_unavailable"]
    return {
        "node_id": node_id,
        "hhi": raw_hhi,
        "normalized_hhi": normalized_hhi(values),
        "hhi_scale": "0_to_1",
        "concentration_level": concentration_level(raw_hhi),
        "threshold_policy": "oecd_derived_supply_chain",
        "threshold_basis": OECD_DERIVED_HHI_THRESHOLDS,
        "significant_dependency": significant_dependency(raw_hhi, 0.20),
        "global_reference_hhi": 0.20,
        "source_refs": refs,
        "warnings": warnings,
    }


def country_concentration_by_input(snapshot: SemiriskGraphSnapshot, node_id: str) -> dict[str, Any]:
    node_country = _country_by_node(snapshot)
    countries: dict[str, float] = defaultdict(float)
    for edge in _dependency_edges(snapshot, node_id):
        for endpoint in (edge.source_node_id, edge.target_node_id):
            country = node_country.get(endpoint)
            if country:
                countries[country] += max(0.01, float(edge.weight) * float(edge.confidence))
    values = list(countries.values())
    raw_hhi = hhi(values)
    global_reference_hhi = 0.20
    significant = significant_dependency(raw_hhi, global_reference_hhi)
    return {
        "node_id": node_id,
        "country_count": len(countries),
        "country_shares": _shares(countries),
        "hhi": raw_hhi,
        "normalized_hhi": normalized_hhi(values),
        "hhi_scale": "0_to_1",
        "concentration_level": concentration_level(raw_hhi),
        "threshold_policy": "oecd_derived_supply_chain",
        "threshold_basis": OECD_DERIVED_HHI_THRESHOLDS,
        "significant_dependency": significant,
        "global_reference_hhi": global_reference_hhi,
        "source_refs": _unique_refs([ref for edge in _dependency_edges(snapshot, node_id) for ref in _edge_refs(edge)]),
        "warnings": ["fixture_proxy_country_shares", "fixture_global_reference_hhi_proxy"],
    }


def substitute_count(snapshot: SemiriskGraphSnapshot, node_id: str) -> int:
    return len(
        [
            edge
            for edge in snapshot.edges
            if edge.edge_type == "substitutable_with"
            and (edge.source_node_id == node_id or edge.target_node_id == node_id)
        ]
    )


def substitution_gap(snapshot: SemiriskGraphSnapshot, node_id: str) -> dict[str, Any]:
    dependencies = _dependency_edges(snapshot, node_id)
    substitutes = [
        edge
        for edge in snapshot.edges
        if edge.edge_type == "substitutable_with"
        and (edge.source_node_id == node_id or edge.target_node_id == node_id)
    ]
    dependency_pressure = min(1.0, sum(edge.weight * edge.confidence for edge in dependencies) / max(1, len(dependencies)))
    substitute_support = min(1.0, sum(edge.weight * edge.confidence for edge in substitutes))
    gap = clamp01(dependency_pressure * (1.0 - min(0.95, substitute_support)))
    return {
        "node_id": node_id,
        "dependency_edge_count": len(dependencies),
        "substitute_count": len(substitutes),
        "substitution_gap": round(gap, 6),
        "source_refs": _unique_refs([ref for edge in [*dependencies, *substitutes] for ref in _edge_refs(edge)]),
        "warnings": ["fixture_proxy_substitution_gap"] if dependencies else ["substitution_gap_unavailable"],
    }


def _dependency_edges(snapshot: SemiriskGraphSnapshot, node_id: str) -> list[SemiriskEdge]:
    return [
        edge
        for edge in snapshot.edges
        if edge.edge_type in {"depends_on", "requires", "supplies", "produces", "routes_through", "participates_in"}
        and (edge.source_node_id == node_id or edge.target_node_id == node_id)
    ]


def _country_by_node(snapshot: SemiriskGraphSnapshot) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for edge in snapshot.edges:
        if edge.edge_type == "located_in" and edge.target_node_id.startswith("country:"):
            mapping[edge.source_node_id] = edge.target_node_id
    return mapping


def _shares(values: dict[str, float]) -> dict[str, float]:
    total = sum(values.values())
    if total <= 0:
        return {}
    return {key: round(value / total, 6) for key, value in sorted(values.items())}


def _edge_refs(edge: SemiriskEdge) -> list[dict[str, Any]]:
    return [
        {
            "edge_id": edge.edge_id,
            "source_id": ref.source_id,
            "source_record_id": ref.source_record_id,
            "payload_hash": ref.payload_hash,
            "provenance_url": ref.provenance_url,
        }
        for ref in edge.provenance_refs
    ]


def _unique_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {}
    for ref in refs:
        by_key[(ref.get("source_id"), ref.get("source_record_id"), ref.get("payload_hash"), ref.get("edge_id"))] = ref
    return [by_key[key] for key in sorted(by_key)]
