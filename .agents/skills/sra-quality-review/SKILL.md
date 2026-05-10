---
name: sra-quality-review
description: Use for final SupplyRiskAtlas review before commit, PR, push, deploy, or acceptance handoff.
---

# SRA Quality Review

## When To Use

Use after implementation and before final handoff, especially for foundation, data, graph, API, frontend, and deployment changes.

## Required Files To Read

- `AGENTS.md`
- `docs/quality-gates.md`
- Changed files
- Relevant tests under `tests/`
- `scripts/browser-smoke.mjs`
- `render.yaml`
- `README.md`

## Forbidden Behaviors

- Do not claim completion without verified files, routes, tests, and deployment behavior.
- Do not leave fake production data, raw payload exposure, secrets, private diagnostics, or hidden unsafe advice.
- Do not conflate local-only changes with `main` or deployed behavior.
- Do not suggest export-control evasion or sanctions circumvention.

## Required Checks

- Confirm changed files are scoped and unrelated dirty work is not staged.
- Run the relevant Python tests, frontend typecheck/build, and browser smoke when servers are available.
- Scan for raw payload exposure, likely secrets, missing lineage/version metadata, and fabricated fallback data.
- Verify deployed URL when the task requires publishing.

## Expected Summary Format

- Commit SHA:
- Changed files:
- Tests run:
- Failures/skips with reasons:
- Deployment status:
- Verified URL:
- Known limitations:
- Next recommended task:
