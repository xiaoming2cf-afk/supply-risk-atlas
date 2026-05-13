from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ResolutionResult:
    original: str
    resolved_id: str | None
    confidence: float
    method: str
    source_refs: tuple[str, ...] = field(default_factory=tuple)
    warning: str | None = None

    @property
    def resolved(self) -> bool:
        return self.resolved_id is not None and self.confidence >= 0.5

    def to_dict(self) -> dict[str, object]:
        return {
            "original": self.original,
            "resolved_id": self.resolved_id,
            "confidence": self.confidence,
            "method": self.method,
            "source_refs": list(self.source_refs),
            "warning": self.warning,
        }


def unresolved_result(original: str, *, method: str, warning: str) -> ResolutionResult:
    return ResolutionResult(
        original=original,
        resolved_id=None,
        confidence=0.0,
        method=method,
        warning=warning,
    )

