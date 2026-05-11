from __future__ import annotations

from ml.simulation.functionality import build_functionality_curve, resilience_integral_loss


def test_resilience_integral_loss_zero_when_functionality_matches_baseline() -> None:
    curve = [
        {"t": 0, "baseline_functionality": 1.0, "functionality": 1.0},
        {"t": 10, "baseline_functionality": 1.0, "functionality": 1.0},
    ]

    assert resilience_integral_loss(curve) == 0


def test_resilience_integral_loss_increases_when_recovery_is_slower() -> None:
    fast = build_functionality_curve(initial_loss=0.5, duration_days=20, recovery_rate=0.8)
    slow = build_functionality_curve(initial_loss=0.5, duration_days=20, recovery_rate=0.05)

    assert resilience_integral_loss(slow) > resilience_integral_loss(fast)
