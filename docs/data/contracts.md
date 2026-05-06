# Data Contracts

## Time Contract

Every time-aware record distinguishes:

- `event_time`: when the event happened.
- `ingest_time`: when the system learned it.
- `valid_from`: when a relationship starts.
- `valid_to`: when a relationship ends.
- `as_of_time`: what a prediction or snapshot is allowed to see.
- `prediction_time`: the forecast origin.

Feature computation and dataset building must enforce:

```text
feature_time <= prediction_time
ingest_time <= prediction_time
```

## Version Contract

Predictions, simulations, explanations, and reports must include:

- `graph_version`
- `feature_version`
- `label_version`
- `model_version`
- `as_of_time`
- audit or lineage reference

## Schema Evolution

Breaking schema changes require:

- ontology/config update
- Pydantic contract update
- test update
- migration or compatibility note
- owner review

## Public Source Ingestion Contract

Production ingestion starts from `configs/sources/default.yaml`. Every source
entry must be public, no-key, license-tagged, and freshness-scoped before a
connector can emit records for it.

Current default sources:

- SEC EDGAR
- GLEIF LEI
- GDELT
- World Bank Open Data
- OFAC sanctions lists
- OurAirports
- NGA World Port Index

Large real node catalogs are maintained in
`configs/sources/public_real_node_catalog.yaml`. Each node must carry a
`source_id`, public external identifiers where available, confidence, and a
domain `entity_type`. Catalog edges must reference existing catalog nodes and a
registered public source. The pipeline folds this catalog into source raw
payload checksums, silver entity records, gold edge events, graph snapshots,
features, predictions, and lineage diagnostics.

Catalog node classes now include operational entities and categorized data
nodes:

- operational nodes: firms, countries, ports, airports, products, policies,
  risk events, and text artifacts.
- data governance nodes: `data_source`, `data_category`, `dataset`,
  `indicator`, `industry`, `schema_field`, `license_policy`,
  `coverage_area`, `source_release`, and `observation_series`.
- data relationships: `source_provides`, `dataset_observes`,
  `dataset_measures`, `dataset_covers`, `categorized_as`, `classified_as`, and
  `indicator_context_for`, `dataset_has_field`, `licensed_under`,
  `released_as`, and `observed_for`.

Data nodes are first-class graph nodes. They must pass ontology, silver entity,
snapshot, lineage, API, and frontend type checks before being promoted.

## Bulk Public-Real Promotion Contract

Bulk ingestion is an explicit build step, not an API request side effect.
`python -m sra_core.ingestion.bulk_public` downloads or reuses cached public
no-key source files, emits a deterministic catalog, and writes:

- `data/cache/public_real/*`: local raw public files and fixture fallbacks.
- `data/promoted/public_real/latest/catalog.json`: promoted graph input.
- `data/promoted/public_real/latest/manifest.json`: cache paths, checksums,
  source status, node/edge counts, and `raw_data_in_git=false`.

The API must read the promoted catalog when available. If it is missing, API
metadata and warnings must make the built-in partial catalog state visible; it
must not silently switch to synthetic or mock business payloads.

Connector output is limited to:

- `RawRecord`: canonical raw source payload plus deterministic SHA-256 checksum,
  license name, allowed use, source record id, event time, and ingest time.
- `SourceManifest`: source freshness status, record ids/checksums, SLA, and
  deterministic manifest checksum.

Downstream transforms may produce:

- `SilverEntity`
- `SilverEvent`
- `GoldEdgeEvent`

## Evidence Lineage Contract

The real-data API exposes `/api/v1/lineage` as the audit join from raw source
records to promoted graph evidence. Each lineage row must include:

- `sourceId`, `sourceName`, `rawId`, `sourceRecordId`, and `rawChecksum`.
- `rawObservedTime` so point-in-time auditors can compare it with `as_of_time`.
- linked `silverEventIds`, `silverEntityIds`, and `goldEdgeEventIds`.
- derived `edgeTypes`, `targetEntities`, and aggregate `confidence`.

Lineage output is diagnostic metadata. It may show source names, entity names,
record identifiers, checksums, counts, and manifest references, but it must not
dump raw source payloads into API responses, browser smoke artifacts, GitHub CI
logs, or public deployment logs.

Connectors must not emit `EdgeState`, API envelopes, prediction payloads, label
values, feature values, or model input rows. Synthetic payloads are allowed only
inside offline tests and fixtures.
