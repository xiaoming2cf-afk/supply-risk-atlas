from __future__ import annotations

from graph_kernel.graph_versioning import promoted_graph_version, source_manifest_id, stable_hash


def test_stable_hash_is_deterministic_for_key_order() -> None:
    assert stable_hash({"b": 2, "a": 1}) == stable_hash({"a": 1, "b": 2})


def test_promoted_graph_version_changes_when_input_changes() -> None:
    first = promoted_graph_version({"nodes": ["a"], "edges": []})
    second = promoted_graph_version({"nodes": ["a", "b"], "edges": []})

    assert first.startswith("promoted_public_evidence_v0_1_")
    assert first != second


def test_source_manifest_id_is_stable_for_same_source_set() -> None:
    basis = {"sources": ["sec_edgar_lite", "gdelt_semiconductor_lite"]}

    assert source_manifest_id(basis) == source_manifest_id({"sources": list(basis["sources"])})

