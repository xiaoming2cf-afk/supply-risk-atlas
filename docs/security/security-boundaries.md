# Security Boundaries

SupplyRiskAtlas is currently a fixture/proxy analytical platform. Security controls are designed to prevent fixture outputs, user text, diagnostics, or run summaries from being mistaken for production data or from leaking raw/private inputs.

## API Boundary

- Request size is bounded by `SUPPLY_RISK_MAX_REQUEST_BYTES` with a default of 256 KB.
- Forward scenario, reverse stress, optimizer, and report inputs are validated before model execution.
- Text inputs are HTML-escaped, length-bounded, screened for unsafe compliance-language, and redacted when they look secret-like.
- Raw payload, source payload, secret, token, API key, password, cookie, authorization, and private diagnostic keys are dropped from sanitized payloads and run summaries.
- Controlled error envelopes return code, message, field, request id, metadata, warnings, and no traceback or private path.

## Browser And CORS Boundary

- Security headers are attached by API middleware when FastAPI is available.
- CORS origins are read from `SUPPLY_RISK_CORS_ORIGINS`.
- Production mode defaults to the configured Render web origin and does not use wildcard CORS.
- Development mode may use local origins only for local testing.

## Analytical Output Boundary

Every analytical output must preserve:

- `graph_version`
- `source_manifest_id`
- relevant formula, model, simulation, optimization, report, or run-store version
- warnings and fixture limitations
- evidence refs or sanitized counts
- explicit fixture/proxy limitation language

The API and UI must not export raw source payloads, private diagnostics, secrets, internal paths, PII, or production-readiness claims.

## Run History Boundary

Run history stores sanitized summaries only. It is bounded, in-memory, process-local, and not a durable audit database. It never stores raw inputs or private diagnostics.
