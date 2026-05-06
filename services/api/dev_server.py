from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

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


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"SupplyRiskAtlas API dev server running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
