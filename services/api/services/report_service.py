from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
import os
from typing import Any

from sra_core.api.envelope import make_envelope, make_error_envelope
from sra_core.reports.investigation import REPORT_VERSION, generate_investigation_report
from services.api.runtime.run_store import sanitized_run_copy
from services.api.runtime.errors import ControlledApiError
from services.api.security.validation import sanitized_payload, validate_report_payload
from services.api.services.common import semiconductor_metadata
from services.api.services.run_service import RUN_CACHE
from services.api.services.semiconductor_snapshot_cache import fixture_snapshot_for_services
from services.api.storage.report_store import ReportStore
from services.api.storage.sqlite_store import SQLiteStore, configured_storage_mode
from sra_core.contracts.semiconductor import payload_hash


class MemoryReportStore:
    def __init__(self, max_items: int = 128) -> None:
        self.max_items = max(1, max_items)
        self._items: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def put_report(self, report: dict[str, Any], *, markdown: str | None = None) -> dict[str, Any] | None:
        clean = sanitized_run_copy(report)
        report_id = str(clean.get("report_id") or "")
        if not report_id:
            return None
        if markdown is not None:
            clean["markdown"] = sanitized_run_copy(markdown)
        clean["raw_payload_excluded"] = True
        clean["private_diagnostics_excluded"] = True
        clean["content_hash"] = payload_hash(clean)
        clean.setdefault("data_mode", "fixture")
        clean.setdefault("graph_mode", "fixture")
        self._items[report_id] = deepcopy(clean)
        self._items.move_to_end(report_id)
        self.cleanup()
        return deepcopy(clean)

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        item = self._items.get(report_id)
        return deepcopy(item) if item is not None else None

    def cleanup(self) -> None:
        while len(self._items) > self.max_items:
            self._items.popitem(last=False)

    def clear(self) -> None:
        self._items.clear()


def _report_store_size() -> int:
    try:
        configured = int(os.getenv("SUPPLY_RISK_REPORT_STORE_SIZE", "128"))
    except ValueError:
        return 128
    return max(1, min(configured, 512))


def build_report_store() -> MemoryReportStore | ReportStore:
    if configured_storage_mode() == "sqlite":
        return ReportStore(SQLiteStore(), max_items=_report_store_size())
    return MemoryReportStore(max_items=_report_store_size())


REPORT_STORE = build_report_store()


def route_investigation_report(
    payload: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        payload = validate_report_payload(payload)
        snapshot = fixture_snapshot_for_services()
        result = sanitized_payload(generate_investigation_report(payload))
    except ControlledApiError as exc:
        return make_error_envelope(
            exc.code,
            str(exc),
            metadata=semiconductor_metadata(feature_version=REPORT_VERSION),
            request_id=request_id,
            field=exc.field,
            warnings=["fixture_graph:not_production_ready"],
        )
    except Exception as exc:
        return make_error_envelope(
            "investigation_report_unavailable",
            "Investigation report could not be generated from the SemiRisk fixture graph.",
            metadata=semiconductor_metadata(feature_version=REPORT_VERSION),
            request_id=request_id,
            warnings=[
                f"report_failed:{type(exc).__name__}",
                "fixture_graph:not_production_ready",
            ],
        )
    response = make_envelope(
        result,
        metadata=semiconductor_metadata(snapshot, feature_version=REPORT_VERSION),
        request_id=request_id,
        warnings=result.get("warnings", ["fixture_graph:not_production_ready"]),
    )
    RUN_CACHE.put_summary("investigation_report", response)
    REPORT_STORE.put_report(result, markdown=result.get("markdown"))
    return response


def route_report_detail(report_id: str, request_id: str | None = None) -> dict[str, Any]:
    snapshot = fixture_snapshot_for_services()
    report = REPORT_STORE.get_report(report_id)
    if report is None:
        raise LookupError(f"Report not found: {report_id}")
    payload = {
        **report,
        "graph_version": report.get("graph_version") or _nested_get(report, "versions", "graph_version") or snapshot.graph_version,
        "source_manifest_id": report.get("source_manifest_id")
        or _nested_get(report, "versions", "source_manifest_id")
        or snapshot.source_manifest_id,
        "data_mode": report.get("data_mode") or "fixture",
        "graph_mode": report.get("graph_mode") or "fixture",
        "storage_mode": configured_storage_mode(),
        "raw_payload_excluded": True,
        "private_diagnostics_excluded": True,
        "warnings": sorted(set([*report.get("warnings", []), "fixture_graph:not_production_ready"])),
    }
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=REPORT_VERSION),
        request_id=request_id,
        warnings=payload["warnings"],
    )


def _nested_get(data: dict[str, Any], parent: str, key: str) -> Any:
    nested = data.get(parent)
    return nested.get(key) if isinstance(nested, dict) else None
