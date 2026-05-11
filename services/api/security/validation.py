from __future__ import annotations

import html
import math
import os
import re
from typing import Any

from ml.optimization.constraints import ALLOWED_INTERVENTION_TYPES
from ml.simulation.scenario_schema import LOSS_MODES, PROPAGATION_MODES, SCENARIO_TYPES, SHOCK_TYPES, TARGET_METRICS
from services.api.runtime.errors import ControlledApiError


DEFAULT_MAX_REQUEST_BYTES = 256 * 1024
MAX_TEXT_LENGTH = 2000
MAX_LIST_ITEMS = 64
REPORT_FORMATS = {"json", "markdown"}
UNSAFE_PHRASES = (
    "by" + "pass",
    "circum" + "vent",
    "evad" + "e",
    "evad" + "ing",
    "disguise",
    "illegal rerout" + "ing",
    "workaround sanctions",
    "avoid export controls",
)
SECRET_VALUE_PATTERNS = (
    re.compile(r"(?i)\b(?:api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9._\-]{8,}"),
    re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9._\-]{8,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{12,}"),
)


def max_request_bytes() -> int:
    try:
        value = int(os.getenv("SUPPLY_RISK_MAX_REQUEST_BYTES", str(DEFAULT_MAX_REQUEST_BYTES)))
    except ValueError:
        return DEFAULT_MAX_REQUEST_BYTES
    return max(1024, min(value, 4 * 1024 * 1024))


def validate_request_size(content_length: str | None) -> None:
    if not content_length:
        return
    try:
        size = int(content_length)
    except ValueError:
        return
    if size > max_request_bytes():
        raise ControlledApiError(
            "request_too_large",
            "Request body exceeds the configured API size limit.",
            field="body",
        )


def validate_forward_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    clean = sanitize_payload(payload or {})
    _require_enum(clean, "scenario_type", SCENARIO_TYPES, "forward_scenario_validation_error")
    targets = clean.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ControlledApiError("forward_scenario_validation_error", "targets must be a non-empty list.", "targets")
    if len(targets) > 10:
        raise ControlledApiError("forward_scenario_validation_error", "targets must contain at most 10 entries.", "targets")
    clean["targets"] = [_bounded_text(item, field="targets") for item in targets]
    _int_guard(clean, "iterations", maximum=5000, code="forward_scenario_validation_error")
    if "loss_mode" in clean:
        _require_enum(clean, "loss_mode", LOSS_MODES, "forward_scenario_validation_error")
    if "propagation_mode" in clean:
        _require_enum(clean, "propagation_mode", PROPAGATION_MODES, "forward_scenario_validation_error")
    return clean


def validate_reverse_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    clean = sanitize_payload(payload or {})
    _require_enum(clean, "target_metric", TARGET_METRICS, "reverse_scenario_validation_error")
    threshold = _finite_float(clean.get("failure_threshold", 35), "failure_threshold", "reverse_scenario_validation_error")
    if threshold < 0:
        raise ControlledApiError("reverse_scenario_validation_error", "failure_threshold must be non-negative.", "failure_threshold")
    if threshold > 100:
        raise ControlledApiError("reverse_scenario_validation_error", "failure_threshold must be <= 100.", "failure_threshold")
    _int_guard(clean, "max_combination_size", maximum=4, code="reverse_scenario_validation_error")
    _int_guard(clean, "beam_width", maximum=20, code="reverse_scenario_validation_error")
    _int_guard(clean, "iterations_per_candidate", maximum=1000, code="reverse_scenario_validation_error")
    if "loss_mode" in clean:
        _require_enum(clean, "loss_mode", LOSS_MODES, "reverse_scenario_validation_error")
    if "propagation_mode" in clean:
        _require_enum(clean, "propagation_mode", PROPAGATION_MODES, "reverse_scenario_validation_error")
    for key in ("allowed_shock_types", "forbidden_shock_types"):
        if key in clean:
            values = clean[key]
            if not isinstance(values, list):
                raise ControlledApiError("reverse_scenario_validation_error", f"{key} must be a list.", key)
            unknown = [item for item in values if str(item) not in SHOCK_TYPES]
            if unknown:
                raise ControlledApiError("reverse_scenario_validation_error", f"{key} contains unsupported values.", key)
    return clean


def validate_optimization_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    clean = sanitize_payload(payload or {})
    budget = _finite_float(clean.get("budget", 100), "budget", "optimization_validation_error")
    if budget < 0:
        raise ControlledApiError("optimization_validation_error", "budget must be non-negative.", "budget")
    clean["budget"] = budget
    _int_guard(clean, "max_actions", maximum=10, code="optimization_validation_error")
    allowed = clean.get("allowed_intervention_types")
    if allowed is not None:
        if not isinstance(allowed, list):
            raise ControlledApiError("optimization_validation_error", "allowed_intervention_types must be a list.", "allowed_intervention_types")
        unknown = [item for item in allowed if str(item) not in ALLOWED_INTERVENTION_TYPES]
        if unknown:
            raise ControlledApiError("optimization_validation_error", "allowed_intervention_types contains unsupported values.", "allowed_intervention_types")
    clean["compliance_constraints"] = {
        "no_export_control_evasion": True,
        "no_sanctions_circumvention": True,
    }
    return clean


def validate_report_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    clean = sanitize_payload(payload or {})
    report_format = str(clean.get("format") or "json").lower()
    if report_format not in REPORT_FORMATS:
        raise ControlledApiError("report_validation_error", "format must be json or markdown.", "format")
    clean["format"] = report_format
    return clean


def sanitized_payload(value: Any) -> Any:
    return sanitize_payload(value)


def sanitize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): sanitize_payload(item)
            for key, item in value.items()
            if _allowed_key(str(key))
        }
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value[:MAX_LIST_ITEMS]]
    if isinstance(value, str):
        return _bounded_text(value, field="text")
    return value


def _allowed_key(key: str) -> bool:
    lowered = key.lower()
    if lowered in {"raw_payload_excluded", "private_diagnostics_excluded"}:
        return True
    blocked = ("raw", "secret", "token", "api_key", "private_diagnostic")
    return not any(part in lowered for part in blocked)


def _bounded_text(value: Any, *, field: str) -> str:
    text = html.escape(str(value), quote=True).strip()
    if len(text) > MAX_TEXT_LENGTH:
        raise ControlledApiError("request_text_too_long", "Text input exceeds the configured length limit.", field=field)
    lowered = text.lower()
    if any(phrase in lowered for phrase in UNSAFE_PHRASES):
        raise ControlledApiError(
            "unsafe_compliance_language",
            "Request includes unsafe compliance-language.",
            field=field,
        )
    if _looks_secret_like(text):
        return "[redacted]"
    return text


def _looks_secret_like(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_VALUE_PATTERNS)


def _require_enum(payload: dict[str, Any], field: str, allowed: set[str], code: str) -> None:
    value = str(payload.get(field) or "").strip()
    if value not in allowed:
        raise ControlledApiError(code, f"{field} is not supported.", field=field)
    payload[field] = value


def _int_guard(payload: dict[str, Any], field: str, *, maximum: int, code: str) -> None:
    value = payload.get(field)
    if value is None:
        return
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ControlledApiError(code, f"{field} must be an integer.", field=field) from exc
    if parsed < 1:
        raise ControlledApiError(code, f"{field} must be >= 1.", field=field)
    if parsed > maximum:
        raise ControlledApiError(code, f"{field} must be <= {maximum}.", field=field)
    payload[field] = parsed


def _finite_float(value: Any, field: str, code: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ControlledApiError(code, f"{field} must be numeric.", field=field) from exc
    if not math.isfinite(parsed):
        raise ControlledApiError(code, f"{field} must be finite.", field=field)
    return parsed
