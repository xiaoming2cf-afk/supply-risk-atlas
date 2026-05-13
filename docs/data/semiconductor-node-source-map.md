# Semiconductor Node Source Map

`configs/sources/semiconductor_node_source_map.yaml` maps chain layers and node types to public-evidence source candidates.

## Source Policy

All mapped sources use `live_fetch_default: disabled` and `fixture_required: true`. A source entry identifies candidate evidence coverage only; it does not authorize uncontrolled live ingestion. If a source has unclear terms, it remains review-required and non-fetchable until manually approved.

## Coverage Rules

- Each `L0` to `L11` chain layer has at least two candidate sources.
- Each canonical node type has at least one candidate source.
- Each source has at least one graph output so downstream graph and audit views can remain source-bound.
- Each supply, demand, production dependency, and evidence relationship class has at least one candidate source.
- Sources with geography-bearing node types require normalization to `region:china_taiwan` / 中国台湾 where applicable.
- No source is treated as production coverage by default.

## Source Notes

- ETO/CSET and OECD sources are used for value-chain structure and methodology context.
- WSTS is used as a fixture/proxy market-pressure source, not a live market-data feed.
- SEC EDGAR and annual-report sources can support disclosure events and company risk factors, but raw filing bodies are not API-visible.
- GDELT supports event context in fixture mode; article bodies are not stored.
- UN Comtrade and WITS support trade-flow and tariff/concentration proxies. HS-code mappings are imperfect and must be labeled as proxies.
- USGS mineral and earthquake sources support critical-mineral and hazard context.
- NGA World Port Index supports logistics-facility context only and is not navigational decision support.
- OFAC, BIS, Federal Register, and screening-list sources support compliance-risk summaries only. The platform must never provide bypass or evasion guidance.

## Limitations

This map is a public-evidence research scaffold. It is not production-ready, not a complete supplier database, and not a financial-loss engine.
