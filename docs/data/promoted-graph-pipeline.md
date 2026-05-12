# Promoted Graph Pipeline

The promoted graph pipeline builds a deterministic graph snapshot from governed fixture/public-evidence records. It does not fetch live data during import, API startup, tests, or the default build path.

Pipeline steps:

1. Load `configs/sources/semiconductor.yaml` through the source registry runtime.
2. Replay governed fixture records and fixture-first public evidence connectors.
3. Promote raw-record indexes into silver entities, silver events, market indicators, graph nodes, and graph edges.
4. Validate ontology direction and provenance through the graph quality checks.
5. Compute deterministic `source_manifest_id`, `manifest_hash`, and `graph_version`.
6. Write sanitized artifacts under `data/promoted/latest/` or a caller-provided output directory.
7. Optionally store sanitized snapshot, graph node/edge, manifest, and raw-record-index rows in SQLite.

Default output files:

- `manifest.json`
- `graph_snapshot.json`
- `source_status.json`

The files contain payload hashes, summaries, provenance URLs, terms references, graph versions, source manifests, warnings, and fixture/promoted-public-evidence limitations. They do not contain raw filing bodies, article bodies, secrets, private diagnostics, or bulk downloaded source payloads.

Runtime mode:

- `SUPPLY_RISK_GRAPH_MODE=fixture` keeps the existing fixture graph path.
- `SUPPLY_RISK_GRAPH_MODE=promoted` may serve promoted graph artifacts once the API integration gate is enabled.

The promoted graph remains research infrastructure based on fixture/proxy/promoted public evidence. It is not production ready, not a production decision engine, and not a financial-loss model.
