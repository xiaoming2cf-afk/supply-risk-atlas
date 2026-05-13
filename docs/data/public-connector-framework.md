# Public Connector Framework

The connector framework under `sra_core.ingestion.connectors` defines a safe
interface for future public-source ingestion.

## Modes

- `fixture`: replay a checked-in fixture and emit sanitized metadata records.
- `dry_run`: validate parameters and return a no-network plan.
- `live_disabled`: return a controlled unavailable result.
- `live`: reserved for explicit CLI/admin-triggered fetches in later gates.

Live mode is not enabled by default, and no connector fetches during import,
tests, app startup, or Render startup.

## Required Metadata

Connector records contain:

- `source_id`
- `source_record_id`
- `retrieved_at`
- `as_of_time`
- `payload_hash`
- `provenance_url`
- `license_or_terms_ref`
- `payload_summary`
- `payload_stored=false`

Full source payload bodies are not stored by default and are not API-visible.

## Safety Controls

- `ConnectorConfig` bounds `max_records` and `timeout_seconds`.
- `InMemoryRateLimiter` enforces windowed request limits.
- `SafeHttpClient` requires timeout and byte caps.
- `ConnectorCache` stores metadata only unless explicitly configured to keep
  sanitized record metadata.
- External text summaries are stripped of HTML/script markers and common
  prompt-injection phrases.

The framework is source-policy aware through the `sra_core.sources` registry.
Connector source status and license policy are available without network calls.
