from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from math import exp, isfinite

from ml.datasets.builder import DatasetSample
from sra_core.contracts.domain import PredictionResult


COUNT_FEATURE_CAPS = {
    "path_count": 8.0,
    "inbound_edge_count": 12.0,
    "outbound_edge_count": 12.0,
    "total_edge_count": 18.0,
}


def risk_level(score: float) -> str:
    if score >= 0.85:
        return "critical"
    if score >= 0.65:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"


@dataclass(frozen=True)
class BaselineRiskModel:
    model_version: str = "baseline_v0.2.0"

    def score_components(self, sample: DatasetSample) -> dict[str, float]:
        normalized_features = {
            name: _normalize_feature(name, value) for name, value in sample.node_features.items()
        }
        risk_signal = _mean(
            [
                value
                for name, value in normalized_features.items()
                if _is_risk_feature(name)
                and not _is_path_feature(name)
                and name != "incoming_risk_max"
            ]
        )
        structure_signal = _mean(
            [value for name, value in normalized_features.items() if _is_structure_feature(name)]
        )
        path_signal = _path_signal(sample, normalized_features)
        edge_signal = _normalize_feature(
            "incoming_risk_max", sample.edge_features.get("incoming_risk_max", 0.0)
        )
        evidence_signal = _mean(
            [value for name, value in normalized_features.items() if _is_evidence_feature(name)]
        )
        residual_signal = _mean(
            [
                value
                for name, value in normalized_features.items()
                if not _is_risk_feature(name)
                and not _is_structure_feature(name)
                and not _is_path_feature(name)
                and not _is_evidence_feature(name)
            ]
        )
        score = _clamp01(
            0.46 * risk_signal
            + 0.24 * edge_signal
            + 0.18 * path_signal
            + 0.08 * structure_signal
            + 0.04 * residual_signal
        )
        return {
            "risk": risk_signal,
            "edge": edge_signal,
            "path": path_signal,
            "structure": structure_signal,
            "evidence": evidence_signal,
            "residual": residual_signal,
            "score": score,
        }

    def predict(self, sample: DatasetSample, created_at: datetime | None = None) -> PredictionResult:
        components = self.score_components(sample)
        score = components["score"]
        interval = 0.18 - (0.08 * components["evidence"])
        digest = sha256(
            f"{sample.target_id}|{sample.prediction_time.isoformat()}|{self.model_version}".encode()
        ).hexdigest()[:12]
        return PredictionResult(
            prediction_id=f"pred_{digest}",
            target_id=sample.target_id,
            target_type=sample.target_type,
            prediction_time=sample.prediction_time,
            horizon=sample.horizon,
            risk_score=score,
            risk_level=risk_level(score),  # type: ignore[arg-type]
            confidence_low=max(0.0, score - interval),
            confidence_high=min(1.0, score + interval),
            model_version=self.model_version,
            graph_version=sample.graph_version,
            feature_version=sample.feature_version,
            label_version=sample.label_version,
            created_at=created_at or sample.prediction_time,
            top_drivers=_top_drivers(sample),
            top_paths=sample.path_tokens[:3],
        )


def _normalize_feature(name: str, value: float) -> float:
    value = _finite_non_negative(value)
    if name.endswith("_norm") or _is_bounded_feature(name):
        return _clamp01(value)
    if "count" in name or "degree" in name:
        return _saturating_count(value, _count_cap(name))
    return 1.0 - exp(-value / 10.0)


def _path_signal(sample: DatasetSample, normalized_features: dict[str, float]) -> float:
    path_risk = _mean(
        [
            value
            for name, value in normalized_features.items()
            if _is_path_feature(name) and ("risk" in name or "score" in name)
        ]
    )
    path_count = max(
        _mean(
            [
                value
                for name, value in normalized_features.items()
                if _is_path_feature(name) and "count" in name
            ]
        ),
        _saturating_count(float(len(sample.path_tokens)), COUNT_FEATURE_CAPS["path_count"]),
    )
    path_confidence = _mean(
        [
            value
            for name, value in normalized_features.items()
            if _is_path_feature(name) and "confidence" in name
        ]
    )
    if path_risk == 0.0:
        return 0.0
    confidence_multiplier = path_confidence if path_confidence > 0.0 else 1.0
    return _clamp01((0.75 * path_risk * confidence_multiplier) + (0.25 * path_risk * path_count))


def _top_drivers(sample: DatasetSample) -> list[str]:
    contributions: dict[str, float] = {}
    for name, value in sample.node_features.items():
        if name == "incoming_risk_max":
            continue
        normalized = _normalize_feature(name, value)
        if _is_evidence_feature(name):
            continue
        if _is_path_feature(name):
            weight = 0.18
        elif _is_risk_feature(name):
            weight = 0.46
        elif _is_structure_feature(name):
            weight = 0.08
        else:
            weight = 0.04
        contributions[name] = max(contributions.get(name, 0.0), normalized * weight)
    incoming_risk = _normalize_feature(
        "incoming_risk_max", sample.edge_features.get("incoming_risk_max", 0.0)
    )
    if incoming_risk > 0.0:
        contributions["incoming_risk_max"] = max(
            contributions.get("incoming_risk_max", 0.0), incoming_risk * 0.24
        )
    ranked = sorted(
        ((value, name) for name, value in contributions.items()),
        key=lambda item: (-item[0], item[1]),
    )
    return [name for value, name in ranked if value > 0.0][:3]


def _is_bounded_feature(name: str) -> bool:
    bounded_tokens = (
        "confidence",
        "coverage",
        "quality",
        "rate",
        "ratio",
        "reliability",
        "risk",
        "score",
        "severity",
        "share",
        "weight",
    )
    return any(token in name for token in bounded_tokens)


def _is_risk_feature(name: str) -> bool:
    if _is_evidence_feature(name):
        return False
    return any(token in name for token in ("delay", "exposure", "risk", "score", "severity"))


def _is_structure_feature(name: str) -> bool:
    return "count" in name or "degree" in name


def _is_path_feature(name: str) -> bool:
    return name.startswith("path_")


def _is_evidence_feature(name: str) -> bool:
    return any(
        token in name
        for token in ("confidence", "evidence", "quality", "reliability", "source_diversity")
    )


def _count_cap(name: str) -> float:
    for key, cap in COUNT_FEATURE_CAPS.items():
        if key in name:
            return cap
    return 16.0


def _saturating_count(value: float, cap: float) -> float:
    return _clamp01(1.0 - exp(-_finite_non_negative(value) / max(cap, 1.0)))


def _finite_non_negative(value: float) -> float:
    numeric = float(value)
    if not isfinite(numeric):
        return 0.0
    return max(0.0, numeric)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
