from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

from graph_kernel.graph_versioning import promoted_graph_version, stable_hash
from graph_kernel.promoted_graph_quality import node_catalog_coverage, quality_report, source_coverage
from graph_kernel.relationship_builder import (
    build_relationship_edge_groups,
    normalize_relationship_edge,
    relationship_metadata,
)
from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from graph_kernel.source_manifest import build_source_manifest
from sra_core.geo.normalize import sanitize_graph_node
from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.bis_export_controls_lite import BisExportControlsLiteConnector
from sra_core.ingestion.connectors.consolidated_screening_list_lite import (
    ConsolidatedScreeningListLiteConnector,
)
from sra_core.ingestion.connectors.federal_register_export_controls_lite import (
    FederalRegisterExportControlsLiteConnector,
)
from sra_core.ingestion.connectors.gdelt_semiconductor_lite import GdeltSemiconductorLiteConnector
from sra_core.ingestion.connectors.nga_world_port_index_lite import NgaWorldPortIndexLiteConnector
from sra_core.ingestion.connectors.ofac_sanctions_list_lite import OfacSanctionsListLiteConnector
from sra_core.ingestion.connectors.sec_edgar_lite import SecEdgarLiteConnector
from sra_core.ingestion.connectors.un_comtrade_semiconductor_trade_lite import (
    UnComtradeSemiconductorTradeLiteConnector,
)
from sra_core.ingestion.connectors.usgs_earthquake_lite import UsgsEarthquakeLiteConnector
from sra_core.ingestion.connectors.usgs_minerals_lite import UsgsMineralsLiteConnector
from sra_core.ingestion.connectors.wits_trade_tariff_lite import WitsTradeTariffLiteConnector


PROMOTED_AS_OF_TIME = "2026-05-12T00:00:00+00:00"
PROMOTED_ONTOLOGY_VERSION = "semirisk_public_evidence_ontology_v0.1"


@dataclass(frozen=True)
class PromotedSourceRef:
    source_id: str
    source_record_id: str

    def model_dump(self, mode: str = "json") -> dict[str, str]:
        return {"source_id": self.source_id, "source_record_id": self.source_record_id}


@dataclass(frozen=True)
class PromotedNode:
    node_id: str
    node_type: str
    canonical_name: str
    attributes: dict[str, Any]
    source_refs: tuple[PromotedSourceRef, ...]
    confidence: float
    valid_from: datetime
    valid_to: datetime | None = None

    def model_dump(self, mode: str = "json") -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "canonical_name": self.canonical_name,
            "attributes": self.attributes,
            "source_refs": [ref.model_dump(mode=mode) for ref in self.source_refs],
            "confidence": self.confidence,
            "valid_from": self.valid_from.isoformat(),
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
        }


@dataclass(frozen=True)
class PromotedEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: str
    weight: float
    confidence: float
    attributes: dict[str, Any]
    provenance_refs: tuple[PromotedSourceRef, ...]
    evidence_text_summary: str
    valid_from: datetime
    valid_to: datetime | None = None

    def model_dump(self, mode: str = "json") -> dict[str, Any]:
        return normalize_relationship_edge(
            {
                "edge_id": self.edge_id,
                "source_node_id": self.source_node_id,
                "target_node_id": self.target_node_id,
                "edge_type": self.edge_type,
                "weight": self.weight,
                "confidence": self.confidence,
                "attributes": self.attributes,
                "provenance_refs": [ref.model_dump(mode=mode) for ref in self.provenance_refs],
                "evidence_text_summary": self.evidence_text_summary,
                "valid_from": self.valid_from.isoformat(),
                "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            }
        )


@dataclass(frozen=True)
class PromotedGraphSnapshot:
    graph_version: str
    ontology_version: str
    source_manifest_id: str
    as_of_time: datetime
    node_count: int
    edge_count: int
    node_count_by_type: dict[str, int]
    edge_count_by_type: dict[str, int]
    missing_provenance_count: int
    unresolved_entity_count: int
    stale_source_count: int
    nodes: tuple[PromotedNode, ...]
    edges: tuple[PromotedEdge, ...]
    quality_report: dict[str, Any]
    data_mode: str = "public_evidence_promoted"
    graph_mode: str = "promoted"

    def model_dump(self, mode: str = "json") -> dict[str, Any]:
        edge_payloads = [edge.model_dump(mode=mode) for edge in self.edges]
        return {
            "graph_version": self.graph_version,
            "ontology_version": self.ontology_version,
            "source_manifest_id": self.source_manifest_id,
            "as_of_time": self.as_of_time.isoformat(),
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "node_count_by_type": self.node_count_by_type,
            "edge_count_by_type": self.edge_count_by_type,
            "missing_provenance_count": self.missing_provenance_count,
            "unresolved_entity_count": self.unresolved_entity_count,
            "stale_source_count": self.stale_source_count,
            "nodes": [node.model_dump(mode=mode) for node in self.nodes],
            "edges": edge_payloads,
            "relationship_edge_groups": build_relationship_edge_groups(edge_payloads),
            "quality_report": self.quality_report,
            "data_mode": self.data_mode,
            "graph_mode": self.graph_mode,
            "warnings": ["promoted_public_evidence:not_production_ready"],
        }


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_fixture_dir() -> Path:
    return repository_root() / "tests" / "ingestion" / "fixtures"


def default_promoted_dir() -> Path:
    return repository_root() / "data" / "promoted" / "latest"


def connector_specs(fixture_dir: Path | None = None) -> list[tuple[PublicEvidenceConnector, Path]]:
    fixture_dir = fixture_dir or default_fixture_dir()
    return [
        (
            SecEdgarLiteConnector(
                config=ConnectorConfig(
                    mode="fixture", fixture_path=fixture_dir / "sec_edgar_lite_sample.json"
                )
            ),
            fixture_dir / "sec_edgar_lite_sample.json",
        ),
        (
            GdeltSemiconductorLiteConnector(
                config=ConnectorConfig(
                    mode="fixture", fixture_path=fixture_dir / "gdelt_semiconductor_lite_sample.json"
                )
            ),
            fixture_dir / "gdelt_semiconductor_lite_sample.json",
        ),
        (
            UnComtradeSemiconductorTradeLiteConnector(
                config=ConnectorConfig(
                    mode="fixture",
                    fixture_path=fixture_dir / "un_comtrade_semiconductor_trade_lite_sample.json",
                )
            ),
            fixture_dir / "un_comtrade_semiconductor_trade_lite_sample.json",
        ),
        (
            WitsTradeTariffLiteConnector(
                config=ConnectorConfig(
                    mode="fixture", fixture_path=fixture_dir / "wits_trade_tariff_lite_sample.json"
                )
            ),
            fixture_dir / "wits_trade_tariff_lite_sample.json",
        ),
        (
            UsgsMineralsLiteConnector(
                config=ConnectorConfig(
                    mode="fixture", fixture_path=fixture_dir / "usgs_minerals_lite_sample.json"
                )
            ),
            fixture_dir / "usgs_minerals_lite_sample.json",
        ),
        (
            UsgsEarthquakeLiteConnector(
                config=ConnectorConfig(
                    mode="fixture", fixture_path=fixture_dir / "usgs_earthquake_lite_sample.json"
                )
            ),
            fixture_dir / "usgs_earthquake_lite_sample.json",
        ),
        (
            NgaWorldPortIndexLiteConnector(
                config=ConnectorConfig(
                    mode="fixture",
                    fixture_path=fixture_dir / "nga_world_port_index_lite_sample.json",
                )
            ),
            fixture_dir / "nga_world_port_index_lite_sample.json",
        ),
        (
            OfacSanctionsListLiteConnector(
                config=ConnectorConfig(
                    mode="fixture", fixture_path=fixture_dir / "ofac_sanctions_list_lite_sample.json"
                )
            ),
            fixture_dir / "ofac_sanctions_list_lite_sample.json",
        ),
        (
            ConsolidatedScreeningListLiteConnector(
                config=ConnectorConfig(
                    mode="fixture",
                    fixture_path=fixture_dir / "consolidated_screening_list_lite_sample.json",
                )
            ),
            fixture_dir / "consolidated_screening_list_lite_sample.json",
        ),
        (
            BisExportControlsLiteConnector(
                config=ConnectorConfig(
                    mode="fixture", fixture_path=fixture_dir / "bis_export_controls_lite_sample.json"
                )
            ),
            fixture_dir / "bis_export_controls_lite_sample.json",
        ),
        (
            FederalRegisterExportControlsLiteConnector(
                config=ConnectorConfig(
                    mode="fixture",
                    fixture_path=fixture_dir / "federal_register_export_controls_lite_sample.json",
                )
            ),
            fixture_dir / "federal_register_export_controls_lite_sample.json",
        ),
    ]


def build_promoted_graph_snapshot(
    *,
    fixture_dir: Path | None = None,
    store_sqlite: bool = False,
) -> PromotedGraphSnapshot:
    fixture_snapshot = build_semiconductor_fixture_snapshot()
    as_of = datetime.fromisoformat(PROMOTED_AS_OF_TIME)
    node_rows: dict[str, dict[str, Any]] = {
        node.node_id: _node_dict_from_fixture(node) for node in fixture_snapshot.nodes
    }
    edge_rows: dict[str, dict[str, Any]] = {
        edge.edge_id: _edge_dict_from_fixture(edge) for edge in fixture_snapshot.edges
    }
    promoted_records: list[dict[str, Any]] = []
    source_ids = [
        "eto_cset_advanced_semiconductor_supply_chain",
        "wsts_historical_billings",
        "global_trade_alert_semiconductor_export_controls",
        "gdelt_semiconductor_events",
    ]

    for connector, _path in connector_specs(fixture_dir):
        result = connector.fetch()
        source_ids.append(connector.source_id)
        promoted = connector.promote(result.records)
        promoted_records.extend(promoted)
        _add_promoted_records(node_rows, edge_rows, promoted)
    _add_relationship_seed_edges(node_rows, edge_rows)

    manifest = build_source_manifest(source_ids)
    quality = quality_report(list(node_rows.values()), list(edge_rows.values()))
    version_basis = {
        "ontology_version": PROMOTED_ONTOLOGY_VERSION,
        "source_manifest_id": manifest["source_manifest_id"],
        "nodes": sorted(node_rows.values(), key=lambda row: row["node_id"]),
        "edges": sorted(edge_rows.values(), key=lambda row: row["edge_id"]),
    }
    graph_version = promoted_graph_version(version_basis)
    nodes_out = tuple(
        _node_from_dict(row, as_of) for row in sorted(node_rows.values(), key=lambda item: item["node_id"])
    )
    edges_out = tuple(
        _edge_from_dict(row, as_of) for row in sorted(edge_rows.values(), key=lambda item: item["edge_id"])
    )
    snapshot = PromotedGraphSnapshot(
        graph_version=graph_version,
        ontology_version=PROMOTED_ONTOLOGY_VERSION,
        source_manifest_id=manifest["source_manifest_id"],
        as_of_time=as_of,
        node_count=len(nodes_out),
        edge_count=len(edges_out),
        node_count_by_type=dict(Counter(node.node_type for node in nodes_out)),
        edge_count_by_type=dict(Counter(edge.edge_type for edge in edges_out)),
        missing_provenance_count=quality["missing_node_provenance_count"]
        + quality["missing_edge_provenance_count"],
        unresolved_entity_count=0,
        stale_source_count=0,
        nodes=nodes_out,
        edges=edges_out,
        quality_report=quality,
    )
    if store_sqlite and os.getenv("SUPPLY_RISK_STORAGE_MODE", "memory").lower() == "sqlite":
        _store_snapshot_sqlite(snapshot)
    return snapshot


def build_promoted_artifacts(
    *,
    output_dir: Path | None = None,
    fixture_dir: Path | None = None,
    store_sqlite: bool = False,
) -> dict[str, Any]:
    snapshot = build_promoted_graph_snapshot(fixture_dir=fixture_dir, store_sqlite=store_sqlite)
    snapshot_payload = snapshot.model_dump(mode="json")
    source_ids = sorted(
        {
            ref["source_id"]
            for node in snapshot_payload["nodes"]
            for ref in node.get("source_refs", [])
        }
        | {
            ref["source_id"]
            for edge in snapshot_payload["edges"]
            for ref in edge.get("provenance_refs", [])
        }
    )
    manifest = build_source_manifest(source_ids)
    coverage = source_coverage(snapshot_payload["nodes"], snapshot_payload["edges"])
    catalog_coverage = node_catalog_coverage(snapshot_payload["nodes"])
    resolution_report = {
        "status": "pass",
        "unresolved_count": snapshot.unresolved_entity_count,
        "warnings": ["crosswalks_are_deterministic_starter_maps"],
    }
    artifacts = {
        "manifest": {
            **manifest,
            "graph_version": snapshot.graph_version,
            "data_mode": snapshot.data_mode,
            "graph_mode": snapshot.graph_mode,
        },
        "graph_snapshot": snapshot_payload,
        "source_status": {
            "source_ids": source_ids,
            "source_count": len(source_ids),
            "status": "fixture_replayed_promoted",
            "warnings": ["live_fetch_disabled_by_default"],
        },
        "quality_report": snapshot.quality_report,
        "source_coverage": coverage,
        "entity_resolution_report": resolution_report,
        "node_catalog_coverage": catalog_coverage,
    }
    if output_dir is not None:
        write_promoted_artifacts(artifacts, output_dir)
    return artifacts


def write_promoted_artifacts(artifacts: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    mapping = {
        "manifest": "manifest.json",
        "graph_snapshot": "graph_snapshot.json",
        "source_status": "source_status.json",
        "quality_report": "quality_report.json",
        "source_coverage": "source_coverage.json",
        "entity_resolution_report": "entity_resolution_report.json",
        "node_catalog_coverage": "node_catalog_coverage.json",
    }
    for key, filename in mapping.items():
        (output_dir / filename).write_text(
            json.dumps(artifacts[key], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _add_promoted_records(
    node_rows: dict[str, dict[str, Any]],
    edge_rows: dict[str, dict[str, Any]],
    records: list[dict[str, Any]],
) -> None:
    for record in records:
        record_type = record["record_type"]
        if record_type == "company_disclosure_event":
            event_id = record["event_id"]
            company_id = record["company_identifier"]
            _ensure_node(node_rows, company_id, "company", company_id, record)
            _ensure_node(node_rows, event_id, "risk_event", record["disclosure_type"], record)
            _add_edge(edge_rows, company_id, event_id, "evidence_for", record)
        elif record_type == "risk_event":
            event_id = record["event_id"]
            _ensure_node(node_rows, event_id, "risk_event", record["event_type"], record)
            for entity_id in record.get("affected_entities", []):
                _ensure_node(node_rows, entity_id, "entity_or_region", entity_id, record)
                _add_edge(edge_rows, entity_id, event_id, "impacted_by", record)
        elif record_type == "trade_flow":
            reporter = f"country:{record['reporter']}"
            partner = f"country:{record['partner']}"
            commodity = f"commodity:{record['commodity_code']}"
            _ensure_node(node_rows, reporter, "country", record["reporter"], record)
            _ensure_node(node_rows, partner, "country", record["partner"], record)
            _ensure_node(node_rows, commodity, "commodity", record["commodity_label"], record)
            _add_edge(edge_rows, reporter, partner, "trade_dependency_edge", record)
            _add_edge(edge_rows, reporter, commodity, "evidence_for", record)
        elif record_type == "trade_tariff_indicator":
            country = f"country:{record['country']}"
            indicator = record["indicator_id"]
            _ensure_node(node_rows, country, "country", record["country"], record)
            _ensure_node(node_rows, indicator, "market_indicator", record["indicator_type"], record)
            _add_edge(edge_rows, country, indicator, "evidence_for", record)
        elif record_type == "mineral_supply_indicator":
            mineral = f"critical_mineral:{record['mineral']}"
            country = f"country:{record['country']}"
            indicator = record["indicator_id"]
            _ensure_node(node_rows, mineral, "critical_mineral", record["mineral"], record)
            _ensure_node(node_rows, country, "country", record["country"], record)
            _ensure_node(node_rows, indicator, "market_indicator", record["mineral"], record)
            _add_edge(edge_rows, country, mineral, "mineral_dependency_edge", record)
            _add_edge(edge_rows, mineral, indicator, "evidence_for", record)
        elif record_type == "natural_hazard_event":
            event_id = record["hazard_event_id"]
            _ensure_node(node_rows, event_id, "hazard_event", record["affected_region"], record)
            _add_edge(edge_rows, event_id, "region:china_taiwan", "hazard_exposure_edge", record)
        elif record_type == "logistics_facility":
            node_id = record["logistics_node_id"]
            country = f"country:{record['country_code']}"
            _ensure_node(node_rows, node_id, "logistics_facility", record["name"], record)
            _ensure_node(node_rows, country, "country", record["country_code"], record)
            _add_edge(edge_rows, country, node_id, "logistics_route_edge", record)
        elif record_type == "sanctions_screening_event":
            event_id = record["screening_event_id"]
            _ensure_node(node_rows, event_id, "sanctions_event", record["list_type"], record)
        elif record_type == "export_control_policy_event":
            event_id = record["policy_event_id"]
            jurisdiction = f"country:{record['jurisdiction']}"
            _ensure_node(node_rows, jurisdiction, "country", record["jurisdiction"], record)
            _ensure_node(node_rows, event_id, "policy_event", record["policy_title"], record)
            _add_edge(edge_rows, jurisdiction, event_id, "policy_restriction_edge", record)


def _add_relationship_seed_edges(
    node_rows: dict[str, dict[str, Any]],
    edge_rows: dict[str, dict[str, Any]],
) -> None:
    demand_record = {
        "source_refs": ["wsts_historical_billings:wsts-demand-proxy-fixture"],
        "confidence": 0.56,
        "evidence_text_summary": (
            "Fixture WSTS billings proxy marks downstream demand pressure for research testing."
        ),
        "demand_proxy_type": "fixture_market_billings_proxy",
        "period": "2026-Q1",
    }
    _ensure_node(node_rows, "sector:AI_datacenter", "downstream_sector", "AI datacenter", demand_record)
    _ensure_node(
        node_rows,
        "demand:wsts_global_billings_proxy",
        "demand_indicator",
        "WSTS billings proxy",
        demand_record,
    )
    _add_edge(edge_rows, "sector:AI_datacenter", "product_grade:hbm", "demands", demand_record)
    _add_edge(
        edge_rows,
        "demand:wsts_global_billings_proxy",
        "product_grade:advanced_logic",
        "demand_signal_for",
        demand_record,
    )


def _ensure_node(
    node_rows: dict[str, dict[str, Any]],
    node_id: str,
    node_type: str,
    label: str,
    record: dict[str, Any],
) -> None:
    safe_node = sanitize_graph_node(
        {
            "node_id": node_id,
            "node_type": node_type,
            "canonical_name": str(label),
            "attributes": {
                "data_mode": "public_evidence_promoted",
                "graph_mode": "promoted",
            },
            "source_refs": record.get("source_refs", []),
            "confidence": float(record.get("confidence", 0.5)),
        },
    )
    node_rows.setdefault(safe_node["node_id"], safe_node)


def _add_edge(
    edge_rows: dict[str, dict[str, Any]],
    source_node_id: str,
    target_node_id: str,
    edge_type: str,
    record: dict[str, Any],
) -> None:
    edge_id = f"promoted:{edge_type}:{stable_hash([source_node_id, target_node_id, record['source_refs']])[:12]}"
    edge_rows.setdefault(
        edge_id,
        normalize_relationship_edge(
            {
                "edge_id": edge_id,
                "source_node_id": source_node_id,
                "target_node_id": target_node_id,
                "edge_type": edge_type,
                "weight": float(record.get("dependency_share", 0.5)),
                "confidence": float(record.get("confidence", 0.5)),
                "attributes": {
                    **relationship_metadata(
                        edge_type,
                        source_node_id=source_node_id,
                        target_node_id=target_node_id,
                        attributes=record,
                    ),
                    "data_mode": "public_evidence_promoted",
                },
                "provenance_refs": record.get("source_refs", []),
                "evidence_text_summary": record.get("evidence_text_summary", ""),
            }
        ),
    )


def _node_dict_from_fixture(node: Any) -> dict[str, Any]:
    row = node.model_dump(mode="json")
    row["attributes"] = {
        key: value
        for key, value in (row.get("attributes") or {}).items()
        if "payload" not in key.lower() and "raw" not in key.lower()
    }
    row["source_refs"] = [
        f"{ref.get('source_id')}:{ref.get('source_record_id', 'fixture')}"
        for ref in row.get("source_refs", [])
    ] or ["semirisk_fixture:graph"]
    return sanitize_graph_node(row)


def _edge_dict_from_fixture(edge: Any) -> dict[str, Any]:
    row = edge.model_dump(mode="json")
    row["attributes"] = {
        key: value
        for key, value in (row.get("attributes") or {}).items()
        if "payload" not in key.lower() and "raw" not in key.lower()
    }
    row["provenance_refs"] = [
        f"{ref.get('source_id')}:{ref.get('source_record_id', 'fixture')}"
        for ref in row.get("provenance_refs", [])
    ] or ["semirisk_fixture:graph"]
    return normalize_relationship_edge(row)


def _node_from_dict(row: dict[str, Any], as_of: datetime) -> PromotedNode:
    return PromotedNode(
        node_id=row["node_id"],
        node_type=row["node_type"],
        canonical_name=row["canonical_name"],
        attributes=row.get("attributes", {}),
        source_refs=tuple(_source_ref(ref) for ref in row.get("source_refs", [])),
        confidence=float(row.get("confidence", 0.5)),
        valid_from=as_of,
    )


def _edge_from_dict(row: dict[str, Any], as_of: datetime) -> PromotedEdge:
    row = normalize_relationship_edge(row)
    return PromotedEdge(
        edge_id=row["edge_id"],
        source_node_id=row["source_node_id"],
        target_node_id=row["target_node_id"],
        edge_type=row["edge_type"],
        weight=float(row.get("weight", 0.5)),
        confidence=float(row.get("confidence", 0.5)),
        attributes=row.get("attributes", {}),
        provenance_refs=tuple(_source_ref(ref) for ref in row.get("provenance_refs", [])),
        evidence_text_summary=row.get("evidence_text_summary", ""),
        valid_from=as_of,
    )


def _source_ref(value: Any) -> PromotedSourceRef:
    if isinstance(value, dict):
        return PromotedSourceRef(
            source_id=str(value.get("source_id") or "unknown"),
            source_record_id=str(value.get("source_record_id") or "record"),
        )
    source_id, _, source_record_id = str(value).partition(":")
    return PromotedSourceRef(source_id=source_id, source_record_id=source_record_id or "record")


def _store_snapshot_sqlite(snapshot: PromotedGraphSnapshot) -> None:
    from services.api.storage.sqlite_store import SQLiteStore

    store = SQLiteStore()
    store.initialize()
    payload = snapshot.model_dump(mode="json")
    store.execute(
        """
        INSERT OR REPLACE INTO graph_snapshot (
            graph_version, source_manifest_id, ontology_version, as_of_time,
            node_count, edge_count, node_count_by_type_json, edge_count_by_type_json,
            quality_report_json, warnings_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            snapshot.graph_version,
            snapshot.source_manifest_id,
            snapshot.ontology_version,
            snapshot.as_of_time.isoformat(),
            snapshot.node_count,
            snapshot.edge_count,
            json.dumps(snapshot.node_count_by_type, sort_keys=True),
            json.dumps(snapshot.edge_count_by_type, sort_keys=True),
            json.dumps(snapshot.quality_report, sort_keys=True),
            json.dumps(payload["warnings"], sort_keys=True),
        ),
    )
