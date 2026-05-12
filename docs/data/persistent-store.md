# Persistent Research Store

SupplyRiskAtlas uses SQLite as its first durable research store. The store is for governed public-evidence metadata, graph snapshots, sanitized run summaries, and sanitized reports. It is not a raw data lake.

## Configuration

- `SUPPLY_RISK_STORAGE_MODE=memory|sqlite`
- `SUPPLY_RISK_SQLITE_PATH=data/runtime/supply_risk_atlas.db`

Local development may use SQLite when the path is writable. Tests use temporary databases. Existing in-memory run history remains available as a fallback.

## Stored Data

The schema stores source manifests, raw-record indexes, silver entities/events, graph snapshots/nodes/edges, run records, report records, and audit events.

Raw downloaded payloads are not stored by default. The raw index stores source IDs, source record IDs, payload hashes, short summaries, provenance URLs, retrieval times, and license or terms references.

## Safety Boundaries

- No secrets, private diagnostics, cookies, tokens, or API keys.
- No raw source payloads in API responses.
- Reports and runs are sanitized before storage.
- Every graph/run/report record keeps graph and source-manifest identifiers when available.
- SQLite persistence does not make the platform production ready; current graph and model outputs remain fixture/proxy or promoted public-evidence artifacts.
