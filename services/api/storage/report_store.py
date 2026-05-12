from __future__ import annotations

import json
from typing import Any

from services.api.runtime.run_store import sanitized_run_copy
from services.api.storage.sqlite_store import SQLiteStore


class ReportStore:
    def __init__(self, store: SQLiteStore, *, max_items: int = 256) -> None:
        self.store = store
        self.max_items = max(1, max_items)
        self.store.initialize()

    def put_report(self, report: dict[str, Any], *, markdown: str | None = None) -> dict[str, Any] | None:
        clean = sanitized_run_copy(report)
        report_id = str(clean.get("report_id") or "")
        if not report_id:
            return None
        versions = clean.get("versions") if isinstance(clean.get("versions"), dict) else {}
        self.store.execute(
            """
            INSERT OR REPLACE INTO report_record
            (report_id, created_at, graph_version, source_manifest_id, format, report_json,
             report_markdown, warnings_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                str(clean.get("generated_at") or ""),
                versions.get("graph_version"),
                versions.get("source_manifest_id"),
                str(clean.get("format") or ("markdown" if markdown else "json")),
                json.dumps(clean, sort_keys=True),
                markdown,
                json.dumps(clean.get("warnings", []), sort_keys=True),
            ),
        )
        self.cleanup()
        return clean

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        row = self.store.fetch_one("SELECT * FROM report_record WHERE report_id = ?", (report_id,))
        if row is None:
            return None
        report = sanitized_run_copy(json.loads(row["report_json"]))
        report["raw_payload_excluded"] = True
        report["private_diagnostics_excluded"] = True
        if row.get("report_markdown"):
            report["markdown"] = row["report_markdown"]
        return report

    def cleanup(self) -> None:
        self.store.execute(
            """
            DELETE FROM report_record
            WHERE report_id NOT IN (
                SELECT report_id FROM report_record ORDER BY created_at DESC, report_id DESC LIMIT ?
            )
            """,
            (self.max_items,),
        )
