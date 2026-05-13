from __future__ import annotations

import argparse
from pathlib import Path

from graph_kernel.promoted_pipeline import build_promoted_artifacts, default_promoted_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Build sanitized promoted public-evidence graph.")
    parser.add_argument("--output-dir", type=Path, default=default_promoted_dir())
    parser.add_argument("--store-sqlite", action="store_true")
    args = parser.parse_args()

    artifacts = build_promoted_artifacts(output_dir=args.output_dir, store_sqlite=args.store_sqlite)
    manifest = artifacts["manifest"]
    print(
        "built promoted graph "
        f"graph_version={manifest['graph_version']} "
        f"source_manifest_id={manifest['source_manifest_id']} "
        f"output_dir={args.output_dir}"
    )


if __name__ == "__main__":
    main()
