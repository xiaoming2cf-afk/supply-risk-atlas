from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_snapshot
from graph_kernel.source_manifest import license_terms_for_sources, promoted_source_status
from sra_core.contracts.semiconductor import (
    DEFAULT_SEMIRISK_AS_OF_TIME,
    SemiconductorPromotionResult,
    SemiconductorRawRecord,
    SemiriskGraphSnapshot,
    payload_hash,
)
from sra_core.ingestion.connectors.gdelt_semiconductor_lite import (
    GdeltSemiconductorLiteConnector,
)
from sra_core.ingestion.connectors.sec_edgar_lite import SecEdgarLiteConnector
from sra_core.ingestion.semiconductor_promote import (
    promote_semiconductor_records,
    replay_semiconductor_fixtures,
)
from services.api.storage.manifest_store import ManifestStore
from services.api.storage.models import RawRecordIndex, SourceManifestRecord
from services.api.storage.sqlite_store import SQLiteStore


PROMOTED_GRAPH_MANIFEST_VERSION = "promoted_graph_manifest_v0.1"
PROMOTED_GRAPH_MODE = "promoted"
PROMOTED_DATA_MODE = "promoted_public_evidence_fixture"


@dataclass(frozen=True)
class PromotedGraphBuildResult:
    promotion: SemiconductorPromotionResult
    snapshot: SemiriskGraphSnapshot
    manifest: dict[str, Any]
    source_status: dict[str, Any]
    output_dir: Path | None = None


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_output_dir() -> Path:
    return project_root() / "data" / "promoted" / "latest"


def build_promoted_graph(
    *,
    fixture_dir: str | Path | None = None,
    registry_path: str | Path | None = None,
    as_of_time: str = DEFAULT_SEMIRISK_AS_OF_TIME,
    output_dir: str | Path | None = None,
    store_sqlite: bool = False,
    sqlite_path: str | Path | None = None,
) -> PromotedGraphBuildResult:
    records = promoted_raw_records(fixture_dir=fixture_dir, registry_path=registry_path)
    source_ids = tuple(sorted({record.source_id for record in records}))
    promotion = promote_semiconductor_records(
        records=records,
        registry_path=registry_path,
        as_of_time=as_of_time,
        source_ids=source_ids,
        manifest_prefix="promoted_public_evidence_manifest",
        fixture_graph=False,
    )
    snapshot = build_semiconductor_snapshot(promotion)
    if snapshot.quality_report.get("errors"):
        raise ValueError("; ".join(snapshot.quality_report["errors"]))
    source_status = promoted_source_status(registry_path)
    manifest = promoted_manifest_payload(
        promotion=promotion,
        snapshot=snapshot,
        source_status=source_status,
        registry_path=registry_path,
    )
    resolved_output_dir = Path(output_dir) if output_dir is not None else None
    if resolved_output_dir is not None:
        write_promoted_outputs(
            output_dir=resolved_output_dir,
            manifest=manifest,
            snapshot=snapshot,
            source_status=source_status,
        )
    if store_sqlite:
        store_promoted_snapshot(
            promotion=promotion,
            snapshot=snapshot,
            manifest=manifest,
            sqlite_path=sqlite_path,
        )
    return PromotedGraphBuildResult(
        promotion=promotion,
        snapshot=snapshot,
        manifest=manifest,
        source_status=source_status,
        output_dir=resolved_output_dir,
    )


def promoted_raw_records(
    *,
    fixture_dir: str | Path | None = None,
    registry_path: str | Path | None = None,
) -> list[SemiconductorRawRecord]:
    records = [
        *replay_semiconductor_fixtures(fixture_dir=fixture_dir, registry_path=registry_path),
        *SecEdgarLiteConnector().replay_fixture(
            fixture_dir=fixture_dir,
            registry_path=registry_path,
        ),
        *GdeltSemiconductorLiteConnector().replay_fixture(
            fixture_dir=fixture_dir,
            registry_path=registry_path,
        ),
    ]
    return sorted(records, key=lambda record: (record.source_id, record.source_record_id))


def promoted_manifest_payload(
    *,
    promotion: SemiconductorPromotionResult,
    snapshot: SemiriskGraphSnapshot,
    source_status: dict[str, Any],
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    source_ids = {record.source_id for record in promotion.raw_records}
    raw_record_index = [
        {
            "raw_id": record.raw_id,
            "source_id": record.source_id,
            "source_record_id": record.source_record_id,
            "payload_hash": record.payload_hash,
            "raw_payload_summary": record.raw_payload_summary,
            "provenance_url": record.provenance_url,
            "license_or_terms_ref": record.license_or_terms_ref,
            "retrieved_at": record.retrieved_at.isoformat(),
            "as_of_time": record.as_of_time.isoformat(),
        }
        for record in promotion.raw_records
    ]
    payload = {
        "manifest_version": PROMOTED_GRAPH_MANIFEST_VERSION,
        "graph_mode": PROMOTED_GRAPH_MODE,
        "data_mode": PROMOTED_DATA_MODE,
        "production_status": "not_production_ready",
        "calibration_status": "proxy_fixture_not_production_calibrated",
        "graph_version": snapshot.graph_version,
        "source_manifest_id": snapshot.source_manifest_id,
        "as_of_time": snapshot.as_of_time.isoformat(),
        "node_count": snapshot.node_count,
        "edge_count": snapshot.edge_count,
        "source_status": source_status["status"],
        "source_status_counts": source_status["connector_status_counts"],
        "license_terms": license_terms_for_sources(source_ids, registry_path),
        "raw_record_index": raw_record_index,
        "warnings": [
            "promoted_graph:public_fixture_evidence_not_production_ready",
            "live_ingestion:disabled",
            "raw_payloads_excluded",
            "financial_loss:not_modeled",
        ],
    }
    return {
        **payload,
        "manifest_hash": payload_hash(payload),
    }


def write_promoted_outputs(
    *,
    output_dir: str | Path,
    manifest: dict[str, Any],
    snapshot: SemiriskGraphSnapshot,
    source_status: dict[str, Any],
) -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    _write_json(path / "manifest.json", manifest)
    _write_json(path / "graph_snapshot.json", snapshot.model_dump(mode="json"))
    _write_json(path / "source_status.json", source_status)


def store_promoted_snapshot(
    *,
    promotion: SemiconductorPromotionResult,
    snapshot: SemiriskGraphSnapshot,
    manifest: dict[str, Any],
    sqlite_path: str | Path | None = None,
) -> None:
    store = SQLiteStore(sqlite_path)
    store.initialize()
    manifest_store = ManifestStore(store)
    manifest_store.put_manifest(
        SourceManifestRecord(
            source_manifest_id=snapshot.source_manifest_id,
            graph_version=snapshot.graph_version,
            as_of_time=snapshot.as_of_time.isoformat(),
            source_status=manifest["source_status"],
            license_terms=manifest["license_terms"],
            manifest=manifest,
        )
    )
    for record in promotion.raw_records:
        manifest_store.put_raw_record_index(
            RawRecordIndex(
                raw_id=record.raw_id,
                source_id=record.source_id,
                source_record_id=record.source_record_id,
                payload_hash=record.payload_hash,
                raw_payload_summary=record.raw_payload_summary,
                provenance_url=record.provenance_url,
                license_or_terms_ref=record.license_or_terms_ref,
                retrieved_at=record.retrieved_at.isoformat(),
                as_of_time=record.as_of_time.isoformat(),
            )
        )
    with store.transaction() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO graph_snapshot
            (graph_version, source_manifest_id, as_of_time, node_count, edge_count, snapshot_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot.graph_version,
                snapshot.source_manifest_id,
                snapshot.as_of_time.isoformat(),
                snapshot.node_count,
                snapshot.edge_count,
                json.dumps(snapshot.model_dump(mode="json"), sort_keys=True),
            ),
        )
        for node in snapshot.nodes:
            connection.execute(
                """
                INSERT OR REPLACE INTO graph_node
                (graph_version, node_id, node_type, canonical_name, node_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    snapshot.graph_version,
                    node.node_id,
                    node.node_type,
                    node.canonical_name,
                    json.dumps(node.model_dump(mode="json"), sort_keys=True),
                ),
            )
        for edge in snapshot.edges:
            connection.execute(
                """
                INSERT OR REPLACE INTO graph_edge
                (graph_version, edge_id, source_node_id, target_node_id, edge_type, edge_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.graph_version,
                    edge.edge_id,
                    edge.source_node_id,
                    edge.target_node_id,
                    edge.edge_type,
                    json.dumps(edge.model_dump(mode="json"), sort_keys=True),
                ),
            )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
