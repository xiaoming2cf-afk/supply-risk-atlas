"""Future-window label generation for temporal graph datasets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from graph_kernel.events import EdgeEvent


@dataclass(frozen=True)
class LabelSpec:
    horizon: int = 7
    positive_actions: tuple[str, ...] = ("delete",)
    incident_only: bool = True

    def __post_init__(self) -> None:
        if self.horizon <= 0:
            raise ValueError("horizon must be positive")


def load_label_spec(path: str | Path) -> LabelSpec:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return LabelSpec(
        horizon=int(payload.get("horizon", LabelSpec.horizon)),
        positive_actions=tuple(payload.get("positive_actions", LabelSpec.positive_actions)),
        incident_only=bool(payload.get("incident_only", LabelSpec.incident_only)),
    )


class LabelFactory:
    """Build node labels from future-observed events only."""

    def __init__(self, spec: LabelSpec | None = None) -> None:
        self.spec = spec or LabelSpec()

    def build(
        self,
        events: Iterable[EdgeEvent],
        entity_ids: Iterable[str],
        *,
        cutoff: int,
    ) -> dict[str, int]:
        if cutoff < 0:
            raise ValueError("cutoff must be non-negative")
        entity_set = set(entity_ids)
        labels = {entity_id: 0 for entity_id in sorted(entity_set)}
        window_end = cutoff + self.spec.horizon
        for event in sorted(events, key=lambda item: item.sort_key()):
            if not cutoff < event.observed_at <= window_end:
                continue
            if event.action not in self.spec.positive_actions:
                continue
            affected = (event.source, event.target) if self.spec.incident_only else tuple(entity_set)
            for entity_id in affected:
                if entity_id in labels:
                    labels[entity_id] = 1
        return labels
