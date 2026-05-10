---
name: sra-frontend-workflow
description: Use when changing SupplyRiskAtlas navigation, hash routes, data gates, frontend API usage, or analytical workflow pages.
---

# SRA Frontend Workflow

## When To Use

Use for `apps/web` navigation, page rendering, data fetching, degraded states, browser smoke, and UI evidence displays.

## Required Files To Read

- `AGENTS.md`
- `apps/web/src/app/App.tsx`
- `apps/web/src/app/pages.tsx`
- `packages/shared-types/src/index.ts`
- `packages/api-client/src/dashboard.ts`
- `scripts/browser-smoke.mjs`
- `tests/e2e/supply-risk-atlas.feature`

## Forbidden Behaviors

- Do not display fake production metrics, fake graph counts, fake risk scores, or fabricated source freshness.
- Do not hide missing data behind optimistic UI states.
- Do not expose raw payloads, secrets, private diagnostics, or internal-only lineage.
- Do not show export-control evasion or sanctions-bypass recommendations.

## Required Checks

- Public routes must be reachable by hash navigation and browser smoke.
- Every analytical page must show source freshness and relevant graph/model/simulation/optimization version metadata where applicable.
- Missing API/source/graph data must render explicit unavailable, stale, partial, or degraded state.
- Browser smoke must protect the intended public behavior.

## Expected Summary Format

- Pages/routes changed:
- Data-fetch changes:
- Degraded-state behavior:
- Smoke/type/build checks:
- Known UI limitations:
