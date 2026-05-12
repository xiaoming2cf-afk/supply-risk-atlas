from __future__ import annotations

import json
from typing import Any

from sra_core.contracts.semiconductor import payload_hash
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
        clean_markdown = sanitized_run_copy(markdown) if markdown is not None else None
        content_hash = payload_hash({"report": clean, "markdown": clean_markdown})
        self.store.execute(
            """
            INSERT OR REPLACE INTO report_record
            (report_id, report_run_id, created_at, format, graph_version, source_manifest_id,
             report_json, report_markdown, content_hash, warnings_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                clean.get("report_run_id"),
                str(clean.get("generated_at") or ""),
                str(clean.get("format") or ("markdown" if clean_markdown else "json")),
                versions.get("graph_version") or clean.get("graph_version"),
                versions.get("source_manifest_id") or clean.get("source_manifest_id"),
                _json(clean),
                clean_markdown,
                content_hash,
                _json(clean.get("warnings", [])),
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
        report["content_hash"] = row["content_hash"]
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


def _json(value: Any) -> str:
    return json.dumps(sanitized_run_copy(value), sort_keys=True)
