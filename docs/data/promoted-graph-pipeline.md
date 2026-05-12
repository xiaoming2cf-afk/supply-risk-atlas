# Promoted Graph Pipeline

The promoted graph pipeline builds a deterministic, sanitized graph snapshot
from fixture public-evidence connectors and the existing SemiRisk fixture graph.

## Inputs

- Semiconductor fixture graph
- SEC EDGAR Lite fixture connector
- GDELT Semiconductor Lite fixture connector
- UN Comtrade Lite fixture connector
- WITS Lite fixture connector
- USGS Earthquake Lite fixture connector
- NGA World Port Index Lite fixture connector
- OFAC Sanctions List Lite fixture connector
- BIS Export Controls Lite fixture connector

No live connector fetch is performed by the pipeline.

## Outputs

`scripts/build_promoted_graph.py` writes:

- `data/promoted/latest/manifest.json`
- `data/promoted/latest/graph_snapshot.json`
- `data/promoted/latest/source_status.json`
- `data/promoted/latest/quality_report.json`
- `data/promoted/latest/source_coverage.json`
- `data/promoted/latest/entity_resolution_report.json`

Artifacts include `data_mode=public_evidence_promoted` and
`graph_mode=promoted`.

## Safety Controls

- Raw payload bodies are not written.
- Connector fixture records contribute summaries, payload hashes, source refs,
  provenance URLs, and license/terms refs only.
- Evidence-context and policy/compliance records are not treated as real
  supply-chain dependencies.
- The promoted graph is not production ready and is not a production decision or
  financial-loss engine.

Set `SUPPLY_RISK_GRAPH_MODE=promoted` to serve promoted graph views from the API.
The default remains fixture mode.
