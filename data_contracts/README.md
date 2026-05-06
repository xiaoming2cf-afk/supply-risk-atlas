# Data Contracts

Contracts are defined in three layers:

1. Ontology YAML under `configs/ontology`.
2. Pydantic models under `packages/sra_core/sra_core/contracts`.
3. Runtime contract tests under `tests/contract`.

Public-source ingestion adds a fourth artifact layer:

- Source registry config under `configs/sources/default.yaml`.
- JSON Schema exports under `data_contracts/ingestion_schema`.
- Connector boundary tests under `tests/ingestion`.

Ingestion connectors are intentionally narrow. They may emit only raw source
records and source freshness manifests. Silver entities/events and gold edge
events are downstream contract shapes; connectors must not emit graph state,
API envelopes, feature payloads, labels, predictions, or model input rows.

Synthetic data is retained only as offline test fixtures. Production source
registration is limited to public, no-key, real-data-first sources with explicit
license, allowed use, update cadence, and freshness SLA metadata.

Schema evolution policy:

- Update ontology/config first.
- Update Pydantic contracts second.
- Update API/shared TypeScript types third.
- Add compatibility or migration notes for any breaking change.
- Existing graph snapshots and reports must retain their original version metadata.
