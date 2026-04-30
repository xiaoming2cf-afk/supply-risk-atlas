from graph_kernel.path_index import PathIndex
from graph_kernel.snapshots import EdgeRecord, GraphSnapshot


def test_path_index_shortest_path_is_deterministic() -> None:
    snapshot = GraphSnapshot(
        as_of=0,
        nodes=("a", "b", "c", "d"),
        edges=(
            EdgeRecord("a", "c", "supplies"),
            EdgeRecord("a", "b", "supplies"),
            EdgeRecord("b", "d", "used_by"),
            EdgeRecord("c", "d", "used_by"),
        ),
    )

    path = PathIndex.from_snapshot(snapshot).shortest_path("a", "d", max_hops=2)

    assert path is not None
    assert path.nodes == ("a", "b", "d")
    assert path.edge_kinds == ("supplies", "used_by")


def test_path_index_lists_simple_paths_without_cycles() -> None:
    snapshot = GraphSnapshot(
        as_of=0,
        nodes=("a", "b", "c", "d"),
        edges=(
            EdgeRecord("a", "b", "supplies"),
            EdgeRecord("b", "a", "returns"),
            EdgeRecord("b", "d", "used_by"),
            EdgeRecord("a", "c", "supplies"),
            EdgeRecord("c", "d", "used_by"),
        ),
    )

    paths = PathIndex.from_snapshot(snapshot).paths_between("a", "d", max_hops=3)

    assert [path.nodes for path in paths] == [("a", "b", "d"), ("a", "c", "d")]
