from __future__ import annotations

import json
from typing import Any

from services.api.runtime.run_store import sanitized_run_copy
from services.api.storage.sqlite_store import SQLiteStore


class SQLiteRunStore:
    def __init__(self, store: SQLiteStore, *, max_items: int = 256) -> None:
        self.store = store
        self.max_items = max(1, max_items)
        self.store.initialize()

    def put_summary(self, run_type: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        if not isinstance(data, dict):
            return None
        run_id = str(data.get("run_id") or data.get("report_id") or "")
        if not run_id:
            return None
        clean = sanitized_run_copy(
            {
                "run_id": run_id,
                "run_type": run_type,
                "created_at": data.get("timestamp") or data.get("generated_at") or "",
                "status": payload.get("status", "success"),
                "graph_version": data.get("graph_version") or _nested_get(data, "versions", "graph_version"),
                "source_manifest_id": data.get("source_manifest_id")
                or _nested_get(data, "versions", "source_manifest_id"),
                "data_mode": data.get("data_mode") or _nested_get(data, "versions", "data_mode") or "fixture",
                "graph_mode": data.get("graph_mode") or _nested_get(data, "versions", "graph_mode") or "fixture",
                "request_hash": data.get("request_hash"),
                "summary": _summary_for_run(data),
                "warnings": payload.get("warnings") or data.get("warnings") or [],
                "evidence_refs": data.get("evidence_refs") or [],
                "versions": {
                    "model_version": data.get("model_version"),
                    "feature_version": data.get("feature_version") or _nested_get(data, "versions", "feature_version"),
                    "simulation_version": data.get("simulation_version")
                    or _nested_get(data, "versions", "simulation_version"),
                    "optimization_version": data.get("optimization_version")
                    or _nested_get(data, "versions", "optimization_version"),
                    "report_version": data.get("report_version") or _nested_get(data, "versions", "report_version"),
                    "data_mode": data.get("data_mode"),
                    "graph_mode": data.get("graph_mode"),
                },
            }
        )
        self.store.execute(
            """
            INSERT OR REPLACE INTO run_record
            (run_id, run_type, created_at, status, graph_version, source_manifest_id, request_hash,
             summary_json, warnings_json, evidence_refs_json, versions_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clean["run_id"],
                clean["run_type"],
                clean.get("created_at") or "",
                clean.get("status", "success"),
                clean.get("graph_version"),
                clean.get("source_manifest_id"),
                clean.get("request_hash"),
                _json(clean.get("summary", {})),
                _json(clean.get("warnings", [])),
                _json(clean.get("evidence_refs", [])),
                _json(clean.get("versions", {})),
            ),
        )
        self.cleanup()
        return clean

    def list_summaries(self) -> list[dict[str, Any]]:
        rows = self.store.fetch_all(
            "SELECT * FROM run_record ORDER BY created_at DESC, run_id DESC LIMIT ?",
            (self.max_items,),
        )
        return [_row_to_run(row) for row in rows]

    def get(self, run_id: str) -> dict[str, Any] | None:
        row = self.store.fetch_one("SELECT * FROM run_record WHERE run_id = ?", (run_id,))
        return _row_to_run(row) if row else None

    def cleanup(self) -> None:
        self.store.execute(
            """
            DELETE FROM run_record
            WHERE run_id NOT IN (
                SELECT run_id FROM run_record ORDER BY created_at DESC, run_id DESC LIMIT ?
            )
            """,
            (self.max_items,),
        )

    def clear(self) -> None:
        self.store.execute("DELETE FROM run_record")


def _row_to_run(row: dict[str, Any]) -> dict[str, Any]:
    versions = json.loads(row["versions_json"])
    return {
        "run_id": row["run_id"],
        "run_type": row["run_type"],
        "created_at": row["created_at"],
        "status": row["status"],
        "graph_version": row["graph_version"],
        "source_manifest_id": row["source_manifest_id"],
        "data_mode": versions.get("data_mode") or "fixture",
        "graph_mode": versions.get("graph_mode") or "fixture",
        "request_hash": row["request_hash"],
        "summary": json.loads(row["summary_json"]),
        "warnings": json.loads(row["warnings_json"]),
        "evidence_refs": json.loads(row["evidence_refs_json"]),
        "versions": versions,
    }


def _summary_for_run(data: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "scenario_type",
        "target_metric",
        "expected_loss",
        "p50_loss",
        "p90_loss",
        "p95_loss",
        "cvar_95",
        "before_expected_loss",
        "after_expected_loss",
        "budget",
        "resilience_roi",
        "loss_mode",
        "propagation_mode",
        "threshold_metric_basis",
        "optimization_context_type",
        "calibration_status",
    ]
    return sanitized_run_copy({key: data.get(key) for key in keys if key in data})


def _nested_get(data: dict[str, Any], parent: str, key: str) -> Any:
    nested = data.get(parent)
    return nested.get(key) if isinstance(nested, dict) else None


def _json(value: Any) -> str:
    return json.dumps(sanitized_run_copy(value), sort_keys=True)
