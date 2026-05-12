# GDELT Semiconductor Lite Connector

The GDELT semiconductor lite connector is a fixture-first proof of narrow public event ingestion for semiconductor supply-risk evidence. Query scope is intentionally bounded to semiconductor, chip supply chain, lithography, wafer fab, photoresist, export control, and earthquake plus semiconductor-region signals.

Live mode is disabled by default and must be explicitly enabled in a future phase. The connector must not fetch during import or API startup, must use bounded HTTP requests with timeouts and rate limits, and must not perform uncontrolled news scraping.

Stored outputs are limited to source URLs, event metadata, location, affected entity identifiers, payload hashes, provenance URLs, terms references, confidence scores, silver risk events, `impacted_by` edges, and `evidence_for` edges. Article text is not stored or returned through API/UI paths.

The platform remains fixture/proxy/promoted-public-evidence based and is not production ready.
