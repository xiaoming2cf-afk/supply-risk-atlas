"""Dependency-free baseline model skeletons."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .dataset import DatasetRecord


FeatureRow = Mapping[str, float]


@dataclass
class MajorityClassClassifier:
    positive_prior_: float = 0.0
    class_: int = 0
    fitted_: bool = False

    def fit(self, records: Iterable[DatasetRecord]) -> "MajorityClassClassifier":
        labels = [record.label for record in records]
        if not labels:
            raise ValueError("at least one training record is required")
        positives = sum(1 for label in labels if label == 1)
        self.positive_prior_ = positives / len(labels)
        self.class_ = 1 if self.positive_prior_ >= 0.5 else 0
        self.fitted_ = True
        return self

    def predict(self, rows: Sequence[FeatureRow]) -> tuple[int, ...]:
        self._require_fit()
        return tuple(self.class_ for _row in rows)

    def predict_proba(self, rows: Sequence[FeatureRow]) -> tuple[float, ...]:
        self._require_fit()
        return tuple(self.positive_prior_ for _row in rows)

    def _require_fit(self) -> None:
        if not self.fitted_:
            raise RuntimeError("model must be fitted before prediction")


@dataclass
class FeatureThresholdClassifier:
    feature_name: str
    threshold: float = 0.0
    direction: str = "gte"
    fitted_: bool = False

    def fit(self, records: Iterable[DatasetRecord]) -> "FeatureThresholdClassifier":
        values = [record.features[self.feature_name] for record in records if self.feature_name in record.features]
        if not values:
            raise ValueError(f"feature {self.feature_name!r} was not present in training records")
        sorted_values = sorted(values)
        self.threshold = sorted_values[len(sorted_values) // 2]
        self.fitted_ = True
        return self

    def predict(self, rows: Sequence[FeatureRow]) -> tuple[int, ...]:
        self._require_fit()
        return tuple(self._score(row) for row in rows)

    def predict_proba(self, rows: Sequence[FeatureRow]) -> tuple[float, ...]:
        self._require_fit()
        return tuple(float(self._score(row)) for row in rows)

    def _score(self, row: FeatureRow) -> int:
        value = float(row.get(self.feature_name, 0.0))
        if self.direction == "gte":
            return int(value >= self.threshold)
        if self.direction == "lte":
            return int(value <= self.threshold)
        raise ValueError("direction must be 'gte' or 'lte'")

    def _require_fit(self) -> None:
        if not self.fitted_:
            raise RuntimeError("model must be fitted before prediction")
