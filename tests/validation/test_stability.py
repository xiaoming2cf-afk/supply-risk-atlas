from __future__ import annotations

from ml.validation.stability import (
    explain_rank_disagreements,
    rank_items,
    score_deltas,
    spearman_rank_correlation,
)


def test_rank_correlation_and_deltas_are_deterministic() -> None:
    left = rank_items(
        [
            {"node_id": "a", "score": 90},
            {"node_id": "b", "score": 60},
            {"node_id": "c", "score": 30},
        ]
    )
    right = rank_items(
        [
            {"node_id": "a", "score": 30},
            {"node_id": "b", "score": 60},
            {"node_id": "c", "score": 90},
        ]
    )

    assert spearman_rank_correlation(left, right) == -1.0
    assert score_deltas(left, right)[0] == {
        "node_id": "a",
        "left_score": 90.0,
        "right_score": 30.0,
        "score_delta": -60.0,
    }
    disagreements = explain_rank_disagreements(left, right, min_rank_delta=1)
    assert disagreements[0]["node_id"] in {"a", "c"}
