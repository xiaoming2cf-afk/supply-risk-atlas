---
name: sra-api-envelope
description: Use when adding or changing SupplyRiskAtlas API endpoints, envelope metadata, error handling, or frontend API client methods.
---

# SRA API Envelope

## When To Use

Use for FastAPI/dev-server routes, endpoint contracts, response envelopes, request validation, shared types, and API client methods.

## Required Files To Read

- `AGENTS.md`
- `services/api/`
- `packages/shared-types/src/index.ts`
- `packages/api-client/src/dashboard.ts`
- `docs/api/`
- `tests/api/`
- `tests/contract/test_api_contracts.py`

## Forbidden Behaviors

- Do not return fabricated fallback data from production-facing APIs.
- Do not expose raw payloads, secrets, private diagnostics, stack traces, or hidden internal fields.
- Do not omit source manifest, graph/model/feature versions, freshness, request ID, warnings, or errors when applicable.
- Do not create export-control evasion guidance.

## Required Checks

- Envelopes must use explicit `success`, `partial`, `stale`, `unavailable`, or `error` status semantics when supported.
- Degraded/unavailable responses must be structured and user-comprehensible.
- API client and shared types must match public endpoint payloads.
- Tests must cover no raw payload exposure and invalid input rejection.

## Expected Summary Format

- Endpoints changed:
- Envelope metadata:
- Client/type changes:
- Tests run:
- Degraded/error behavior:
- Residual risks:
