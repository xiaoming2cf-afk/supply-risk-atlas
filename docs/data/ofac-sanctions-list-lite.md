# OFAC Sanctions List Lite

`OfacSanctionsListLiteConnector` is a fixture-first connector for public
sanctions-list metadata.

Fixture promotion emits `sanctions_screening_event` summaries with entity name,
list type, program, country, match confidence, provenance URL, payload hash,
source refs, and license/terms ref.

The output is compliance-risk awareness only. It does not provide operational
trade routing, transaction structuring, or restricted-party handling guidance.

Live fetching is disabled by default and not implemented for CI or startup.

