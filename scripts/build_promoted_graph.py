from __future__ import annotations

import argparse
import json
from pathlib import Path

from graph_kernel.promoted_pipeline import build_promoted_graph, default_output_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Build promoted public-evidence graph artifacts.")
    parser.add_argument(
        "--output-dir",
        default=str(default_output_dir()),
        help="Directory for manifest.json, graph_snapshot.json, and source_status.json.",
    )
    parser.add_argument(
        "--store-sqlite",
        action="store_true",
        help="Also store sanitized snapshot/index rows in the configured SQLite store.",
    )
    parser.add_argument("--sqlite-path", default=None, help="Optional SQLite path for --store-sqlite.")
    args = parser.parse_args()

    result = build_promoted_graph(
        output_dir=Path(args.output_dir),
        store_sqlite=args.store_sqlite,
        sqlite_path=args.sqlite_path,
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "graph_version": result.snapshot.graph_version,
                "source_manifest_id": result.snapshot.source_manifest_id,
                "node_count": result.snapshot.node_count,
                "edge_count": result.snapshot.edge_count,
                "output_dir": str(result.output_dir),
                "warnings": result.manifest["warnings"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
