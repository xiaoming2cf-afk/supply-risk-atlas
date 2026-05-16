from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from services.api import main


class Handler(BaseHTTPRequestHandler):
    server_version = "SupplyRiskAtlasDev/0.1"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        request_id = self.headers.get("x-request-id")
        if parsed.path.startswith("/api/v1/dashboard/"):
            page_id = parsed.path.rsplit("/", 1)[-1]
            try:
                self._write(200, main.route_dashboard_page(page_id=page_id, request_id=request_id))
            except LookupError as exc:
                self._write(404, main.make_error("not_found", str(exc), request_id=request_id))
            return
        routes = {
            "/health": lambda: main.route_health(request_id=request_id),
            "/api/v1/health": lambda: main.route_health(request_id=request_id),
            "/api/v1/version": lambda: main.route_version(request_id=request_id),
            "/lineage": lambda: main.route_lineage(
                source_id=_first(query.get("source_id")),
                target_id=_first(query.get("target_id")),
                request_id=request_id,
            ),
            "/api/v1/entities": lambda: main.route_entities(
                entity_type=_first(query.get("entity_type")),
                source_id=_first(query.get("source_id")),
                category=_first(query.get("category")),
                country=_first(query.get("country")),
                industry=_first(query.get("industry")),
                q=_first(query.get("q")),
                limit=_int_or_default(_first(query.get("limit")), 100),
                offset=_int_or_default(_first(query.get("offset")), 0),
                request_id=request_id,
            ),
            "/api/v1/sources": lambda: main.route_sources(
                source_id=_first(query.get("source_id")),
                request_id=request_id,
            ),
            "/api/v1/lineage": lambda: main.route_lineage(
                source_id=_first(query.get("source_id")),
                target_id=_first(query.get("target_id")),
                request_id=request_id,
            ),
            "/api/v1/graph": lambda: main.route_graph_snapshots(request_id=request_id),
            "/api/v1/graph/snapshots": lambda: main.route_graph_snapshots(request_id=request_id),
            "/api/v1/graph/diff": lambda: main.route_graph_diff(request_id=request_id),
            "/api/v1/graph/view": lambda: main.route_graph_view(
                mode=_first(query.get("mode")) or "overview",
                relationship_class=_first(query.get("relationship_class")),
                request_id=request_id,
            ),
            "/api/v1/graph/focus": lambda: main.route_graph_focus(
                node_id=_first(query.get("node_id")) or "company:tsmc",
                depth=_int_or_default(_first(query.get("depth")), 1),
                relationship_class=_first(query.get("relationship_class")),
                request_id=request_id,
            ),
            "/api/v1/graph/clusters": lambda: main.route_graph_clusters(request_id=request_id),
            "/api/v1/graph/path-view": lambda: main.route_graph_path_view(
                source_node_id=_first(query.get("source_node_id")) or "company:tsmc",
                target_node_id=_first(query.get("target_node_id")) or "product_grade:advanced_logic",
                request_id=request_id,
            ),
            "/api/v1/graph/timeline": lambda: main.route_graph_timeline(
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/graph/geo": lambda: main.route_graph_geo(
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/graph/matrix": lambda: main.route_graph_matrix(
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/graph/layers": lambda: main.route_graph_layers(request_id=request_id),
            "/api/v1/graph/evidence": lambda: main.route_graph_evidence(
                source_id=_first(query.get("source_id")),
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/graph/scenario-overlay": lambda: main.route_graph_scenario_overlay(
                run_id=_first(query.get("run_id")),
                request_id=request_id,
            ),
            "/api/v1/graph/node-catalog": lambda: main.route_graph_node_catalog(
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/graph/source-coverage": lambda: main.route_graph_source_coverage(
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/graph/supply-relationships": lambda: main.route_graph_supply_relationships(
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/graph/demand-relationships": lambda: main.route_graph_demand_relationships(
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/graph/production-dependencies": lambda: main.route_graph_production_dependencies(
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/graph/supply-demand-balance": lambda: main.route_graph_supply_demand_balance(
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/graph/snapshot": lambda: main.route_semiconductor_graph_snapshot(
                request_id=request_id,
            ),
            "/api/v1/graph/neighborhood": lambda: main.route_semiconductor_graph_neighborhood(
                node_id=_first(query.get("node_id")) or "company:tsmc",
                depth=_int_or_default(_first(query.get("depth")), 1),
                request_id=request_id,
            ),
            "/api/v1/analytics/charts": lambda: main.route_analytics_charts(
                chart_id=_first(query.get("chart_id")),
                limit=_int_or_default(_first(query.get("limit")), 50),
                request_id=request_id,
            ),
            "/api/v1/analytics/tables": lambda: main.route_analytics_tables(
                table_id=_first(query.get("table_id")),
                limit=_int_or_default(_first(query.get("limit")), 50),
                offset=_int_or_default(_first(query.get("offset")), 0),
                request_id=request_id,
            ),
            "/api/v1/risk/portfolio": lambda: main.route_semirisk_risk_portfolio(
                node_type=_first(query.get("node_type")) or "company",
                limit=_int_or_default(_first(query.get("limit")), 20),
                request_id=request_id,
            ),
            "/api/v1/features": lambda: main.route_features(
                entity_id=_first(query.get("entity_id")),
                request_id=request_id,
            ),
            "/api/v1/labels": lambda: main.route_labels(
                target_id=_first(query.get("target_id")),
                request_id=request_id,
            ),
            "/api/v1/predictions": lambda: main.route_predictions(request_id=request_id),
            "/api/v1/explanations": lambda: main.route_explanations(request_id=request_id),
            "/api/v1/simulations": lambda: main.route_simulations(
                intervention_type=_first(query.get("intervention_type")) or "close_port",
                target_id=_first(query.get("target_id")) or "port_kaohsiung",
                request_id=request_id,
            ),
            "/api/v1/reports": lambda: main.route_reports(request_id=request_id),
        }
        if parsed.path not in routes:
            if parsed.path.startswith("/api/v1/sources/"):
                source_id = parsed.path.rsplit("/", 1)[-1]
                try:
                    self._write(200, main.route_sources(source_id=source_id, request_id=request_id))
                except LookupError as exc:
                    self._write(404, main.make_error("not_found", str(exc), request_id=request_id))
                return
            if parsed.path.startswith("/api/v1/lineage/"):
                source_id = parsed.path.rsplit("/", 1)[-1]
                self._write(
                    200,
                    main.route_lineage(
                        source_id=source_id,
                        target_id=_first(query.get("target_id")),
                        request_id=request_id,
                    ),
                )
                return
            if parsed.path.startswith("/api/v1/risk/entities/"):
                entity_id = unquote(parsed.path.rsplit("/", 1)[-1])
                self._write(
                    200,
                    main.route_semirisk_entity_risk(entity_id=entity_id, request_id=request_id),
                )
                return
            if parsed.path.startswith("/api/v1/stage-graph/"):
                self._write(200, _route_stage_graph(parsed.path, query, request_id))
                return
            if parsed.path.startswith("/api/v1/analytics/tables/"):
                table_id = unquote(parsed.path.rsplit("/", 1)[-1])
                self._write(
                    200,
                    main.route_analytics_table(
                        table_id=table_id,
                        limit=_int_or_default(_first(query.get("limit")), 50),
                        offset=_int_or_default(_first(query.get("offset")), 0),
                        request_id=request_id,
                    ),
                )
                return
            if parsed.path.startswith("/api/v1/analytics/export/"):
                table_id = unquote(parsed.path.rsplit("/", 1)[-1])
                self._write(
                    200,
                    main.route_analytics_export(
                        table_id=table_id,
                        export_format=_first(query.get("format")) or "json",
                        limit=_int_or_default(_first(query.get("limit")), 50),
                        offset=_int_or_default(_first(query.get("offset")), 0),
                        request_id=request_id,
                    ),
                )
                return
            self._write(404, main.make_error("not_found", f"Route not found: {parsed.path}", request_id=request_id))
            return
        try:
            self._write(200, routes[parsed.path]())
        except LookupError as exc:
            self._write(404, main.make_error("not_found", str(exc), request_id=request_id))

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        request_id = self.headers.get("x-request-id")
        body = self._read_json()
        routes = {
            "/api/v1/dashboard/shock-simulator": lambda: main.route_shock_simulator(
                payload=body,
                request_id=request_id,
            ),
            "/api/v1/predictions": lambda: main.route_predictions(request_id=request_id),
            "/api/v1/explanations": lambda: main.route_explanations(request_id=request_id),
            "/api/v1/simulations": lambda: main.route_simulations(
                intervention_type=str(body.get("intervention_type") or "close_port"),
                target_id=str(body.get("target_id") or "port_kaohsiung"),
                request_id=request_id,
            ),
            "/api/v1/scenarios/forward": lambda: main.route_forward_scenario(
                payload=body,
                request_id=request_id,
            ),
            "/api/v1/scenarios/reverse": lambda: main.route_reverse_scenario(
                payload=body,
                request_id=request_id,
            ),
            "/api/v1/optimization/interventions": lambda: main.route_intervention_optimization(
                payload=body,
                request_id=request_id,
            ),
            "/api/v1/reports/investigation": lambda: main.route_investigation_report(
                payload=body,
                request_id=request_id,
            ),
            "/api/v1/reports": lambda: main.route_reports(request_id=request_id),
        }
        if parsed.path not in routes:
            self._write(404, main.make_error("not_found", f"Route not found: {parsed.path}", request_id=request_id))
            return
        try:
            self._write(200, routes[parsed.path]())
        except LookupError as exc:
            self._write(404, main.make_error("not_found", str(exc), request_id=request_id))

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._write_cors_headers()
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return

    def _read_json(self) -> dict[str, object]:
        length = int(self.headers.get("content-length", "0") or "0")
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _write(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self._write_cors_headers()
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_cors_headers(self) -> None:
        self.send_header("access-control-allow-origin", "*")
        self.send_header("access-control-allow-methods", "GET, POST, OPTIONS")
        self.send_header("access-control-allow-headers", "content-type, x-request-id")


def _first(values: list[str] | None) -> str | None:
    return values[0] if values else None


def _int_or_default(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _route_stage_graph(path: str, query: dict[str, list[str]], request_id: str | None) -> dict[str, object]:
    parts = [unquote(part) for part in path.strip("/").split("/")]
    stage_index = parts.index("stage-graph") + 1
    stage_id = parts[stage_index]
    suffix = parts[stage_index + 1] if len(parts) > stage_index + 1 else ""
    limit = _int_or_default(_first(query.get("limit")), 18)
    relationship_class = _first(query.get("relationship_class"))
    if suffix == "focus":
        return main.route_stage_graph_focus(
            stage_id=stage_id,
            node_id=_first(query.get("node_id")),
            limit=limit,
            relationship_class=relationship_class,
            request_id=request_id,
        )
    if suffix == "source-coverage":
        return main.route_stage_graph_source_coverage(stage_id=stage_id, request_id=request_id)
    if suffix == "evidence":
        return main.route_stage_graph_evidence(stage_id=stage_id, limit=limit, request_id=request_id)
    if suffix == "tables":
        return main.route_stage_graph_tables(stage_id=stage_id, limit=limit, request_id=request_id)
    if suffix == "charts":
        return main.route_stage_graph_charts(stage_id=stage_id, limit=limit, request_id=request_id)
    return main.route_stage_graph(
        stage_id=stage_id,
        limit=limit,
        relationship_class=relationship_class,
        request_id=request_id,
    )


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"SupplyRiskAtlas API dev server running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
