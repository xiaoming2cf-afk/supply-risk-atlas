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
        run_id = str(data.get("run_id") or "")
        if not run_id:
            return None
        summary = {
            "run_id": run_id,
            "run_type": run_type,
            "created_at": data.get("timestamp") or data.get("generated_at"),
            "graph_version": data.get("graph_version"),
            "source_manifest_id": data.get("source_manifest_id"),
            "status": payload.get("status", "success"),
            "warnings": payload.get("warnings") or data.get("warnings") or [],
            "summary": _summary_for_run(data),
            "versions": {
                "feature_version": data.get("feature_version"),
                "simulation_version": data.get("simulation_version"),
                "optimization_version": data.get("optimization_version"),
                "report_version": data.get("report_version"),
            },
        }
        clean = sanitized_run_copy(summary)
        self.store.execute(
            """
            INSERT OR REPLACE INTO run_record
            (run_id, run_type, created_at, graph_version, source_manifest_id, status,
             summary_json, warnings_json, versions_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clean["run_id"],
                clean["run_type"],
                clean.get("created_at") or "",
                clean.get("graph_version"),
                clean.get("source_manifest_id"),
                clean.get("status", "success"),
                json.dumps(clean.get("summary", {}), sort_keys=True),
                json.dumps(clean.get("warnings", []), sort_keys=True),
                json.dumps(clean.get("versions", {}), sort_keys=True),
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


def _row_to_run(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": row["run_id"],
        "run_type": row["run_type"],
        "created_at": row["created_at"],
        "graph_version": row["graph_version"],
        "source_manifest_id": row["source_manifest_id"],
        "status": row["status"],
        "warnings": json.loads(row["warnings_json"]),
        "summary": json.loads(row["summary_json"]),
        "versions": json.loads(row["versions_json"]),
    }


def _summary_for_run(data: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "expected_loss",
        "cvar_95",
        "cvar95",
        "before_expected_loss",
        "after_expected_loss",
        "budget",
        "resilience_roi",
        "loss_mode",
        "propagation_mode",
    ]
    return sanitized_run_copy({key: data.get(key) for key in keys if key in data})

