from services.api import main


def assert_envelope(payload: dict) -> None:
    assert set(payload) == {
        "request_id",
        "status",
        "data",
        "metadata",
        "warnings",
        "errors",
        "mode",
        "source_status",
        "source",
    }
    assert payload["status"] == "success"
    assert payload["mode"] == "real"
    assert payload["source_status"] in {"fresh", "stale", "partial", "unavailable"}
    assert payload["source"]["name"]
    metadata = payload["metadata"]
    for key in ["graph_version", "feature_version", "label_version", "model_version", "as_of_time"]:
        assert metadata[key]
    assert metadata["data_mode"] == "real"


def test_health_route_uses_api_envelope() -> None:
    payload = main.route_health()
    assert_envelope(payload)
    assert payload["data"]["status"] == "ok"


def test_prediction_route_is_versioned() -> None:
    payload = main.route_predictions()
    assert_envelope(payload)
    assert payload["data"]
    assert payload["data"][0]["graph_version"] == payload["metadata"]["graph_version"]
    assert payload["data"][0]["score_components"]
    assert payload["data"][0]["driver_contributions"]
    assert payload["data"][0]["prediction_form"] == "public_evidence_graph_ensemble"


def test_prediction_center_route_exposes_mechanisms_and_paths() -> None:
    payload = main.route_dashboard_page(page_id="prediction-center")
    assert_envelope(payload)

    center = payload["data"]
    assert center["predictions"]
    assert center["topPredictions"]
    assert center["mechanisms"]
    assert center["saturatedScoreCount"] < len(center["predictions"])
    assert any(prediction["path_details"] for prediction in center["topPredictions"])


def test_sources_route_is_versioned_and_fresh() -> None:
    payload = main.route_sources()
    assert_envelope(payload)
    assert payload["data"]["manifestRef"].startswith("manifest_public_real_")
    assert payload["data"]["sourceCount"] >= 8
    assert payload["data"]["dataNodeCount"] >= 30
    assert payload["data"]["promotedGraph"]["status"] in {"promoted", "partial"}
    assert payload["data"]["sources"][0]["status"] == "fresh"


def test_lineage_route_is_versioned_and_filterable() -> None:
    payload = main.route_lineage(source_id="gdelt")
    assert_envelope(payload)
    assert payload["data"]["manifestRef"].startswith("manifest_public_real_")
    assert payload["data"]["rawRecordCount"] == 1
    assert payload["data"]["silverEventCount"] >= 1
    assert payload["data"]["goldEdgeEventCount"] >= 1
    assert payload["data"]["records"][0]["sourceId"] == "gdelt"

    target_payload = main.route_lineage(target_id="firm_apple")
    assert_envelope(target_payload)
    assert target_payload["data"]["records"]
    assert all("Apple Inc." in record["targetEntities"] for record in target_payload["data"]["records"])


def test_graph_explorer_returns_renderable_subgraph_with_stats() -> None:
    payload = main.route_dashboard_page(page_id="graph-explorer")
    assert_envelope(payload)

    graph = payload["data"]
    assert graph["nodes"]
    assert graph["links"]
    assert len(graph["nodes"]) <= graph["graphStats"]["renderedNodeLimit"]
    assert len(graph["links"]) <= graph["graphStats"]["renderedLinkLimit"]
    assert graph["graphStats"]["totalNodes"] >= len(graph["nodes"])
    assert graph["graphStats"]["totalLinks"] >= len(graph["links"])
    assert any(row["source"] == "USGS Earthquake Hazards Program" for row in graph["graphStats"]["bySource"])

    node_ids = {node["id"] for node in graph["nodes"]}
    assert "firm_apple" in node_ids
    assert any(link["source"] == "firm_apple" or link["target"] == "firm_apple" for link in graph["links"])


def test_path_analysis_route_exposes_critical_nodes_and_transmission_paths() -> None:
    payload = main.route_dashboard_page(page_id="path-analysis")
    assert_envelope(payload)

    path_analysis = payload["data"]
    assert path_analysis["criticalNodes"]
    assert path_analysis["transmissionPaths"]

    critical_node = path_analysis["criticalNodes"][0]
    assert {"id", "label", "kind", "level", "score", "drivers"} <= set(critical_node)
    assert critical_node["level"] in {"critical", "severe", "elevated", "guarded", "low"}
    assert isinstance(critical_node["drivers"], list)

    transmission_path = path_analysis["transmissionPaths"][0]
    assert {"id", "sourceId", "targetId", "nodeSequence", "edgeSequence", "pathRisk", "pathConfidence"} <= set(
        transmission_path
    )
    assert len(transmission_path["nodeSequence"]) >= 2
    assert len(transmission_path["edgeSequence"]) == len(transmission_path["nodeSequence"]) - 1
    assert 0 <= transmission_path["pathRisk"] <= 1
    assert 0 <= transmission_path["pathConfidence"] <= 1


def test_country_lens_route_exposes_country_options_and_selected_lens() -> None:
    payload = main.route_dashboard_page(page_id="country-lens")
    assert_envelope(payload)

    country_data = payload["data"]
    assert country_data["availableCountries"]
    assert country_data["countryLens"]

    countries = country_data["availableCountries"]
    assert all({"code", "label", "entityCount", "riskScore"} <= set(country) for country in countries)
    assert any(country["code"] == "CN" for country in countries)
    assert all(country["code"] != "TW" for country in countries)

    lens = country_data["countryLens"]
    assert {"countryCode", "countryName", "riskScore", "criticalNodes", "transmissionPaths"} <= set(lens)
    assert lens["countryCode"] in {country["code"] for country in countries}
    assert lens["criticalNodes"]
    assert lens["transmissionPaths"]


def test_entity_route_supports_query_filter() -> None:
    payload = main.route_entities(q="semiconductor", limit=10)
    assert_envelope(payload)
    assert payload["data"]
    assert all(
        "semiconductor" in " ".join(
            [
                entity["canonical_id"],
                entity["display_name"],
                entity.get("industry") or "",
                " ".join(entity.get("external_ids", {}).values()),
            ]
        ).lower()
        for entity in payload["data"]
    )

    source_payload = main.route_entities(q="SEC EDGAR", limit=50)
    assert_envelope(source_payload)
    source_ids = {entity["canonical_id"] for entity in source_payload["data"]}
    assert {"firm_apple", "firm_tesla", "firm_nvidia"} <= source_ids

    cik_payload = main.route_entities(q="0000320193", limit=10)
    assert_envelope(cik_payload)
    assert [entity["canonical_id"] for entity in cik_payload["data"]] == ["firm_apple"]

    data_payload = main.route_entities(entity_type="data_source", q="World Bank", limit=10)
    assert_envelope(data_payload)
    assert [entity["canonical_id"] for entity in data_payload["data"]] == ["data_source_world_bank"]

    indicator_payload = main.route_entities(q="TX.VAL.TECH.MF.ZS", limit=10)
    assert_envelope(indicator_payload)
    assert [entity["canonical_id"] for entity in indicator_payload["data"]] == [
        "indicator_high_tech_exports"
    ]

    source_filtered_payload = main.route_entities(entity_type="indicator", source_id="world_bank", limit=10)
    assert_envelope(source_filtered_payload)
    assert source_filtered_payload["data"]
    assert all(entity["entity_type"] == "indicator" for entity in source_filtered_payload["data"])


def test_simulation_route_returns_counterfactual_version() -> None:
    payload = main.route_simulations()
    assert_envelope(payload)
    assert payload["data"]["counterfactual_graph_version"].startswith("cf_")
