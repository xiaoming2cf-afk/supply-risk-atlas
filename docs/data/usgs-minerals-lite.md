# USGS Minerals Lite Connector

`usgs_minerals_lite` is a fixture-first connector for public mineral commodity summary metadata. It is used only for upstream mineral supply proxy context.

## Safety Boundary

- Fixture mode is required for tests and CI.
- Live mode is disabled by default and currently returns a controlled unavailable result.
- Raw tables and bulk payloads are not stored or exposed.
- API-visible records contain payload hashes, summaries, provenance URLs, source refs, and license/terms refs only.

## Promoted Records

The connector promotes fixture records to `mineral_supply_indicator` summaries that can support mineral dependency context in the promoted graph. These indicators are proxy evidence, not production supply measurements.
