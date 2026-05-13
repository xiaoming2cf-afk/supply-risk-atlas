from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def promoted_graph_version(value: Any) -> str:
    return f"promoted_public_evidence_v0_1_{stable_hash(value)[:16]}"


def source_manifest_id(value: Any) -> str:
    return f"public_evidence_manifest_{stable_hash(value)[:16]}"

