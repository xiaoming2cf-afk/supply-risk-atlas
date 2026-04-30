"""Deterministic synthetic supply graph event generation."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .events import EdgeEvent


@dataclass(frozen=True)
class SyntheticGraphSpec:
    seed: int = 17
    supplier_count: int = 6
    component_count: int = 4
    facility_count: int = 3
    days: int = 30
    disruption_rate: float = 0.3

    def __post_init__(self) -> None:
        if self.supplier_count <= 0 or self.component_count <= 0 or self.facility_count <= 0:
            raise ValueError("supplier_count, component_count, and facility_count must be positive")
        if self.days < 2:
            raise ValueError("days must be at least 2")
        if not 0.0 <= self.disruption_rate <= 1.0:
            raise ValueError("disruption_rate must be between 0 and 1")


def _supplier(index: int) -> str:
    return f"supplier:{index:03d}"


def _component(index: int) -> str:
    return f"component:{index:03d}"


def _facility(index: int) -> str:
    return f"facility:{index:03d}"


def generate_synthetic_edge_events(spec: SyntheticGraphSpec = SyntheticGraphSpec()) -> tuple[EdgeEvent, ...]:
    """Generate deterministic edge events for local tests and demos."""

    rng = random.Random(spec.seed)
    events: list[EdgeEvent] = []
    sequence = 0

    supplier_component_edges: list[tuple[str, str]] = []
    for supplier_index in range(spec.supplier_count):
        supplier = _supplier(supplier_index)
        fanout = 1 + (supplier_index % min(2, spec.component_count))
        for offset in range(fanout):
            component_index = (supplier_index + offset) % spec.component_count
            component = _component(component_index)
            supplier_component_edges.append((supplier, component))
            events.append(
                EdgeEvent(
                    source=supplier,
                    target=component,
                    kind="supplies",
                    action="upsert",
                    effective_at=0,
                    observed_at=0,
                    sequence=sequence,
                    attrs={
                        "capacity": 50 + rng.randint(0, 90),
                        "lead_time_days": 2 + rng.randint(0, 12),
                        "reliability": round(0.75 + rng.random() * 0.24, 3),
                    },
                )
            )
            sequence += 1

    for component_index in range(spec.component_count):
        component = _component(component_index)
        facility = _facility(component_index % spec.facility_count)
        events.append(
            EdgeEvent(
                source=component,
                target=facility,
                kind="used_by",
                action="upsert",
                effective_at=0,
                observed_at=0,
                sequence=sequence,
                attrs={
                    "criticality": round(0.4 + rng.random() * 0.6, 3),
                    "buffer_days": 1 + rng.randint(0, 6),
                },
            )
        )
        sequence += 1

    for supplier_index in range(spec.supplier_count):
        supplier = _supplier(supplier_index)
        facility = _facility((supplier_index * 2) % spec.facility_count)
        events.append(
            EdgeEvent(
                source=supplier,
                target=facility,
                kind="ships_to",
                action="upsert",
                effective_at=0,
                observed_at=0,
                sequence=sequence,
                attrs={
                    "lane_cost": 100 + rng.randint(0, 250),
                    "lead_time_days": 3 + rng.randint(0, 10),
                    "reliability": round(0.7 + rng.random() * 0.25, 3),
                },
            )
        )
        sequence += 1

    disruption_candidates = list(supplier_component_edges)
    rng.shuffle(disruption_candidates)
    if spec.disruption_rate > 0 and disruption_candidates:
        minimum = 1
    else:
        minimum = 0
    disruption_count = max(minimum, int(round(len(disruption_candidates) * spec.disruption_rate)))
    for supplier, component in disruption_candidates[:disruption_count]:
        day = rng.randint(1, spec.days - 1)
        events.append(
            EdgeEvent(
                source=supplier,
                target=component,
                kind="supplies",
                action="delete",
                effective_at=day,
                observed_at=day,
                sequence=sequence,
                attrs={"reason": "synthetic_disruption"},
            )
        )
        sequence += 1

    return tuple(sorted(events, key=lambda event: event.sort_key()))
