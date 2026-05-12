# SEC EDGAR Lite Connector

`SecEdgarLiteConnector` is a fixture-first connector for public SEC EDGAR
company disclosure metadata.

## Current Mode

- Fixture mode is implemented and tested.
- Live mode is disabled by default.
- Live mode returns controlled unavailable unless `SEC_USER_AGENT` is set and
  an explicit CIK or ticker request is provided. Bulk downloads are not
  implemented.

## Extracted Fields

- company identifier
- filing date
- filing type
- disclosure type
- risk-factor summary
- supply-chain keywords
- semiconductor keyword match
- source URL
- confidence
- payload hash
- license/terms ref

The connector does not store or expose raw filing bodies.

## Promotion

Fixture records promote to `company_disclosure_event` summaries with source
refs, provenance URL, payload hash, confidence, and evidence summary.

This connector is for research evidence context only. It does not make
production-readiness or investment/financial-loss claims.

