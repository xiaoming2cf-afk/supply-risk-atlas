# Real Data Governance

SupplyRiskAtlas is real-data-first: source-derived behavior must be traceable to public, reviewable inputs before it becomes part of production-facing workflows.

## V1 Source Policy

- Use public no-key sources only.
- Do not commit raw source data, proprietary extracts, private credentials, or personal data.
- Keep CI artifacts limited to sanitized reports, schemas, manifests, and aggregate diagnostics.
- Record source license, freshness, schema, and determinism evidence before ingest automation is merged.
- Add production secrets only after a separate Render and GitHub secrets-management gate is approved.

## Required Source Manifest

Every real source must have an input manifest before promotion beyond local exploration. The manifest should be deterministic and sufficient to rebuild a snapshot without fetching floating latest data.

Required fields:

| Field | Purpose |
| --- | --- |
| `source_id` | Stable internal source identifier |
| `publisher` | Public source owner or publisher |
| `source_url` | Public landing page or endpoint |
| `license_url` | License, terms, or public-use policy |
| `allowed_use` | Summary of allowed internal, public, and derivative use |
| `attribution` | Required attribution text or citation |
| `retrieved_at` | Timestamp when the source artifact was retrieved |
| `source_published_at` | Timestamp from the publisher when available |
| `as_of_time` | Time boundary that downstream predictions or snapshots may see |
| `freshness_sla` | Expected refresh interval and stale threshold |
| `content_digest` | Hash of the exact source artifact used |
| `contract_version` | Raw schema or source contract version used for validation |
| `transform_version` | Pipeline, graph, feature, or label transform version |
| `runtime_config_digest` | Digest of config that affects output values |

## Gate Evidence

| Gate | Evidence to keep |
| --- | --- |
| License policy | Manifest license fields, terms review note, attribution requirement |
| Schema validation | Contract validation report with counts and field-level failures, without raw rows |
| Source freshness | Retrieved time, source published time, stale threshold, degraded behavior note |
| Contract compatibility | Compatibility note for changed schemas and consumer update evidence |
| PII/secret hygiene | Sanitized logs, no raw samples, no credentials, no personal-data fields exposed |
| Snapshot determinism | Input manifest, content digests, transform versions, reproducible output digest |

## Logging and Artifacts

CI and deployment logs may include:

- Source IDs and manifest IDs.
- Contract names and versions.
- Aggregate counts and validation error categories.
- Content digests and output digests.
- Stale/fresh status.

CI and deployment logs must not include:

- Raw source rows or record payloads.
- API keys, tokens, cookies, or signed URLs.
- Personal data or proprietary identifiers.
- Full raw file paths that disclose private local data locations.

Related docs: [quality gates](../quality-gates.md), [multi-agent operating model](multi-agent.md), [GitHub CI deployment notes](../deployment/github-ci.md).
