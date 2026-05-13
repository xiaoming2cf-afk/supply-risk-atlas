from __future__ import annotations

from datetime import datetime, timezone
import csv
from hashlib import sha256
from io import StringIO
import json
from typing import Any

from sra_core.api.envelope import make_envelope
from services.api.services.common import semiconductor_metadata
from services.api.services.graph_service import (
    GRAPH_VIEW_VERSION,
    _base_view_metadata,
    _bounded_limit,
    _build_active_semiconductor_snapshot,
    _chart_payloads,
    _relationship_edge_payloads,
    _supplier_concentration,
    _table_payloads,
)
from graph_kernel.supply_demand_builder import (
    demand_relationship_rows,
    production_dependency_rows,
    supply_demand_balance_rows,
    supply_relationship_rows,
)
from sra_core.sources.registry import source_readiness_rows


ANALYTICS_EXPORT_VERSION = "semirisk_analytics_export_v0.1"
MAX_EXPORT_ROWS = 500

TABLE_ALIASES = {
    "source-catalog": "source_catalog",
    "source_status": "source_status",
    "source-status": "source_status",
    "connector-status": "connector_status",
    "evidence-refs": "evidence_refs",
    "graph-quality": "graph_quality_table",
    "risk-ranking": "risk_rankings",
    "risk-rankings": "risk_rankings",
    "trade-flows": "trade_flows",
    "policy-events": "policy_events",
    "hazard-events": "hazard_events",
    "logistics-facilities": "logistics_facilities",
    "supply-relationships": "supply_relationships",
    "demand-relationships": "demand_relationships",
    "production-dependencies": "production_dependencies",
    "supplier-concentration": "supplier_concentration",
    "product-demand": "product_demand",
    "critical-inputs": "critical_inputs",
    "supply-demand-balance": "supply_demand_balance",
}

PUBLIC_TABLE_IDS = {
    "source_catalog",
    "source_status",
    "connector_status",
    "evidence_refs",
    "graph_quality_table",
    "risk_rankings",
    "trade_flows",
    "policy_events",
    "hazard_events",
    "logistics_facilities",
    "supply_relationships",
    "demand_relationships",
    "production_dependencies",
    "supplier_concentration",
    "product_demand",
    "critical_inputs",
    "supply_demand_balance",
}

EXPORT_FORMATS = {"json", "csv", "markdown"}
BLOCKED_KEY_PARTS = (
    "raw",
    "payload",
    "secret",
    "token",
    "private",
    "cookie",
    "authorization",
    "password",
    "internal_path",
)


def route_analytics_table(
    table_id: str,
    limit: int = 50,
    offset: int = 0,
    request_id: str | None = None,
) -> dict[str, Any]:
    snapshot = _build_active_semiconductor_snapshot()
    normalized_table_id = _normalize_table_id(table_id)
    rows = _table_rows(normalized_table_id, limit=limit, offset=offset)
    bounded_limit = _bounded_limit(limit)
    safe_offset = max(0, offset)
    payload = {
        **_safe_view_metadata(snapshot, mode=f"analytics-table:{normalized_table_id}"),
        "table_id": normalized_table_id,
        "rows": rows,
        "limit": bounded_limit,
        "offset": safe_offset,
        "next_offset": safe_offset + bounded_limit,
        "row_count": len(rows),
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=payload["warnings"],
    )


def route_analytics_export(
    table_id: str,
    export_format: str = "json",
    limit: int = 50,
    offset: int = 0,
    request_id: str | None = None,
) -> dict[str, Any]:
    normalized_format = export_format.strip().lower()
    if normalized_format not in EXPORT_FORMATS:
        raise LookupError("unsupported analytics export format")
    snapshot = _build_active_semiconductor_snapshot()
    normalized_table_id = _normalize_table_id(table_id)
    bounded_limit = min(_bounded_limit(limit), MAX_EXPORT_ROWS)
    safe_offset = max(0, offset)
    rows = _table_rows(normalized_table_id, limit=bounded_limit, offset=safe_offset)
    export_time = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    export_content = _format_export(normalized_format, normalized_table_id, rows)
    content_hash = sha256(
        json.dumps(
            {
                "table_id": normalized_table_id,
                "format": normalized_format,
                "rows": rows,
                "graph_version": snapshot.graph_version,
                "source_manifest_id": snapshot.source_manifest_id,
            },
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    payload = {
        **_safe_view_metadata(snapshot, mode=f"analytics-export:{normalized_table_id}"),
        "table_id": normalized_table_id,
        "format": normalized_format,
        "export_time": export_time,
        "row_count": len(rows),
        "limit": bounded_limit,
        "offset": safe_offset,
        "content_hash": content_hash,
        "content": export_content,
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=ANALYTICS_EXPORT_VERSION),
        request_id=request_id,
        warnings=payload["warnings"],
    )


def _normalize_table_id(table_id: str) -> str:
    normalized = table_id.strip().lower().replace("-", "_")
    normalized = TABLE_ALIASES.get(table_id.strip().lower(), TABLE_ALIASES.get(normalized, normalized))
    if normalized not in PUBLIC_TABLE_IDS:
        raise LookupError("unknown analytics table")
    return normalized


def _safe_view_metadata(snapshot: Any, *, mode: str) -> dict[str, Any]:
    metadata = _base_view_metadata(snapshot, mode=mode)
    metadata["fixture_limitations"] = [
        str(item).replace("source_payloads_excluded", "source_content_excluded")
        for item in metadata.get("fixture_limitations", [])
    ]
    return metadata


def _table_rows(table_id: str, *, limit: int, offset: int) -> list[dict[str, Any]]:
    bounded_limit = _bounded_limit(limit)
    safe_offset = max(0, offset)
    rows = _all_table_rows(table_id)
    return [_sanitize_row(row) for row in rows[safe_offset : safe_offset + bounded_limit]]


def _all_table_rows(table_id: str) -> list[dict[str, Any]]:
    snapshot = _build_active_semiconductor_snapshot()
    if table_id in {"source_catalog", "source_status", "connector_status"}:
        source_rows = source_readiness_rows()
        if table_id == "connector_status":
            return [
                {
                    "source_id": row["source_id"],
                    "publisher": row["publisher"],
                    "connector": row["connector"],
                    "connector_status": row["connector_status"],
                    "status": row["status"],
                    "source_tier": row["source_tier"],
                }
                for row in source_rows
            ]
        if table_id == "source_status":
            return [
                {
                    "source_id": row["source_id"],
                    "publisher": row["publisher"],
                    "status": row["status"],
                    "source_tier": row["source_tier"],
                    "data_category": row["data_category"],
                    "freshness_sla_hours": row["freshness_sla_hours"],
                }
                for row in source_rows
            ]
        return [
            {
                "source_id": row["source_id"],
                "publisher": row["publisher"],
                "source_tier": row["source_tier"],
                "data_category": row["data_category"],
                "enabled_by_default": row["enabled_by_default"],
                "live_fetch_default": row["live_fetch_default"],
                "license_or_terms_summary": row["license_or_terms_summary"],
                "attribution": row["attribution"],
                "status": row["status"],
            }
            for row in source_rows
        ]

    if table_id == "graph_quality_table":
        return _chart_payloads(snapshot, limit=MAX_EXPORT_ROWS).get("graph_quality_table", [])
    relationship_edges = _relationship_edge_payloads(snapshot)
    if table_id == "supply_relationships":
        return supply_relationship_rows(relationship_edges)
    if table_id == "demand_relationships":
        return demand_relationship_rows(relationship_edges)
    if table_id == "production_dependencies":
        return production_dependency_rows(relationship_edges)
    if table_id == "supplier_concentration":
        return _supplier_concentration(supply_relationship_rows(relationship_edges))
    if table_id == "product_demand":
        return demand_relationship_rows(relationship_edges)
    if table_id == "critical_inputs":
        return [
            row for row in production_dependency_rows(relationship_edges)
            if row.get("bottleneck_flag") is True
        ]
    if table_id == "supply_demand_balance":
        return supply_demand_balance_rows(relationship_edges)
    return _table_payloads(snapshot).get(table_id, [])


def _sanitize_row(row: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, value in row.items():
        lowered = str(key).lower()
        if any(part in lowered for part in BLOCKED_KEY_PARTS):
            continue
        clean[str(key)] = _sanitize_value(value)
    return clean


def _sanitize_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _sanitize_text(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value[:50]]
    if isinstance(value, dict):
        return _sanitize_row(value)
    return _sanitize_text(str(value))


def _sanitize_text(value: str) -> str:
    text = value.replace("<", "").replace(">", "")
    lowered = text.lower()
    if "script" in lowered or "onerror" in lowered or "javascript:" in lowered:
        text = "[sanitized external text]"
    if len(text) > 500:
        text = text[:497] + "..."
    return text


def _format_export(export_format: str, table_id: str, rows: list[dict[str, Any]]) -> Any:
    if export_format == "json":
        return {"rows": rows}
    if export_format == "csv":
        return _rows_to_csv(rows)
    return _rows_to_markdown(table_id, rows)


def _rows_to_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    columns = _columns_for_rows(rows)
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: _cell_to_text(row.get(column)) for column in columns})
    return buffer.getvalue()


def _rows_to_markdown(table_id: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return f"# {table_id}\n\nNo rows available for this bounded export."
    columns = _columns_for_rows(rows)
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(_cell_to_text(row.get(column)).replace("|", "/") for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([f"# {table_id}", "", header, divider, *body])


def _columns_for_rows(rows: list[dict[str, Any]]) -> list[str]:
    columns: list[str] = []
    for row in rows[:10]:
        for key in row:
            if key not in columns:
                columns.append(key)
            if len(columns) >= 12:
                return columns
    return columns


def _cell_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return json.dumps(value, sort_keys=True)
