from services.api import main


def assert_envelope(payload: dict) -> None:
    assert set(payload) == {"request_id", "status", "data", "metadata", "warnings", "errors"}
    assert payload["status"] == "success"
    metadata = payload["metadata"]
    for key in ["graph_version", "feature_version", "label_version", "model_version", "as_of_time"]:
        assert metadata[key]


def test_health_route_uses_api_envelope() -> None:
    payload = main.route_health()
    assert_envelope(payload)
    assert payload["data"]["status"] == "ok"


def test_prediction_route_is_versioned() -> None:
    payload = main.route_predictions()
    assert_envelope(payload)
    assert payload["data"]
    assert payload["data"][0]["graph_version"] == payload["metadata"]["graph_version"]


def test_simulation_route_returns_counterfactual_version() -> None:
    payload = main.route_simulations()
    assert_envelope(payload)
    assert payload["data"]["counterfactual_graph_version"].startswith("cf_")
