# WITS Trade Tariff Lite

`WitsTradeTariffLiteConnector` is a fixture-first connector for public tariff
and trade-indicator context.

## Current Mode

- Fixture mode is implemented and tested.
- Live mode is disabled by default and returns controlled unavailable.
- No raw bulk WITS tables are committed.

## Extracted Fields

- indicator type
- country
- partner or world aggregate
- commodity group
- period
- value and unit
- source URL
- confidence
- payload hash
- license/terms ref

## Promotion

Records promote to `trade_tariff_indicator` summaries that can later support
market-context charts and promoted graph country/product context.

Indicators are proxy context, not calibrated production decision data.
