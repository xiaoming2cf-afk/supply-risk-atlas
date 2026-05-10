---
name: sra-source-ingest
description: Use when adding or changing SupplyRiskAtlas public-source registration, ingestion connectors, fixtures, freshness, or source manifests.
---

# SRA Source Ingest

## When To Use

Use for source registry entries, connector work, fixture replay, source freshness, and manifest generation.

## Required Files To Read

- `AGENTS.md`
- `configs/sources/default.yaml`
- `configs/sources/semiconductor.yaml`
- `docs/data/data-flow.md`
- `docs/data/semiconductor-source-registry.md`
- `data_contracts/ingestion_schema/`
- `tests/ingestion/`

## Forbidden Behaviors

- Do not commit raw downloaded data, private payloads, secrets, API keys, or hidden diagnostics.
- Do not silently substitute fixtures or generated rows for production data.
- Do not expose raw source payloads through API or frontend.
- Do not give export-control evasion or sanctions-bypass advice.

## Required Checks

- Source entries must include publisher, source URL, terms URL, allowed use, freshness SLA, connector, contracts, owner, and review status.
- Fixture replay must be deterministic and clearly test-only.
- Missing live data must surface unavailable, stale, partial, or degraded state.
- Every emitted record must carry source refs, provenance URL, retrieved/as-of times, confidence, and payload hashes where applicable.

## Expected Summary Format

- Sources changed:
- Connector state:
- Manifest/freshness behavior:
- Tests run:
- Raw-data hygiene:
- Known gaps:
