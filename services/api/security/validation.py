from __future__ import annotations

from typing import Any


def sanitized_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): sanitized_payload(item)
            for key, item in value.items()
            if "raw" not in str(key).lower() and "secret" not in str(key).lower()
        }
    if isinstance(value, list):
        return [sanitized_payload(item) for item in value]
    if isinstance(value, str):
        return value.replace("<", "&lt;").replace(">", "&gt;")[:2000]
    return value

