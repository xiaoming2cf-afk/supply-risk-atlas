from __future__ import annotations

from importlib import import_module
from pathlib import Path

from services.api import main


def test_requested_service_modules_exist_and_import() -> None:
    expected = [
        "system_health_service",
        "graph_service",
        "risk_service",
        "scenario_service",
        "reverse_stress_service",
        "optimization_service",
        "report_service",
        "run_service",
    ]

    for module in expected:
        import_module(f"services.api.services.{module}")


def test_main_facade_reexports_extracted_route_functions() -> None:
    assert main.route_semiconductor_graph_snapshot()["status"] == "success"
    assert main.route_graph_view()["status"] == "success"
    assert main.route_graph_focus(node_id="company:tsmc")["status"] == "success"
    assert main.route_graph_clusters()["status"] == "success"
    assert main.route_graph_path_view()["status"] == "success"
    assert main.route_semirisk_entity_risk("company:tsmc")["status"] == "success"
    assert main.route_forward_scenario(
        {
            "scenario_type": "earthquake",
            "targets": ["company:tsmc"],
            "severity_distribution": {"type": "fixed", "params": {"value": 0.4}},
            "duration_days_distribution": {"type": "fixed", "params": {"value": 7}},
            "iterations": 5,
        }
    )["status"] == "success"


def test_main_py_line_count_is_materially_reduced() -> None:
    lines = Path("services/api/main.py").read_text(encoding="utf-8").splitlines()
    non_empty_lines = [line for line in lines if line.strip()]

    assert len(lines) < 3189
    assert len(non_empty_lines) <= 2789

