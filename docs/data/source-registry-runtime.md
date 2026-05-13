# Source Registry Runtime

The semiconductor source registry is loaded from
`configs/sources/semiconductor.yaml` by `sra_core.sources`.

The runtime validates required governance fields, computes source and connector
status, and returns API-visible readiness summaries. It does not fetch network
resources, open live connectors, or store raw payloads.

## Status Model

Source status values:

- `enabled_fixture`: source is enabled through fixture data only.
- `enabled_promoted`: source is enabled through promoted public evidence.
- `enabled_live_available`: live connector is explicitly enabled and available.
- `live_unavailable`: live connector is not available.
- `disabled_review_required`: source is known but disabled pending review.
- `unavailable_terms_review`: source terms require review before use.
- `deferred_paid_or_proprietary`: source is paid, proprietary, or private and
  registry-only.

Connector status values:

- `fixture_connector`
- `promoted_connector`
- `live_connector_available`
- `live_connector_unavailable`
- `disabled_review_required`
- `deferred_not_allowed`

## License Policy

Each source receives a conservative license-policy summary:

- API-visible summaries and lineage may be allowed.
- Raw payload storage is disabled by default.
- Redistribution is disabled when terms require review or the source is
  deferred/proprietary.
- Attribution is required whenever a publisher attribution is available.

Sources with unclear terms are marked `terms_review_required`. Tier 3 sources
are never fetched by default and are exposed only as registry metadata.

## System Health

System Health uses the runtime readiness summary to display:

- source count
- enabled/disabled/deferred counts
- source status counts
- connector status counts
- source tier counts
- warnings for live-fetch and raw-payload controls

This is a fixture/proxy/public-evidence research control surface. It is not a
production data pipeline and does not perform startup ingestion.

