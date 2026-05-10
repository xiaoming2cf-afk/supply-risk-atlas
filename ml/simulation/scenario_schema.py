from __future__ import annotations

import math
import random
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


DEFAULT_SIMULATION_AS_OF_TIME = "2026-05-01T00:00:00Z"
FORWARD_SIMULATION_VERSION = "semirisk_forward_mc_v0.1"
REVERSE_SIMULATION_VERSION = "semirisk_reverse_stress_v0.1"
FIXTURE_GRAPH_WARNING = "fixture_graph:not_production_ready"
MAX_FORWARD_ITERATIONS = 5000

SCENARIO_TYPES = {
    "earthquake",
    "export_control",
    "material_shortage",
    "demand_spike",
    "port_disruption",
    "factory_shutdown",
    "cyber_incident",
    "power_outage",
}

SCENARIO_MULTIPLIERS = {
    "earthquake": 1.08,
    "export_control": 1.18,
    "material_shortage": 1.04,
    "demand_spike": 0.88,
    "port_disruption": 0.96,
    "factory_shutdown": 1.12,
    "cyber_incident": 0.86,
    "power_outage": 0.9,
}


class ScenarioValidationError(ValueError):
    def __init__(self, message: str, *, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field


def normalize_forward_request(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = dict(payload or {})
    scenario_type = str(raw.get("scenario_type") or "").strip()
    if scenario_type not in SCENARIO_TYPES:
        raise ScenarioValidationError(f"invalid scenario_type: {scenario_type or 'missing'}", field="scenario_type")
    targets = raw.get("targets")
    if not isinstance(targets, list) or not all(str(item).strip() for item in targets):
        raise ScenarioValidationError("targets must be a non-empty list of node IDs or selectors", field="targets")
    iterations = _int(raw.get("iterations"), 1000)
    if iterations < 1:
        raise ScenarioValidationError("iterations must be >= 1", field="iterations")
    if iterations > MAX_FORWARD_ITERATIONS:
        raise ScenarioValidationError(f"iterations must be <= {MAX_FORWARD_ITERATIONS}", field="iterations")
    seed = _int(raw.get("seed"), 42)
    assumptions = raw.get("assumptions") if isinstance(raw.get("assumptions"), list) else []
    return {
        "scenario_type": scenario_type,
        "targets": [str(item).strip() for item in targets],
        "severity_distribution": normalize_distribution(
            raw.get("severity_distribution"),
            default={"type": "fixed", "params": {"value": 0.72}},
            field="severity_distribution",
        ),
        "duration_days_distribution": normalize_distribution(
            raw.get("duration_days_distribution"),
            default={"type": "fixed", "params": {"value": 28}},
            field="duration_days_distribution",
        ),
        "iterations": iterations,
        "seed": seed,
        "as_of_time": normalize_time(raw.get("as_of_time")),
        "graph_version": raw.get("graph_version"),
        "assumptions": [str(item)[:240] for item in assumptions],
    }


def normalize_distribution(
    value: Any,
    *,
    default: dict[str, Any],
    field: str,
) -> dict[str, Any]:
    if value is None:
        return default
    if not isinstance(value, dict):
        raise ScenarioValidationError(f"{field} must be an object", field=field)
    kind = str(value.get("type") or "").strip().lower()
    params = value.get("params") if isinstance(value.get("params"), dict) else {}
    allowed = {"fixed", "constant", "triangular", "beta", "uniform", "normal", "bounded_normal", "lognormal"}
    if kind not in allowed:
        raise ScenarioValidationError(f"invalid {field}.type: {kind or 'missing'}", field=field)
    return {"type": "fixed" if kind == "constant" else kind, "params": dict(params)}


def sample_distribution(spec: dict[str, Any], rng: random.Random, *, default: float) -> float:
    kind = str(spec.get("type") or "fixed")
    params = spec.get("params") if isinstance(spec.get("params"), dict) else {}
    if kind == "fixed":
        return float(params.get("value", default))
    if kind == "uniform":
        low, high = _low_high(params, default)
        return rng.uniform(low, high)
    if kind == "triangular":
        low, high = _low_high(params, default)
        mode = float(params.get("mode", (low + high) / 2.0))
        return rng.triangular(low, high, max(low, min(high, mode)))
    if kind == "beta":
        alpha = max(0.01, float(params.get("alpha", 2.0)))
        beta = max(0.01, float(params.get("beta", 2.0)))
        scale = float(params.get("scale", 1.0))
        loc = float(params.get("loc", 0.0))
        return loc + rng.betavariate(alpha, beta) * scale
    if kind in {"normal", "bounded_normal"}:
        mean = float(params.get("mean", default))
        stdev = max(0.0, float(params.get("stdev", params.get("stddev", 0.0))))
        low = float(params.get("min", mean - 3.0 * stdev))
        high = float(params.get("max", mean + 3.0 * stdev))
        return max(min(low, high), min(max(low, high), rng.gauss(mean, stdev)))
    if kind == "lognormal":
        mean = float(params.get("mean", math.log(max(default, 1.0))))
        sigma = max(0.0, float(params.get("sigma", 0.15)))
        low = float(params.get("min", 1.0))
        high = float(params.get("max", max(default * 4.0, low)))
        return max(min(low, high), min(max(low, high), rng.lognormvariate(mean, sigma)))
    return default


def normalize_severity(value: float) -> float:
    severity = float(value)
    if severity > 1.0:
        severity /= 100.0
    return max(0.0, min(1.0, severity))


def normalize_time(value: Any) -> str:
    if value in {None, ""}:
        return DEFAULT_SIMULATION_AS_OF_TIME
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    else:
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ScenarioValidationError("as_of_time must be an ISO timestamp", field="as_of_time") from exc
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_run_id(prefix: str, payload: Any) -> str:
    digest = sha256(stable_material(payload).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def stable_material(value: Any) -> str:
    if isinstance(value, dict):
        return "{" + ",".join(f"{key}:{stable_material(value[key])}" for key in sorted(value)) + "}"
    if isinstance(value, list):
        return "[" + ",".join(stable_material(item) for item in value) + "]"
    return str(value)


def _low_high(params: dict[str, Any], default: float) -> tuple[float, float]:
    low = float(params.get("min", default))
    high = float(params.get("max", low))
    return min(low, high), max(low, high)


def _int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

