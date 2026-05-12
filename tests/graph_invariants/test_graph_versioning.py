from __future__ import annotations

from graph_kernel.graph_versioning import canonical_graph_hash, deterministic_graph_version


def test_canonical_graph_hash_is_deterministic() -> None:
    first = canonical_graph_hash({"b": [2, 1], "a": {"x": True}})
    second = canonical_graph_hash({"a": {"x": True}, "b": [2, 1]})

    assert first == second
    assert len(first) == 64


def test_deterministic_graph_version_changes_when_payload_changes() -> None:
    first = deterministic_graph_version(
        namespace="test_graph",
        as_of_time="2026-05-01T00:00:00Z",
        graph_payload={"nodes": ["a"], "edges": []},
    )
    second = deterministic_graph_version(
        namespace="test_graph",
        as_of_time="2026-05-01T00:00:00Z",
        graph_payload={"nodes": ["a"], "edges": ["edge:a:b"]},
    )

    assert first.startswith("test_graph_20260501T000000Z_")
    assert first != second
