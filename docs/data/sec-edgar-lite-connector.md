# SEC EDGAR Lite Connector

The SEC EDGAR lite connector is a fixture-first proof of the public evidence ingestion boundary. It extracts only bounded filing metadata and summarized risk-factor signals for explicitly requested company identifiers.

Live mode is disabled by default. A future live mode must be explicitly triggered, use a SEC-compliant `SUPPLY_RISK_SEC_EDGAR_USER_AGENT`, apply timeouts and rate limits, and avoid bulk filing downloads. The connector must not fetch during import or API startup.

Stored outputs are limited to source URLs, provenance URLs, retrieval timestamps, payload hashes, terms references, risk-factor summaries, supply-chain keywords, confidence scores, silver disclosure events, and `evidence_for` graph edges. Full filing bodies are not stored or returned through API/UI paths.

The platform remains fixture/proxy/promoted-public-evidence based and is not production ready.
