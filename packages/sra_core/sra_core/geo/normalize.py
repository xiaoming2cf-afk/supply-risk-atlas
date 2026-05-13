from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from sra_core.geo.terminology import (
    CANONICAL_DISPLAY,
    CANONICAL_REGION_ID,
    COUNTRY_CONTEXT_KEYS,
    LEGACY_ID_ALIASES,
    LEGACY_LABEL_ALIASES,
    LEGACY_TEXT_REPLACEMENTS,
    PARENT_COUNTRY_DISPLAY,
    PARENT_COUNTRY_ID,
    REGION_CONTEXT_KEYS,
)


def _compact(value: str) -> str:
    return " ".join(value.strip().split())


def normalize_geo_id(value: Any) -> Any:
    if value is None:
        return value
    text = str(value)
    if text.lower() in LEGACY_ID_ALIASES:
        return CANONICAL_REGION_ID
    return sanitize_identifier(text)


def sanitize_identifier(value: str) -> str:
    text = value
    for pattern, replacement in LEGACY_TEXT_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text


def normalize_geo_label(value: Any) -> Any:
    if value is None:
        return value
    text = _compact(str(value))
    if text.lower() in LEGACY_LABEL_ALIASES or text.lower() in LEGACY_ID_ALIASES:
        return CANONICAL_DISPLAY
    return sanitize_api_visible_text(text)


def normalize_country_context(value: Any) -> dict[str, str]:
    normalized = normalize_geo_label(value)
    if normalized == CANONICAL_DISPLAY:
        return {
            "country_id": PARENT_COUNTRY_ID,
            "country_display": PARENT_COUNTRY_DISPLAY,
            "region_id": CANONICAL_REGION_ID,
            "region_display": CANONICAL_DISPLAY,
        }
    return {
        "country_id": str(value) if value is not None else "",
        "country_display": str(value) if value is not None else "",
    }


def sanitize_api_visible_text(value: Any) -> str:
    text = "" if value is None else str(value)
    for pattern, replacement in LEGACY_TEXT_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return " ".join(text.split())


def sanitize_report_text(text: Any) -> str:
    return sanitize_api_visible_text(text)


def sanitize_source_summary(summary: Any) -> str:
    return sanitize_api_visible_text(summary)


def sanitize_graph_node(node: Mapping[str, Any]) -> dict[str, Any]:
    result = sanitize_chart_table_payload(dict(node))
    if "node_id" in result:
        result["node_id"] = normalize_geo_id(result["node_id"])
    if result.get("node_id") == CANONICAL_REGION_ID:
        result["node_type"] = "region"
        result["canonical_name"] = CANONICAL_DISPLAY
        result["display_name"] = CANONICAL_DISPLAY
        attributes = dict(result.get("attributes") or {})
        attributes.update(
            {
                "region_id": CANONICAL_REGION_ID,
                "display_region": CANONICAL_DISPLAY,
                "country_id": PARENT_COUNTRY_ID,
                "country_display": PARENT_COUNTRY_DISPLAY,
                "country_code": "CN",
            }
        )
        result["attributes"] = attributes
    for key in ("canonical_name", "display_name", "label", "name"):
        if key in result:
            result[key] = normalize_geo_label(result[key])
    return result


def sanitize_graph_edge(edge: Mapping[str, Any]) -> dict[str, Any]:
    result = sanitize_chart_table_payload(dict(edge))
    for key in ("source_node_id", "target_node_id", "source", "target"):
        if key in result:
            result[key] = normalize_geo_id(result[key])
    if "edge_id" in result:
        result["edge_id"] = sanitize_identifier(str(result["edge_id"]))
    if "evidence_text_summary" in result:
        result["evidence_text_summary"] = sanitize_api_visible_text(result["evidence_text_summary"])
    return result


def sanitize_chart_table_payload(payload: Any) -> Any:
    if isinstance(payload, Mapping):
        return _sanitize_mapping(payload)
    if isinstance(payload, tuple):
        return tuple(sanitize_chart_table_payload(item) for item in payload)
    if isinstance(payload, list):
        return [sanitize_chart_table_payload(item) for item in payload]
    if isinstance(payload, str):
        return sanitize_api_visible_text(payload)
    return payload


def _sanitize_mapping(payload: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in payload.items():
        safe_key = sanitize_identifier(str(key))
        result[safe_key] = _sanitize_value_for_key(safe_key, value)
    return result


def _sanitize_value_for_key(key: str, value: Any) -> Any:
    if key in COUNTRY_CONTEXT_KEYS:
        if value is None:
            return None
        if str(value).strip().upper() in {"TW", "TWN"} or normalize_geo_label(value) == CANONICAL_DISPLAY:
            return "CN"
    if key in REGION_CONTEXT_KEYS and value is not None:
        normalized = normalize_geo_label(value)
        if normalized == CANONICAL_DISPLAY or str(value).strip().upper() in {"TW", "TWN"}:
            return CANONICAL_DISPLAY
    if key.endswith("_id") or key in {"id", "node_id", "source_node_id", "target_node_id"}:
        if value is None:
            return None
        return normalize_geo_id(value)
    if isinstance(value, Mapping):
        return _sanitize_mapping(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [sanitize_chart_table_payload(item) for item in value]
    if isinstance(value, str):
        return sanitize_api_visible_text(value)
    return value
