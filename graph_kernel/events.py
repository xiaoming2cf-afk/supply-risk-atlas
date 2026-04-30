"""Temporal edge events and deterministic state materialization."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping


Action = str


def _canonical_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical_value(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, set):
        return sorted(_canonical_value(item) for item in value)
    return value


def _frozen_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    normalized = _canonical_value(value or {})
    return MappingProxyType(normalized)


def _stable_hash(payload: Mapping[str, Any]) -> str:
    body = json.dumps(_canonical_value(payload), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclass(frozen=True, order=True)
class EdgeKey:
    """Stable identity for a directed typed edge."""

    source: str
    target: str
    kind: str

    def __post_init__(self) -> None:
        if not self.source or not self.target or not self.kind:
            raise ValueError("source, target, and kind are required")

    def as_tuple(self) -> tuple[str, str, str]:
        return (self.source, self.target, self.kind)


@dataclass(frozen=True)
class EdgeEvent:
    """An append-only fact about an edge.

    ``observed_at`` is the time the platform learned the fact. ``effective_at``
    is when the fact became true in the external world. Materialization requires
    both timestamps to be at or before the requested cutoff.
    """

    source: str
    target: str
    kind: str
    action: Action
    effective_at: int
    observed_at: int
    attrs: Mapping[str, Any] = field(default_factory=dict)
    sequence: int = 0
    event_id: str | None = None

    def __post_init__(self) -> None:
        EdgeKey(self.source, self.target, self.kind)
        if self.action not in {"upsert", "delete"}:
            raise ValueError(f"unsupported edge action: {self.action}")
        if self.effective_at < 0 or self.observed_at < 0:
            raise ValueError("effective_at and observed_at must be non-negative")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        object.__setattr__(self, "attrs", _frozen_mapping(self.attrs))

    @property
    def key(self) -> EdgeKey:
        return EdgeKey(self.source, self.target, self.kind)

    @property
    def stable_event_id(self) -> str:
        if self.event_id:
            return self.event_id
        return _stable_hash(
            {
                "source": self.source,
                "target": self.target,
                "kind": self.kind,
                "action": self.action,
                "effective_at": self.effective_at,
                "observed_at": self.observed_at,
                "attrs": self.attrs,
                "sequence": self.sequence,
            }
        )

    def sort_key(self) -> tuple[int, int, int, str, tuple[str, str, str]]:
        return (
            self.observed_at,
            self.effective_at,
            self.sequence,
            self.stable_event_id,
            self.key.as_tuple(),
        )


@dataclass(frozen=True)
class EdgeState:
    """Latest materialized state for an edge key at a cutoff."""

    key: EdgeKey
    active: bool
    effective_at: int
    observed_at: int
    attrs: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "attrs", _frozen_mapping(self.attrs))


def materialize_edge_state(
    events: Iterable[EdgeEvent],
    as_of: int,
    *,
    include_inactive: bool = False,
) -> dict[EdgeKey, EdgeState]:
    """Return the latest deterministic edge state visible at ``as_of``.

    Events with ``observed_at`` after the cutoff are invisible even if their
    ``effective_at`` is in the past. Events with ``effective_at`` after the
    cutoff are also withheld because they were not true yet at the snapshot
    time.
    """

    if as_of < 0:
        raise ValueError("as_of must be non-negative")

    states: dict[EdgeKey, EdgeState] = {}
    for event in sorted(events, key=lambda item: item.sort_key()):
        if event.observed_at > as_of or event.effective_at > as_of:
            continue
        states[event.key] = EdgeState(
            key=event.key,
            active=event.action == "upsert",
            effective_at=event.effective_at,
            observed_at=event.observed_at,
            attrs=event.attrs if event.action == "upsert" else {},
            event_id=event.stable_event_id,
        )

    if include_inactive:
        return dict(sorted(states.items(), key=lambda item: item[0].as_tuple()))
    return {
        key: state
        for key, state in sorted(states.items(), key=lambda item: item[0].as_tuple())
        if state.active
    }
