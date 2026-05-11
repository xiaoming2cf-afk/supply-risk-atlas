from __future__ import annotations

from ml.risk_scoring.weighting import (
    HEURISTIC_CALIBRATION_STATUS,
    HEURISTIC_COMPONENT_WEIGHTS,
    HEURISTIC_WEIGHT_SOURCE,
    noisy_or,
)


def test_noisy_or_accumulates_without_hard_coded_weights() -> None:
    single = noisy_or([0.4])
    combined = noisy_or([0.4, 0.4])

    assert single == 0.4
    assert combined > single
    assert round(combined, 2) == 0.64


def test_heuristic_weights_are_explicitly_unvalidated() -> None:
    assert sum(HEURISTIC_COMPONENT_WEIGHTS.values()) == 1.0
    assert HEURISTIC_WEIGHT_SOURCE == "heuristic_unvalidated"
    assert HEURISTIC_CALIBRATION_STATUS == "not_calibrated"
