from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from threading import Lock
from typing import Any, Callable


SENSITIVE_KEY_PARTS = ("raw", "payload", "secret", "token", "api_key", "private_diagnostic")


def sanitized_copy(value: Any) -> Any:
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                continue
            clean[str(key)] = sanitized_copy(item)
        return clean
    if isinstance(value, list):
        return [sanitized_copy(item) for item in value]
    if isinstance(value, tuple):
        return [sanitized_copy(item) for item in value]
    return deepcopy(value)


class SnapshotCache:
    def __init__(self, max_items: int = 8) -> None:
        self.max_items = max_items
        self._items: OrderedDict[str, Any] = OrderedDict()
        self._lock = Lock()

    def get_or_set(self, *, graph_version: str, as_of_time: str, factory: Callable[[], Any]) -> Any:
        key = f"{graph_version}:{as_of_time}"
        with self._lock:
            if key in self._items:
                self._items.move_to_end(key)
                return deepcopy(self._items[key])
        value = sanitized_copy(factory())
        with self._lock:
            self._items[key] = value
            self._items.move_to_end(key)
            while len(self._items) > self.max_items:
                self._items.popitem(last=False)
            return deepcopy(self._items[key])

    def keys(self) -> list[str]:
        with self._lock:
            return list(self._items)


class BoundedRunCache:
    def __init__(self, max_items: int = 32) -> None:
        self.max_items = max_items
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
            "created_at": data.get("timestamp") or data.get("generated_at"),
            "graph_version": data.get("graph_version"),
            "source_manifest_id": data.get("source_manifest_id"),
            "status": payload.get("status", "success"),
            "warnings": sanitized_copy(payload.get("warnings") or data.get("warnings") or []),
            "summary": _summary_for_run(data),
            "evidence_refs": sanitized_copy(data.get("evidence_refs", []))[:20],
            "versions": {
                "model_version": data.get("model_version"),
                "simulation_version": data.get("simulation_version"),
                "optimization_version": data.get("optimization_version"),
                "report_version": data.get("report_version"),
            },
        }
        clean = sanitized_copy(summary)
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


def _summary_for_run(data: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "expected_loss",
        "cvar_95",
        "cvar95",
        "before_expected_loss",
        "after_expected_loss",
        "before_cvar95",
        "after_cvar95",
        "cost",
        "resilience_roi",
        "format",
        "calibration_status",
        "fixture_label",
    ]
    return sanitized_copy({key: data.get(key) for key in keys if key in data})

