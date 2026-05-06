# GitHub CI Data Hygiene

GitHub Actions is a public-code validation environment for v1. It must prove quality without storing or printing raw source data.

## CI Rules

- Use public no-key sources only in v1 CI.
- Do not inject production secrets into CI for source access.
- Do not upload raw datasets, raw source rows, database dumps, or source extracts as artifacts.
- Do not print raw records in workflow logs, test failure output, or server startup diagnostics.
- Upload only sanitized reports, manifests, screenshots where allowed, and aggregate validation summaries.
- Treat browser-smoke artifacts as public diagnostics; they must not contain raw data or credentials.

## Allowed Artifacts

| Artifact type | Examples |
| --- | --- |
| Browser smoke reports | `artifacts/browser-smoke/report.real.json`, `artifacts/browser-smoke/report.mock.json` |
| Validation summaries | Contract names, versions, row counts, error categories |
| Manifests | Source IDs, timestamps, digests, license metadata, contract versions |
| Build diagnostics | Typecheck, compile, test, and smoke status |

## Disallowed Artifacts

| Artifact type | Examples |
| --- | --- |
| Raw source data | `data/raw/**`, CSV extracts, JSONL payloads, downloaded archives |
| Runtime data stores | DuckDB/SQLite snapshots containing source rows, local object-store contents |
| Secret material | `.env`, tokens, cookies, service credentials, signed URLs |
| PII | Personal names, emails, phone numbers, individual-level records |

## Workflow Expectations

- Artifact upload paths must be explicit file patterns, not broad directories such as `artifacts/`.
- Failure logs should summarize counts and error classes instead of dumping source payloads.
- Changed-file routing in `quality-gates.yml` should show the required gates and responsible agent for pull requests.
- Any future production secret use must add a dedicated secret-management gate before the workflow consumes those secrets.

Related docs: [quality gates](../quality-gates.md), [real data governance](../governance/real-data-governance.md), [Render deployment](render.md).
