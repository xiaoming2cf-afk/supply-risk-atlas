from __future__ import annotations

from typing import Any, Iterable


def rank_items(rows: Iterable[dict[str, Any]], *, id_key: str = "node_id", score_key: str = "score") -> list[dict[str, Any]]:
    ranked = sorted(
        rows,
        key=lambda row: (-float(row.get(score_key, 0.0)), str(row.get(id_key, ""))),
    )
    return [
        {
            **row,
            "rank": index + 1,
        }
        for index, row in enumerate(ranked)
    ]


def spearman_rank_correlation(
    left: Iterable[dict[str, Any]],
    right: Iterable[dict[str, Any]],
    *,
    id_key: str = "node_id",
    rank_key: str = "rank",
) -> float | None:
    left_ranks = {str(row[id_key]): int(row[rank_key]) for row in left if id_key in row and rank_key in row}
    right_ranks = {str(row[id_key]): int(row[rank_key]) for row in right if id_key in row and rank_key in row}
    common = sorted(set(left_ranks) & set(right_ranks))
    n = len(common)
    if n < 2:
        return None
    squared_delta_sum = sum((left_ranks[node_id] - right_ranks[node_id]) ** 2 for node_id in common)
    return round(1.0 - (6.0 * squared_delta_sum) / (n * (n * n - 1)), 6)


def score_deltas(
    left: Iterable[dict[str, Any]],
    right: Iterable[dict[str, Any]],
    *,
    id_key: str = "node_id",
    left_score_key: str = "score",
    right_score_key: str = "score",
) -> list[dict[str, Any]]:
    left_by_id = {str(row[id_key]): row for row in left if id_key in row}
    right_by_id = {str(row[id_key]): row for row in right if id_key in row}
    rows: list[dict[str, Any]] = []
    for node_id in sorted(set(left_by_id) & set(right_by_id)):
        left_score = round(float(left_by_id[node_id].get(left_score_key, 0.0)), 4)
        right_score = round(float(right_by_id[node_id].get(right_score_key, 0.0)), 4)
        rows.append(
            {
                "node_id": node_id,
                "left_score": left_score,
                "right_score": right_score,
                "score_delta": round(right_score - left_score, 4),
            }
        )
    return rows


def explain_rank_disagreements(
    left: Iterable[dict[str, Any]],
    right: Iterable[dict[str, Any]],
    *,
    id_key: str = "node_id",
    rank_key: str = "rank",
    min_rank_delta: int = 2,
) -> list[dict[str, Any]]:
    left_by_id = {str(row[id_key]): row for row in left if id_key in row}
    right_by_id = {str(row[id_key]): row for row in right if id_key in row}
    rows: list[dict[str, Any]] = []
    for node_id in sorted(set(left_by_id) & set(right_by_id)):
        left_rank = int(left_by_id[node_id][rank_key])
        right_rank = int(right_by_id[node_id][rank_key])
        rank_delta = right_rank - left_rank
        if abs(rank_delta) < min_rank_delta:
            continue
        rows.append(
            {
                "node_id": node_id,
                "left_rank": left_rank,
                "right_rank": right_rank,
                "rank_delta": rank_delta,
                "explanation": (
                    "The likelihood-impact-vulnerability proxy emphasizes evidence-backed "
                    "event/policy exposure, concentration, substitution, and propagation context, "
                    "while the heuristic baseline uses fixed manual component weights."
                ),
            }
        )
    return sorted(rows, key=lambda row: (-abs(int(row["rank_delta"])), str(row["node_id"])))

