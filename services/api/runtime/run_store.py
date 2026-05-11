from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock
from typing import Any


RUN_STORE_VERSION = "semirisk_run_store_v0.1"
SENSITIVE_KEY_PARTS = (
    "raw",
    "payload",
    "secret",
    "token",
    "api_key",
    "authorization",
    "cookie",
    "password",
    "private_diagnostic",
)


def sanitized_run_copy(value: Any) -> Any:
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                continue
            clean[str(key)] = sanitized_run_copy(item)
        return clean
    if isinstance(value, list):
        return [sanitized_run_copy(item) for item in value[:64]]
    if isinstance(value, tuple):
        return [sanitized_run_copy(item) for item in value[:64]]
    return deepcopy(value)


class RunStore:
    def __init__(self, max_items: int = 32) -> None:
        self.max_items = max(1, max_items)
        self._items: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._lock = Lock()

    def put_summary(self, run_type: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        if not isinstance(data, dict):
            return None
        run_id = str(data.get("run_id") or data.get("report_id") or "")
        if not run_id:
            return None
        summary = {
            "run_id": run_id,
            "run_type": run_type,
            "created_at": data.get("timestamp") or data.get("generated_at") or _utc_now(),
            "graph_version": data.get("graph_version") or _nested_get(data, "versions", "graph_version"),
            "source_manifest_id": data.get("source_manifest_id") or _nested_get(data, "versions", "source_manifest_id"),
            "status": payload.get("status", "success"),
            "warnings": sanitized_run_copy(payload.get("warnings") or data.get("warnings") or []),
            "summary": _summary_for_run(data),
            "evidence_refs": sanitized_run_copy(data.get("evidence_refs", []))[:20],
            "versions": {
                "model_version": data.get("model_version"),
                "feature_version": data.get("feature_version") or _nested_get(data, "versions", "feature_version"),
                "simulation_version": data.get("simulation_version") or _nested_get(data, "versions", "simulation_version"),
                "optimization_version": data.get("optimization_version") or _nested_get(data, "versions", "optimization_version"),
                "report_version": data.get("report_version") or _nested_get(data, "versions", "report_version"),
            },
            "fixture_limitations": [
                "fixture_graph:not_production_ready",
                "sanitized_summary_only",
                "source_inputs_and_private_diagnostics_excluded",
            ],
        }
        clean = sanitized_run_copy(summary)
        with self._lock:
            self._items[run_id] = clean
            self._items.move_to_end(run_id)
            while len(self._items) > self.max_items:
                self._items.popitem(last=False)
            return deepcopy(clean)

    def list_summaries(self) -> list[dict[str, Any]]:
        with self._lock:
            return [deepcopy(item) for item in reversed(self._items.values())]

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            item = self._items.get(run_id)
            return deepcopy(item) if item is not None else None

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


def _summary_for_run(data: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "scenario_type",
        "target_metric",
        "expected_loss",
        "p50_loss",
        "p90_loss",
        "p95_loss",
        "cvar_95",
        "cvar95",
        "before_expected_loss",
        "after_expected_loss",
        "before_cvar95",
        "after_cvar95",
        "cost",
        "budget",
        "resilience_roi",
        "format",
        "calibration_status",
        "fixture_label",
        "loss_mode",
        "propagation_mode",
        "threshold_metric_basis",
        "optimization_context_type",
        "scenario_count",
    ]
    summary = {key: data.get(key) for key in keys if key in data}
    for count_key in ("affected_nodes", "top_transmission_paths", "ranked_shock_sets", "recommended_actions", "evidence_summary"):
        if isinstance(data.get(count_key), list):
            summary[f"{count_key}_count"] = len(data[count_key])
    return sanitized_run_copy(summary)


def _nested_get(data: dict[str, Any], parent: str, key: str) -> Any:
    nested = data.get(parent)
    if isinstance(nested, dict):
        return nested.get(key)
    return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
