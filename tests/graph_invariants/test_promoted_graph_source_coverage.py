from __future__ import annotations

from graph_kernel.promoted_pipeline import build_promoted_artifacts


REQUIRED_PUBLIC_SOURCES = {
    "sec_edgar_lite",
    "gdelt_semiconductor_lite",
    "un_comtrade_semiconductor_trade_lite",
    "world_bank_wits_trade_tariff_lite",
    "usgs_mineral_commodity_summaries_lite",
    "usgs_earthquake_lite",
    "nga_world_port_index_lite",
    "ofac_sanctions_list_lite",
    "consolidated_screening_list_lite",
    "bis_export_controls_lite",
    "federal_register_export_controls_lite",
}


def test_promoted_graph_reports_source_coverage_by_source_id() -> None:
    artifacts = build_promoted_artifacts()
    coverage = artifacts["source_coverage"]["counts_by_source_id"]

    assert REQUIRED_PUBLIC_SOURCES <= set(coverage)
    assert all(coverage[source_id] > 0 for source_id in REQUIRED_PUBLIC_SOURCES)
