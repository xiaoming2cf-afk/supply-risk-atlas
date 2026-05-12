# Persistent Research Store

SupplyRiskAtlas uses SQLite as its first durable research store. The store is for governed public-evidence metadata, graph snapshots, sanitized run summaries, validation artifacts, and sanitized reports. It is not a raw data lake and does not make the platform production ready.

## Configuration

- `SUPPLY_RISK_STORAGE_MODE=memory|sqlite`
- `SUPPLY_RISK_SQLITE_PATH=data/runtime/supply_risk_atlas.db`

Tests use temporary SQLite databases. Local development may use SQLite when the configured path is writable. Existing in-memory run history remains the fallback until a later integration gate switches runtime services by configuration.

## Stored Data

The schema stores source manifests, source status, raw-record indexes, silver entities/events, market indicators, trade flows, policy events, logistics nodes, hazard events, graph snapshots/nodes/edges, graph view cache entries, run records, report records, audit events, and validation artifacts.

Raw downloaded payloads are not stored by default. The raw-record index stores source IDs, source record IDs, retrieval/as-of times, payload hashes, short summaries, provenance URLs, and license or terms references. The `raw_payload_stored` flag defaults to false.

## Safety Boundaries

- No secrets, cookies, tokens, Authorization headers, passwords, private diagnostics, or API keys.
- No raw source payloads, raw article bodies, or raw filing bodies in API-visible outputs.
- Reports and runs are sanitized before storage.
- Graph/run/report records preserve graph and source-manifest identifiers when available.
- Local storage paths are an implementation detail and must not be exposed through public API responses.
- Retention is bounded by store-specific limits for run and report records.

Current graph and model outputs remain fixture/proxy or promoted public-evidence artifacts, not production decisions and not financial-loss estimates.
