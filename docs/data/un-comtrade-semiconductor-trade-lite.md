# UN Comtrade Semiconductor Trade Lite

`UnComtradeSemiconductorTradeLiteConnector` is a fixture-first connector for
semiconductor-related trade-flow proxy records.

## Current Mode

- Fixture mode is implemented and tested.
- Live mode is disabled by default and returns controlled unavailable.
- No raw bulk trade data is committed.

## HS Proxy Scope

Fixture records use bounded semiconductor-related HS code proxies such as:

- `854231` integrated circuits
- `854232` memory
- `854233` amplifiers
- `854239` other integrated circuits
- `848620` semiconductor manufacturing machines
- `381800` doped chemical elements for electronics
- `370790` photoresist-related proxy category
- `280461` high-purity silicon proxy category

These mappings are imperfect public-data proxies and must not be presented as a
complete supply-chain truth.

## Promotion

Records promote to `trade_flow` summaries with reporter, partner, flow type,
commodity code, period, value, payload hash, source refs, provenance URL, and
license/terms refs.

The connector computes bounded context metrics:

- dependency share within reporter/product/flow group
- country/product HHI
- significant dependency flag at 0.20 share
- high dependency flag at 0.40 share

These metrics are for research context only.

