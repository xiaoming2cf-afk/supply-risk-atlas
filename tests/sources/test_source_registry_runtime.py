from __future__ import annotations

from sra_core.sources.registry import load_semiconductor_source_registry, source_registry_readiness


def test_source_registry_runtime_loads_semiconductor_config() -> None:
    registry = load_semiconductor_source_registry()

    assert registry["registry_version"] == "semiconductor-source-registry-v0.1"
    assert len(registry["sources"]) == 6
    assert {source["source_id"] for source in registry["sources"]} >= {
        "sec_edgar",
        "gdelt_semiconductor_events",
    }


def test_source_registry_readiness_reports_connector_states_without_fetching() -> None:
    readiness = source_registry_readiness()

    assert readiness["source_count"] == 6
    assert readiness["connector_status_counts"]["fixture_connector"] == 4
    assert readiness["connector_status_counts"]["disabled_review_required"] == 2
    assert readiness["unavailable_count"] == 0
    assert "source_registry:no_live_fetch_in_runtime" in readiness["warnings"]
    assert all("raw_payload" not in source for source in readiness["sources"])

