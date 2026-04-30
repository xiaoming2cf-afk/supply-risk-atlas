"""Namespace shim for local, non-installed development.

The actual source package lives in `packages/sra_core/sra_core`. This shim lets
plain `python` and ASGI servers import `sra_core` from the repository root
without requiring a successful editable install first.
"""

from __future__ import annotations

from pathlib import Path

_REAL_PACKAGE = Path(__file__).resolve().parents[1] / "packages" / "sra_core" / "sra_core"
if str(_REAL_PACKAGE) not in __path__:
    __path__.append(str(_REAL_PACKAGE))

from sra_core.contracts.domain import (  # noqa: E402,F401
    ApiEnvelope,
    CanonicalEntity,
    EdgeEvent,
    EdgeState,
    FeatureValue,
    GraphSnapshot,
    LabelValue,
    PredictionResult,
    VersionMetadata,
)

__all__ = [
    "ApiEnvelope",
    "CanonicalEntity",
    "EdgeEvent",
    "EdgeState",
    "FeatureValue",
    "GraphSnapshot",
    "LabelValue",
    "PredictionResult",
    "VersionMetadata",
]
