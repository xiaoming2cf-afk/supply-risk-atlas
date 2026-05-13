# GDELT Semiconductor Lite Connector

`GdeltSemiconductorLiteConnector` is a fixture-first connector for bounded
semiconductor-related public event metadata.

## Current Mode

- Fixture mode is implemented and tested.
- Live mode is disabled by default.
- Live mode returns controlled unavailable and rejects broad queries outside the
  semiconductor event scope.

Allowed query hints for future live work include semiconductor, chip supply
chain, lithography, wafer fab, photoresist, export control, earthquake near
semiconductor regions, power outage, HBM demand spike, and port disruption.

## Extracted Fields

- event time
- event type
- location
- affected entities
- evidence URL
- source name
- confidence
- tone/severity proxy where available
- payload hash
- license/terms ref

The connector does not perform uncontrolled news scraping and does not store or
expose article bodies.

## Promotion

Fixture records promote to `risk_event` summaries with affected entities,
source refs, provenance URL, payload hash, confidence, and evidence summary.
