# Public Source Catalog

The catalog in `configs/sources/semiconductor.yaml` separates enabled fixture
sources, disabled public connector candidates, review-required sources, and
deferred paid/proprietary sources.

## Enabled Fixture Sources

- `eto_cset_advanced_semiconductor_supply_chain`
- `wsts_historical_billings`
- `global_trade_alert_semiconductor_export_controls`
- `gdelt_semiconductor_events`

These remain fixture-only in the current platform state.

## Disabled Public Connector Candidates

- `sec_edgar_lite`
- `gdelt_semiconductor_lite`
- `un_comtrade_semiconductor_trade_lite`
- `world_bank_wits_trade_tariff_lite`
- `usgs_earthquake_lite`
- `nga_world_port_index_lite`
- `ofac_sanctions_list_lite`
- `bis_export_controls_lite`

These are source-registered for future bounded, explicit connector work. Live
fetch remains disabled by default.

## Review-Required Sources

- `federal_register_export_controls_lite`
- `world_bank_macro_indicators_lite`
- `ourairports_lite`
- `openalex_crossref_literature_lite`
- `company_annual_report_manual_upload`
- `customs_trade_manual_upload`

These require connector, terms, or manual-upload review before ingestion.

## Deferred Sources

- `paid_semi_market_data`
- `proprietary_factset_supply_chain`
- `bloomberg_supply_chain`
- `wind_or_choice_private_data`
- `company_private_order_data`

These are registry-only. They must not be fetched, stored, redistributed, or
used to claim production coverage in this project.

## Legal And Safety Notes

The catalog stores source URLs, terms URLs, attribution, allowed-use notes, and
redistribution limits. It does not store raw source payloads. API-visible output
is limited to summaries, lineage, status, and derived facts when a future gate
implements a connector and promotion path.

Sanctions and export-control sources are for compliance risk awareness and
resilience planning only. The platform must not provide evasion, bypass, or
circumvention advice.
