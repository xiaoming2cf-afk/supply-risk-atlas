# Semiconductor Source Registry

`configs/sources/semiconductor.yaml` is the public-source registry for the semiconductor foundation slice. It is intentionally separate from the general source registry so the app can show semiconductor readiness without implying live semiconductor ingestion is production-ready.

## Registered Sources

| Source ID | Lane | Default | Freshness SLA | Connector state | Purpose |
| --- | --- | --- | ---: | --- | --- |
| `eto_cset_advanced_semiconductor_supply_chain` | v0.1 | enabled | 720h | live unavailable | Public supply-chain relationships, inputs, stages, and production sequence evidence. |
| `wsts_historical_billings` | v0.1 | enabled | 720h | live unavailable | Public semiconductor billings indicators. |
| `global_trade_alert_semiconductor_export_controls` | v0.1 | enabled | 168h | live unavailable | Public trade-policy and export-control measures. |
| `gdelt_semiconductor_events` | v0.1 | enabled | 6h | live unavailable | Public event-monitoring signals. |
| `sec_edgar` | v0.2 | disabled | 72h | disabled pending review | Future issuer filings and risk-factor extraction. |
| `un_comtrade` | v0.2 | disabled | 2160h | disabled pending review | Future import/export trade-flow indicators. |

## Required Fields

Every source entry must include publisher, source URL, terms URL, license or terms summary, allowed use, redistribution limits, attribution, API-key flag, default enablement, update frequency, freshness SLA, connector state, raw/silver/graph contracts, owner, and review status.

## Freshness And Degraded States

The foundation registry is governance evidence only. The v0.1 live connectors are marked `unavailable:live_connector_not_implemented`, and the v0.2 sources are disabled by default. Production API and frontend surfaces must show unavailable, stale, partial, or degraded state when a source, connector, manifest, or graph snapshot is missing.

## Raw Data Policy

Raw downloaded data, private payloads, secrets, API keys, and hidden diagnostics are not committed to Git. Public API and UI surfaces may expose only source metadata, freshness, hashes, lineage refs, summaries, manifests, and derived graph facts. Raw payloads must not be exposed through the API or frontend.

## Export-Control Safety

Policy sources may describe restrictions and cite public evidence. Platform outputs must not recommend export-control evasion, sanctions circumvention, or illegal bypass behavior.
