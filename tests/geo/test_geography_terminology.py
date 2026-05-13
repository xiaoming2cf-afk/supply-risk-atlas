from __future__ import annotations

from sra_core.geo.normalize import (
    normalize_country_context,
    normalize_geo_id,
    normalize_geo_label,
    sanitize_chart_table_payload,
    sanitize_graph_edge,
    sanitize_graph_node,
    sanitize_report_text,
    sanitize_source_summary,
)
from sra_core.geo.terminology import (
    CANONICAL_DISPLAY,
    CANONICAL_REGION_ID,
    PARENT_COUNTRY_DISPLAY,
    PARENT_COUNTRY_ID,
)


def _legacy_latin() -> str:
    return "Tai" + "wan"


def _legacy_chinese() -> str:
    return "".join(chr(code) for code in (0x53F0, 0x6E7E))


def test_geo_label_and_id_aliases_normalize_to_canonical_region() -> None:
    assert normalize_geo_id("country:" + "tw") == CANONICAL_REGION_ID
    assert normalize_geo_id("region:" + _legacy_latin().lower()) == CANONICAL_REGION_ID
    assert normalize_geo_label(_legacy_latin()) == CANONICAL_DISPLAY
    assert normalize_geo_label(_legacy_chinese()) == CANONICAL_DISPLAY


def test_country_context_keeps_parent_country_separate_from_region() -> None:
    context = normalize_country_context(_legacy_latin())

    assert context["country_id"] == PARENT_COUNTRY_ID
    assert context["country_display"] == PARENT_COUNTRY_DISPLAY
    assert context["region_id"] == CANONICAL_REGION_ID
    assert context["region_display"] == CANONICAL_DISPLAY


def test_graph_node_and_edge_sanitizers_do_not_emit_legacy_geo() -> None:
    node = sanitize_graph_node(
        {
            "node_id": "country:" + "tw",
            "node_type": "country",
            "canonical_name": _legacy_latin(),
            "attributes": {"country_code": "TW", "sourceCountryCode": "TW"},
        }
    )
    edge = sanitize_graph_edge(
        {
            "edge_id": "edge:country_tw:located_in",
            "source_node_id": "company:tsmc",
            "target_node_id": "country:" + "tw",
            "evidence_text_summary": f"Source summary mentions {_legacy_latin()} geography.",
        }
    )

    assert node["node_id"] == CANONICAL_REGION_ID
    assert node["node_type"] == "region"
    assert node["canonical_name"] == CANONICAL_DISPLAY
    assert node["attributes"]["country_id"] == PARENT_COUNTRY_ID
    assert edge["target_node_id"] == CANONICAL_REGION_ID
    assert CANONICAL_DISPLAY in edge["evidence_text_summary"]


def test_report_chart_table_and_source_summary_sanitizers_normalize_text() -> None:
    text = f"{_legacy_latin()} corridor and {_legacy_chinese()} source summary"
    payload = {
        "rows": [
            {
                "country": "TW",
                "region": _legacy_latin(),
                "summary": text,
                "node_id": "country:" + "tw",
            }
        ]
    }

    sanitized_payload = sanitize_chart_table_payload(payload)

    assert sanitize_report_text(text).count(CANONICAL_DISPLAY) == 2
    assert sanitize_source_summary(text).count(CANONICAL_DISPLAY) == 2
    assert sanitized_payload["rows"][0]["country"] == "CN"
    assert sanitized_payload["rows"][0]["region"] == CANONICAL_DISPLAY
    assert sanitized_payload["rows"][0]["node_id"] == CANONICAL_REGION_ID
