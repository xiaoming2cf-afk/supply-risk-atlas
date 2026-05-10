from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from sra_core.contracts.semiconductor import (
    SemiconductorRawRecord,
    SemiconductorSourceId,
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[5]


def default_fixture_dir() -> Path:
    return project_root() / "tests" / "ingestion" / "fixtures"


def default_registry_path() -> Path:
    return project_root() / "configs" / "sources" / "semiconductor.yaml"


def load_semiconductor_registry(path: str | Path | None = None) -> dict[str, Any]:
    registry_path = Path(path) if path else default_registry_path()
    return yaml.safe_load(registry_path.read_text(encoding="utf-8"))


def source_terms_ref(source_id: str, registry_path: str | Path | None = None) -> str:
    registry = load_semiconductor_registry(registry_path)
    for source in registry.get("sources", []):
        if source.get("source_id") == source_id:
            return str(source.get("terms_url") or source.get("source_url") or source_id)
    return source_id


@dataclass(frozen=True)
class SemiconductorFixtureConnector:
    source_id: SemiconductorSourceId
    fixture_file: str

    def load_fixture(self, fixture_dir: str | Path | None = None) -> dict[str, Any]:
        path = Path(fixture_dir) if fixture_dir else default_fixture_dir()
        payload = json.loads((path / self.fixture_file).read_text(encoding="utf-8"))
        if payload.get("source_id") != self.source_id:
            raise ValueError(
                f"fixture source_id mismatch for {self.fixture_file}: {payload.get('source_id')}"
            )
        return payload

    def replay(
        self,
        *,
        fixture_dir: str | Path | None = None,
        registry_path: str | Path | None = None,
    ) -> list[SemiconductorRawRecord]:
        fixture = self.load_fixture(fixture_dir)
        terms_ref = source_terms_ref(self.source_id, registry_path)
        rows = fixture.get("records", [])
        if not isinstance(rows, list):
            raise ValueError(f"fixture records must be a list: {self.fixture_file}")
        return [
            SemiconductorRawRecord.from_fixture(
                source_id=self.source_id,
                row=row,
                license_or_terms_ref=terms_ref,
            )
            for row in rows
        ]
