---
name: sra-contract-first
description: Use before changing SupplyRiskAtlas public data shapes, JSON schemas, API envelopes, graph snapshots, model outputs, or frontend-visible payloads.
---

# SRA Contract First

## When To Use

Use for any task that changes raw, silver, graph, feature, model, API, shared TypeScript, or frontend-visible contracts.

## Required Files To Read

- `AGENTS.md`
- `README.md`
- `docs/quality-gates.md`
- `data_contracts/`
- `packages/shared-types/src/index.ts`
- `packages/api-client/src/dashboard.ts`

## Forbidden Behaviors

- Do not render fake production data.
- Do not expose raw payloads, secrets, private diagnostics, or hidden internal fields.
- Do not skip lineage, freshness, source manifest, or version metadata.
- Do not recommend export-control evasion, sanctions circumvention, or illegal bypass behavior.

## Required Checks

- Update contract, shared types, API client, frontend usage, tests, and docs together.
- Validate schema-required fields, provenance, temporal validity, and no raw payload exposure.
- Require explicit unavailable, stale, partial, or degraded states when real data is missing.

## Expected Summary Format

- Contract changes:
- Public shape changes:
- Lineage/version metadata:
- Tests run:
- Degraded-state behavior:
- Remaining risks:
