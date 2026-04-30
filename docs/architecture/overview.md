# Architecture Overview

SupplyRiskAtlas is organized around contracts rather than model code.

```text
Raw/Synthetic Data
  -> Entity Registry
  -> Edge Event Store
  -> Edge State Materialization
  -> Graph Snapshot
  -> Path Index
  -> Feature Factory
  -> Label Factory
  -> Dataset Builder
  -> Model Registry / Prediction
  -> API Envelope
  -> Frontend / Reports
```

## Core Rules

- Ontology is the semantic source of truth.
- Event sourcing is the temporal source of truth.
- Entity registry is the identity source of truth.
- Graph snapshots are deterministic for fixed input, config, and `as_of_time`.
- Feature and label logic must be point-in-time safe.
- Every visible output must carry graph, feature, label, and model versions.

## Layer Boundaries

| Layer | Paths | Responsibility |
| --- | --- | --- |
| Experience | `apps/web/`, `packages/design-system/`, `packages/api-client/` | Present analyst workflows and consume stable API contracts |
| Service | `services/api/`, `packages/shared-types/` | Serve entities, graph slices, predictions, explanations, reports, and API envelopes |
| Domain core | `packages/sra_core/`, `graph_kernel/` | Build canonical entities, edge events, snapshots, paths, features, labels, and quality results |
| Data and ML | `ml/`, `configs/features/`, `configs/labels/`, `configs/models/` | Produce point-in-time datasets, baselines, simulations, causal primitives, and evaluation outputs |
| Contracts and config | `data_contracts/`, `configs/ontology/`, `configs/environments/` | Define schemas, ontology, environment behavior, and compatibility rules |
| Infrastructure | `infra/`, `docker-compose.yml` | Provide local and deployment runtime topology |

## Boundary Contracts

- Frontend-to-API contracts belong in `packages/api-client/` and `packages/shared-types/`.
- API envelopes must carry request status, metadata versions, warnings, and errors.
- Data pipeline contracts belong in `data_contracts/`.
- Graph schema and ontology contracts belong in `data_contracts/graph_schema/` and `configs/ontology/`.
- Feature, label, and model output contracts belong in `data_contracts/feature_schema/`, `data_contracts/label_schema/`, and `configs/models/`.

## Storage Strategy

- Data lake and graph snapshots: Parquet/DuckDB-ready structures.
- Interactive graph query: Kuzu.
- Metadata and service state: Postgres.
- Cache: Redis.
- Files and model artifacts: MinIO.

The graph database is never the training source.

Related docs: [data flow](../data/data-flow.md), [quality gates](../quality-gates.md), [E2E acceptance](../../tests/e2e/README.md).
