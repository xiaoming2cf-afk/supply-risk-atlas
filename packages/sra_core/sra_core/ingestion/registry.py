from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from sra_core.contracts.data import SourceRegistry


def default_registry_path() -> Path:
    return Path(__file__).resolve().parents[4] / "configs" / "sources" / "default.yaml"


def load_source_registry(path: str | Path | None = None) -> SourceRegistry:
    registry_path = Path(path) if path is not None else default_registry_path()
    with registry_path.open("r", encoding="utf-8") as handle:
        payload: dict[str, Any] = yaml.safe_load(handle)
    return SourceRegistry.model_validate(payload)
