from __future__ import annotations

from collections import Counter
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from services.api.services.common import semiconductor_fixture_warnings, semiconductor_metadata
from services.api.services.semiconductor_snapshot_cache import fixture_snapshot_for_services
from sra_core.api.envelope import make_envelope, make_error_envelope
from sra_core.geo.normalize import sanitize_chart_table_payload


ROOT = Path(__file__).resolve().parents[3]
CONTENT_PATH = ROOT / "configs" / "sources" / "semiconductor_supply_chain_content.yaml"
CONTENT_FEATURE_VERSION = "semiconductor_content_coverage_v0.1"
DEFAULT_LIMIT = 100
MAX_LIMIT = 500


@lru_cache(maxsize=1)
def _content_fixture() -> dict[str, Any]:
    return yaml.safe_load(CONTENT_PATH.read_text(encoding="utf-8"))


def semiconductor_content_summary_payload() -> dict[str, Any]:
    fixture = _content_fixture()
    counts = _coverage_counts(fixture)
    return sanitize_chart_table_payload(
        {
            "content_version": fixture["content_version"],
            "source_manifest_id": fixture["source_manifest_id"],
            "data_mode": fixture["data_mode"],
            "graph_mode": fixture["graph_mode"],
            "source_status": "fixture_or_promoted_public_evidence",
            "calibration_status": "fixture_proxy_not_calibrated",
            "coverage_level": fixture["coverage_level"],
            "last_updated": fixture["generated_at"],
            "fixture_required": fixture["fixture_required"],
            "live_fetch_default": fixture["live_fetch_default"],
            "counts": counts,
            "coverage_counts": counts,
            "source_family_counts": _source_family_counts(fixture),
            "source_summaries": fixture["source_summaries"],
            "coverage_gaps": fixture.get("coverage_gaps", []),
            "representative_country_region_exposures": fixture["country_region_exposures"][:10],
            "representative_value_chain_layers": fixture["value_chain_layers"][:12],
            "representative_entities": fixture["entity_profiles"][:12],
            "representative_chokepoints": fixture["chokepoints"][:8],
            "warnings": fixture.get("warnings", []),
        }
    )


def route_semiconductor_coverage_overview(request_id: str | None = None) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    payload = {
        **_base_payload(fixture, snapshot, content_scope="coverage_overview"),
        "coverage_counts": _coverage_counts(fixture),
        "source_family_counts": _source_family_counts(fixture),
        "source_summaries": fixture["source_summaries"],
        "coverage_gaps": fixture.get("coverage_gaps", []),
        "representative_country_region_exposures": fixture["country_region_exposures"][:10],
        "representative_value_chain_layers": fixture["value_chain_layers"][:12],
        "representative_entities": fixture["entity_profiles"][:12],
        "representative_chokepoints": fixture["chokepoints"][:8],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def route_semiconductor_value_chain_layers(
    stage: str | None = None,
    layer_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    rows = list(fixture["value_chain_layers"])
    if stage:
        rows = [row for row in rows if str(row.get("stage")) == stage]
    if layer_id:
        rows = [row for row in rows if str(row.get("layer_id")) == layer_id]
    payload = {
        **_base_payload(fixture, snapshot, content_scope="value_chain_layers"),
        "filters": {"stage": stage, "layer_id": layer_id},
        "total": len(rows),
        "layers": rows[: _bounded_limit(limit)],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def route_semiconductor_country_exposures(
    geo_id: str | None = None,
    stage: str | None = None,
    limit: int = DEFAULT_LIMIT,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    rows = list(fixture["country_region_exposures"])
    if geo_id:
        rows = [row for row in rows if str(row.get("geo_id")) == geo_id]
    if stage:
        stage_key = stage.strip().lower()
        rows = [
            row
            for row in rows
            if any(stage_key in str(value).lower() for value in _country_stage_values(row))
        ]
    payload = {
        **_base_payload(fixture, snapshot, content_scope="country_region_exposures"),
        "filters": {"geo_id": geo_id, "stage": stage},
        "total": len(rows),
        "country_region_exposures": rows[: _bounded_limit(limit)],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def route_semiconductor_entity_profiles(
    entity_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    rows = list(fixture["entity_profiles"])
    if entity_id:
        rows = [row for row in rows if str(row.get("entity_id")).lower() == entity_id.lower()]
    payload = {
        **_base_payload(fixture, snapshot, content_scope="entity_profiles"),
        "filters": {"entity_id": entity_id},
        "total": len(rows),
        "entity_profiles": rows[: _bounded_limit(limit)],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def route_semiconductor_chokepoints(
    layer_id: str | None = None,
    stage: str | None = None,
    limit: int = DEFAULT_LIMIT,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    layer_stage = {row["layer_id"]: row["stage"] for row in fixture["value_chain_layers"]}
    rows = list(fixture["chokepoints"])
    if layer_id:
        rows = [row for row in rows if str(row.get("layer_id")) == layer_id]
    if stage:
        rows = [row for row in rows if layer_stage.get(str(row.get("layer_id"))) == stage]
    payload = {
        **_base_payload(fixture, snapshot, content_scope="chokepoints"),
        "filters": {"layer_id": layer_id, "stage": stage},
        "total": len(rows),
        "chokepoints": rows[: _bounded_limit(limit)],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def profile_for_entity(entity_id: str) -> dict[str, Any] | None:
    normalized = entity_id.lower()
    for row in _content_fixture()["entity_profiles"]:
        if str(row.get("entity_id", "")).lower() == normalized:
            return sanitize_chart_table_payload(deepcopy(row))
    return None


def _content_envelope(
    payload: dict[str, Any],
    *,
    snapshot: Any,
    request_id: str | None,
) -> dict[str, Any]:
    return make_envelope(
        sanitize_chart_table_payload(payload),
        metadata=semiconductor_metadata(snapshot, feature_version=CONTENT_FEATURE_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def _content_error(exc: Exception, *, request_id: str | None) -> dict[str, Any]:
    return make_error_envelope(
        "semiconductor_content_unavailable",
        "Semiconductor content fixture could not be loaded.",
        metadata=semiconductor_metadata(feature_version=CONTENT_FEATURE_VERSION),
        request_id=request_id,
        warnings=[f"semiconductor_content_fixture_failed:{type(exc).__name__}"],
    )


def _base_payload(fixture: dict[str, Any], snapshot: Any, *, content_scope: str) -> dict[str, Any]:
    return {
        "content_scope": content_scope,
        "content_version": fixture["content_version"],
        "graph_version": snapshot.graph_version,
        "source_manifest_id": snapshot.source_manifest_id,
        "data_mode": getattr(snapshot, "data_mode", fixture["data_mode"]),
        "graph_mode": getattr(snapshot, "graph_mode", fixture["graph_mode"]),
        "source_status": "fixture_or_promoted_public_evidence",
        "calibration_status": "fixture_proxy_not_calibrated",
        "last_updated": fixture["generated_at"],
        "fixture_required": fixture["fixture_required"],
        "live_fetch_default": fixture["live_fetch_default"],
        "warnings": fixture.get("warnings", []),
        "audit": {
            "source_manifest_id": fixture["source_manifest_id"],
            "api_visibility_policy": fixture["api_visibility_policy"],
            "source_payload_policy": fixture["source_payload_policy"],
            "coverage_level": fixture["coverage_level"],
            "production_status": fixture["production_status"],
        },
    }


def _coverage_counts(fixture: dict[str, Any]) -> dict[str, int]:
    return {
        "country_region_count": len(fixture["country_region_exposures"]),
        "value_chain_layer_count": len(fixture["value_chain_layers"]),
        "entity_profile_count": len(fixture["entity_profiles"]),
        "relationship_edge_count": len(fixture["relationship_edges"]),
        "chokepoint_count": len(fixture["chokepoints"]),
        "source_family_count": len(fixture["source_summaries"]),
    }


def _source_family_counts(fixture: dict[str, Any]) -> dict[str, int]:
    families: Counter[str] = Counter()
    for section_name in ("country_region_exposures", "value_chain_layers", "entity_profiles", "relationship_edges", "chokepoints"):
        for row in fixture.get(section_name, []):
            for source_id in row.get("provenance", []):
                families[_source_family_for_source(source_id)] += 1
    return dict(sorted(families.items()))


def _source_family_for_source(source_id: str) -> str:
    if source_id.startswith(("sec_edgar", "company_annual_report")):
        return "enterprise_public_disclosure"
    if source_id.startswith(("eto_", "wsts_", "gdelt_", "openalex_")):
        return "industry_public_fixture"
    return "national_policy_macro_public"


def _country_stage_values(row: dict[str, Any]) -> list[Any]:
    return [
        *(row.get("upstream_strengths") or []),
        *(row.get("midstream_strengths") or []),
        *(row.get("downstream_strengths") or []),
        row.get("semiconductor_role_summary"),
        row.get("chokepoint_exposure"),
    ]


def _bounded_limit(value: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = DEFAULT_LIMIT
    return max(1, min(MAX_LIMIT, parsed))
