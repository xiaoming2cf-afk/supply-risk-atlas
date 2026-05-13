from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from hashlib import sha256
import json
import os
import re
from pathlib import Path
from typing import Any

import yaml

from graph_kernel.path_index import build_path_index
from graph_kernel.snapshot_builder import build_graph_snapshot, checksum_payload
from ml.datasets.builder import DatasetSample, build_dataset
from ml.models.baseline import BaselineRiskModel
from sra_core.contracts.data import GoldEdgeEvent, RawRecord, SilverEntity, SilverEvent, SourceManifest, SourceReference
from sra_core.contracts.domain import (
    CanonicalEntity,
    EdgeEvent,
    EdgeState,
    ExplanationPath,
    FeatureValue,
    GraphSnapshot,
    PredictionResult,
    SourceRegistry,
    VersionMetadata,
)
from sra_core.ingestion.connectors import connector_for_source
from sra_core.ingestion.bulk_public import load_promoted_catalog, load_promoted_manifest
from sra_core.ingestion.registry import load_source_registry
from sra_core.geo.normalize import sanitize_api_visible_text, sanitize_chart_table_payload, sanitize_identifier
from sra_core.feature_factory import compute_features
from sra_core.label_factory import label_quality_report


PUBLIC_REAL_AS_OF_TIME = datetime(2026, 5, 2, tzinfo=timezone.utc)
PUBLIC_REAL_WINDOW_START = datetime(2026, 4, 1, tzinfo=timezone.utc)
CHINA_TAIWAN_REGION_ID = "region_china_taiwan"
CHINA_TAIWAN_DISPLAY_NAME = "中国台湾"

COUNTRY_NAMES: dict[str, str] = {
    "AD": "Andorra", "AE": "United Arab Emirates", "AF": "Afghanistan", "AG": "Antigua and Barbuda",
    "AL": "Albania", "AM": "Armenia", "AO": "Angola", "AR": "Argentina", "AT": "Austria",
    "AU": "Australia", "AZ": "Azerbaijan", "BA": "Bosnia and Herzegovina", "BB": "Barbados",
    "BD": "Bangladesh", "BE": "Belgium", "BF": "Burkina Faso", "BG": "Bulgaria", "BH": "Bahrain",
    "BI": "Burundi", "BJ": "Benin", "BN": "Brunei Darussalam", "BO": "Bolivia", "BR": "Brazil",
    "BS": "Bahamas", "BT": "Bhutan", "BW": "Botswana", "BY": "Belarus", "BZ": "Belize",
    "CA": "Canada", "CD": "Congo, Dem. Rep.", "CF": "Central African Republic", "CG": "Congo",
    "CH": "Switzerland", "CI": "Cote d'Ivoire", "CL": "Chile", "CM": "Cameroon", "CN": "China",
    "CO": "Colombia", "CR": "Costa Rica", "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany",
    "DJ": "Djibouti", "DK": "Denmark", "DO": "Dominican Republic", "DZ": "Algeria", "EC": "Ecuador",
    "EE": "Estonia", "EG": "Egypt", "ES": "Spain", "ET": "Ethiopia", "FI": "Finland", "FJ": "Fiji",
    "FR": "France", "GA": "Gabon", "GB": "United Kingdom", "GE": "Georgia", "GH": "Ghana",
    "GM": "Gambia", "GN": "Guinea", "GQ": "Equatorial Guinea", "GR": "Greece", "GT": "Guatemala",
    "HK": "Hong Kong SAR, China", "HN": "Honduras", "HR": "Croatia", "HU": "Hungary", "ID": "Indonesia",
    "IE": "Ireland", "IL": "Israel", "IN": "India", "IQ": "Iraq", "IS": "Iceland", "IT": "Italy",
    "JM": "Jamaica", "JO": "Jordan", "JP": "Japan", "KE": "Kenya", "KG": "Kyrgyz Republic",
    "KH": "Cambodia", "KR": "South Korea", "KW": "Kuwait", "KZ": "Kazakhstan", "LA": "Lao PDR",
    "LB": "Lebanon", "LK": "Sri Lanka", "LR": "Liberia", "LS": "Lesotho", "LT": "Lithuania",
    "LU": "Luxembourg", "LV": "Latvia", "MA": "Morocco", "MD": "Moldova", "MG": "Madagascar",
    "MK": "North Macedonia", "ML": "Mali", "MM": "Myanmar", "MN": "Mongolia", "MR": "Mauritania",
    "MT": "Malta", "MU": "Mauritius", "MW": "Malawi", "MX": "Mexico", "MY": "Malaysia",
    "MZ": "Mozambique", "NA": "Namibia", "NE": "Niger", "NG": "Nigeria", "NI": "Nicaragua",
    "NL": "Netherlands", "NO": "Norway", "NP": "Nepal", "NZ": "New Zealand", "OM": "Oman",
    "PA": "Panama", "PE": "Peru", "PG": "Papua New Guinea", "PH": "Philippines", "PK": "Pakistan",
    "PL": "Poland", "PT": "Portugal", "PY": "Paraguay", "QA": "Qatar", "RO": "Romania",
    "RS": "Serbia", "RU": "Russian Federation", "RW": "Rwanda", "SA": "Saudi Arabia", "SD": "Sudan",
    "SE": "Sweden", "SG": "Singapore", "SI": "Slovenia", "SK": "Slovakia", "SL": "Sierra Leone",
    "SN": "Senegal", "SV": "El Salvador", "TH": "Thailand", "TN": "Tunisia", "TR": "Turkiye",
    "TZ": "Tanzania", "UA": "Ukraine", "UG": "Uganda", "US": "United States", "UY": "Uruguay",
    "UZ": "Uzbekistan", "VE": "Venezuela", "VN": "Vietnam", "ZA": "South Africa", "ZM": "Zambia",
    "ZW": "Zimbabwe",
}

VALID_COUNTRY_CODES = set(COUNTRY_NAMES)
PUBLIC_CURATION_SOURCE = "world_bank"


@dataclass(frozen=True)
class SourceFreshness:
    source_id: str
    status: str
    last_successful_ingest: datetime
    max_stale_minutes: int
    record_count: int
    checksum: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "status": self.status,
            "last_successful_ingest": self.last_successful_ingest.isoformat(),
            "max_stale_minutes": self.max_stale_minutes,
            "record_count": self.record_count,
            "checksum": self.checksum,
        }


@dataclass(frozen=True)
class PublicRealDataset:
    sources: list[SourceRegistry]
    freshness: list[SourceFreshness]
    raw_records: list[RawRecord]
    source_manifests: list[SourceManifest]
    silver_entities: list[SilverEntity]
    silver_events: list[SilverEvent]
    gold_edge_events: list[GoldEdgeEvent]
    entities: list[CanonicalEntity]
    edge_events: list[EdgeEvent]
    source_manifest_ref: str
    source_manifest_checksum: str
    catalog_source: str
    promoted_manifest: dict[str, Any] | None = None


@dataclass(frozen=True)
class RealPipelineResult:
    real: PublicRealDataset
    snapshot: GraphSnapshot
    edge_states: list[EdgeState]
    features: list[FeatureValue]
    labels: list[object]
    samples: list[DatasetSample]
    predictions: list[PredictionResult]
    explanations: list[ExplanationPath]
    label_quality: dict[str, float | int]


def _utc(month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(2026, month, day, hour, minute, tzinfo=timezone.utc)


def _event_id(source: str, source_id: str, target_id: str, edge_type: str) -> str:
    digest = sha256(f"{source}|{source_id}|{target_id}|{edge_type}".encode("utf-8")).hexdigest()[:12]
    return f"real_edge_event_{digest}"


def _checksum(value: Any) -> str:
    return checksum_payload({"value": value})


def _real_catalog_id(value: Any) -> str:
    text = sanitize_identifier(str(value))
    legacy_region = "tai" + "wan"
    text = re.sub(r"(?<!china_)" + legacy_region, "china_taiwan", text, flags=re.IGNORECASE)
    if text == "region:china_taiwan":
        return CHINA_TAIWAN_REGION_ID
    return text


def _public_real_node_catalog_path() -> Path:
    return Path(__file__).resolve().parents[3] / "configs" / "sources" / "public_real_node_catalog.yaml"


def _load_public_real_node_catalog(path: str | Path | None = None) -> dict[str, Any]:
    if path is not None:
        payload = _read_catalog_file(Path(path))
    else:
        env_catalog_path = os.environ.get("SUPPLY_RISK_REAL_CATALOG_PATH")
        if env_catalog_path:
            payload = _read_catalog_file(Path(env_catalog_path))
        else:
            payload = load_promoted_catalog()
            if payload is None:
                payload = _read_catalog_file(_public_real_node_catalog_path())
    if not isinstance(payload, dict):
        raise ValueError("public real node catalog must be a mapping")
    return _normalize_public_real_catalog(_merge_missing_builtin_sources(payload))


def _normalize_public_real_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    entities: dict[str, dict[str, Any]] = {}
    for raw_entity in catalog.get("entities", []):
        if not isinstance(raw_entity, dict):
            continue
        entity = dict(raw_entity)
        canonical_id = _real_catalog_id(entity.get("canonical_id") or "")
        entity_type = str(entity.get("entity_type") or "")
        external_ids = {
            str(key): str(value)
            for key, value in sanitize_chart_table_payload(entity.get("external_ids") or {}).items()
            if value is not None
        }
        entity["canonical_id"] = canonical_id
        if entity.get("display_name") is not None:
            entity["display_name"] = sanitize_api_visible_text(entity["display_name"])
        if entity.get("displayName") is not None:
            entity["displayName"] = sanitize_api_visible_text(entity["displayName"])
        source_country = _raw_geo_code(
            external_ids.get("sourceCountryCode")
            or external_ids.get("iso2")
            or entity.get("sourceCountryCode")
            or entity.get("country")
        )
        if canonical_id == CHINA_TAIWAN_REGION_ID or (entity_type == "country" and source_country == "TW"):
            entity_type = "coverage_area"
            entity.update(
                {
                    "canonical_id": CHINA_TAIWAN_REGION_ID,
                    "entity_type": "coverage_area",
                    "display_name": CHINA_TAIWAN_DISPLAY_NAME,
                    "displayName": CHINA_TAIWAN_DISPLAY_NAME,
                    "country": "CN",
                    "geoId": CHINA_TAIWAN_REGION_ID,
                    "geoLevel": "region",
                    "countryCode": "CN",
                    "regionId": "region:china_taiwan",
                    "parentGeoId": "country_cn",
                    "sourceCountryCode": "CN",
                }
            )
            external_ids.update(
                {
                    "geoId": CHINA_TAIWAN_REGION_ID,
                    "geoLevel": "region",
                    "countryCode": "CN",
                    "regionId": "region:china_taiwan",
                    "parentGeoId": "country_cn",
                    "sourceCountryCode": "CN",
                }
            )
        if entity_type == "country":
            country_code = _raw_geo_code(entity.get("country") or external_ids.get("iso2") or canonical_id.replace("country_", ""))
            if country_code not in VALID_COUNTRY_CODES:
                continue
            canonical_id = f"country_{country_code.lower()}"
            entity.update(
                {
                    "canonical_id": canonical_id,
                    "entity_type": "country",
                    "display_name": COUNTRY_NAMES.get(country_code, entity.get("display_name") or country_code),
                    "displayName": COUNTRY_NAMES.get(country_code, entity.get("display_name") or country_code),
                    "country": country_code,
                    "geoId": canonical_id,
                    "geoLevel": "country",
                    "countryCode": country_code,
                    "provinceCode": None,
                    "parentGeoId": None,
                    "sourceCountryCode": country_code,
                }
            )
            external_ids.update({"iso2": country_code, "geoId": canonical_id, "geoLevel": "country", "countryCode": country_code, "sourceCountryCode": country_code})
        elif (
            source_country == "TW"
            or entity.get("country") == "TW"
            or _real_catalog_id(entity.get("geoId") or external_ids.get("geoId") or "") == CHINA_TAIWAN_REGION_ID
        ):
            entity.update(
                {
                    "country": "CN",
                    "geoId": CHINA_TAIWAN_REGION_ID,
                    "geoLevel": "region_context",
                    "countryCode": "CN",
                    "regionId": "region:china_taiwan",
                    "parentGeoId": "country_cn",
                    "sourceCountryCode": "CN",
                }
            )
            external_ids.update(
                {
                    "geoId": CHINA_TAIWAN_REGION_ID,
                    "geoLevel": "region_context",
                    "countryCode": "CN",
                    "regionId": "region:china_taiwan",
                    "parentGeoId": "country_cn",
                    "sourceCountryCode": "CN",
                }
            )
        else:
            country_code = _raw_geo_code(entity.get("country"))
            if country_code == "TW":
                entity["country"] = "CN"
            elif country_code and country_code not in VALID_COUNTRY_CODES:
                entity["country"] = None
        entity["external_ids"] = external_ids
        entities[canonical_id] = entity

    _ensure_curated_entity(
        entities,
        {
            "canonical_id": CHINA_TAIWAN_REGION_ID,
            "entity_type": "coverage_area",
            "display_name": CHINA_TAIWAN_DISPLAY_NAME,
            "displayName": CHINA_TAIWAN_DISPLAY_NAME,
            "country": "CN",
            "geoId": CHINA_TAIWAN_REGION_ID,
            "geoLevel": "region",
            "countryCode": "CN",
            "regionId": "region:china_taiwan",
            "parentGeoId": "country_cn",
            "sourceCountryCode": "CN",
            "industry": None,
            "source_id": PUBLIC_CURATION_SOURCE,
            "confidence": 1.0,
            "external_ids": {
                "geoId": CHINA_TAIWAN_REGION_ID,
                "geoLevel": "region",
                "countryCode": "CN",
                "regionId": "region:china_taiwan",
                "parentGeoId": "country_cn",
                "sourceCountryCode": "CN",
                "iso3166_2": "CN-TW",
            },
        },
    )
    for code, name in COUNTRY_NAMES.items():
        _ensure_curated_entity(
            entities,
            {
                "canonical_id": f"country_{code.lower()}",
                "entity_type": "country",
                "display_name": name,
                "displayName": name,
                "country": code,
                "geoId": f"country_{code.lower()}",
                "geoLevel": "country",
                "countryCode": code,
                "sourceCountryCode": code,
                "industry": None,
                "source_id": PUBLIC_CURATION_SOURCE,
                "confidence": 0.9,
                "external_ids": {"iso2": code, "geoId": f"country_{code.lower()}", "geoLevel": "country", "countryCode": code, "sourceCountryCode": code},
            },
        )

    edges: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for raw_edge in catalog.get("edges", []):
        if not isinstance(raw_edge, dict):
            continue
        edge = dict(raw_edge)
        source_id = _real_catalog_id(edge.get("source_id") or "")
        target_id = _real_catalog_id(edge.get("target_id") or "")
        edge["source_id"] = source_id
        edge["target_id"] = target_id
        if source_id not in entities or target_id not in entities:
            continue
        key = (str(edge.get("source") or PUBLIC_CURATION_SOURCE), source_id, target_id, str(edge.get("edge_type") or ""))
        edges[key] = edge

    _add_curated_supply_chain_overlay(entities, edges)
    return {
        **catalog,
        "catalog_version": f"{catalog.get('catalog_version', 'public-real')}-contract-v2",
        "entities": sorted(entities.values(), key=lambda item: item["canonical_id"]),
        "edges": sorted(edges.values(), key=lambda item: (item["source"], item["edge_type"], item["source_id"], item["target_id"])),
    }


def _raw_geo_code(value: Any) -> str | None:
    text = str(value or "").strip().upper()
    return text if len(text) == 2 and text.isalpha() else None


def _ensure_curated_entity(entities: dict[str, dict[str, Any]], entity: dict[str, Any]) -> None:
    if entity["canonical_id"] in entities:
        existing = entities[entity["canonical_id"]]
        existing_external = dict(existing.get("external_ids") or {})
        existing_external.update(entity.get("external_ids") or {})
        existing["external_ids"] = existing_external
        for key in ("geoId", "geoLevel", "countryCode", "provinceCode", "parentGeoId", "sourceCountryCode", "displayName"):
            if entity.get(key) is not None:
                existing.setdefault(key, entity[key])
        return
    entities[entity["canonical_id"]] = entity


def _add_curated_entity(
    entities: dict[str, dict[str, Any]],
    canonical_id: str,
    entity_type: str,
    display_name: str,
    country: str | None,
    industry: str,
    *,
    source_id: str = PUBLIC_CURATION_SOURCE,
    confidence: float = 0.82,
    external_ids: dict[str, Any] | None = None,
) -> None:
    external = {str(key): str(value) for key, value in (external_ids or {}).items() if value is not None}
    if country == "TW":
        country = "CN"
        external.update({"geoId": CHINA_TAIWAN_REGION_ID, "geoLevel": "province_context", "countryCode": "CN", "regionId": "region:china_taiwan", "parentGeoId": "country_cn", "sourceCountryCode": "CN"})
    elif country:
        external.update({"geoId": f"country_{country.lower()}", "geoLevel": "country_context", "countryCode": country, "sourceCountryCode": country})
    _ensure_curated_entity(
        entities,
        {
            "canonical_id": canonical_id,
            "entity_type": entity_type,
            "display_name": display_name,
            "displayName": display_name,
            "country": country,
            "industry": industry,
            "source_id": source_id,
            "confidence": confidence,
            "external_ids": external,
        },
    )


def _add_curated_edge(
    entities: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
    source_id: str,
    target_id: str,
    edge_type: str,
    *,
    source: str = PUBLIC_CURATION_SOURCE,
    confidence: float = 0.74,
    day: int = 11,
    weight: float | None = None,
    risk_score: float | None = None,
    attributes: dict[str, Any] | None = None,
) -> None:
    if source_id not in entities or target_id not in entities:
        return
    key = (source, source_id, target_id, edge_type)
    if key in edges:
        return
    edge_attributes = {"weight": round(weight if weight is not None else confidence, 4), "risk_score": round(risk_score if risk_score is not None else max(0.01, 1.0 - confidence), 4)}
    edge_attributes.update(attributes or {})
    edges[key] = {
        "source_id": source_id,
        "target_id": target_id,
        "edge_type": edge_type,
        "source": source,
        "day": max(1, min(28, day)),
        "confidence": confidence,
        "attributes": edge_attributes,
    }


def _add_curated_supply_chain_overlay(
    entities: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
) -> None:
    curated_nodes = [
        ("raw_material_high_purity_silicon", "raw_material", "High-purity silicon feedstock", "US", "Semiconductor raw material"),
        ("raw_material_lithium_carbonate", "raw_material", "Lithium carbonate", "CL", "Battery raw material"),
        ("raw_material_cobalt", "raw_material", "Cobalt", "CD", "Battery raw material"),
        ("raw_material_nickel_sulfate", "raw_material", "Nickel sulfate", "ID", "Battery raw material"),
        ("raw_material_graphite", "raw_material", "Battery-grade graphite", "CN", "Battery raw material"),
        ("raw_material_neon", "raw_material", "Semiconductor-grade neon", "UA", "Electronic gas"),
        ("component_silicon_wafer", "component", "300mm silicon wafer", "JP", "Semiconductor component"),
        ("component_photoresist", "component", "Advanced photoresist", "JP", "Semiconductor component"),
        ("component_substrate_abf", "component", "ABF package substrate", "CN", "Semiconductor component"),
        ("component_battery_cell", "component", "Lithium-ion battery cell", "CN", "Battery component"),
        ("component_battery_cathode", "component", "Battery cathode active material", "KR", "Battery component"),
        ("component_power_module", "component", "Automotive power module", "DE", "Automotive electronics"),
        ("product_grade_logic_5nm", "product_grade", "Advanced logic 5nm grade", "CN", "Product grade"),
        ("product_grade_hbm", "product_grade", "High-bandwidth memory grade", "KR", "Product grade"),
        ("product_grade_lfp_cell", "product_grade", "LFP battery cell grade", "CN", "Product grade"),
        ("supplier_tier_1", "supplier_tier", "Tier 1 direct supplier", None, "Supplier tier taxonomy"),
        ("supplier_tier_2", "supplier_tier", "Tier 2 component supplier", None, "Supplier tier taxonomy"),
        ("supplier_tier_3", "supplier_tier", "Tier 3 material supplier", None, "Supplier tier taxonomy"),
        ("factory_tsmc_fab18", "factory", "TSMC Fab 18", "TW", "Semiconductor factory"),
        ("factory_samsung_pyeongtaek", "factory", "Samsung Pyeongtaek semiconductor campus", "KR", "Semiconductor factory"),
        ("factory_intel_arizona", "factory", "Intel Arizona fab campus", "US", "Semiconductor factory"),
        ("factory_foxconn_zhengzhou", "factory", "Foxconn Zhengzhou manufacturing campus", "CN", "Electronics factory"),
        ("factory_catl_ningde", "factory", "CATL Ningde battery manufacturing base", "CN", "Battery factory"),
        ("warehouse_memphis_electronics_dc", "warehouse", "Memphis electronics distribution center", "US", "Warehouse"),
        ("warehouse_rotterdam_components_hub", "warehouse", "Rotterdam components hub", "NL", "Warehouse"),
        ("warehouse_singapore_semiconductor_hub", "warehouse", "Singapore semiconductor logistics hub", "SG", "Warehouse"),
        ("route_lane_china_taiwan_us_west_coast", "route_lane", "中国台湾 to US West Coast electronics lane", None, "Route lane"),
        ("route_lane_east_asia_rotterdam", "route_lane", "East Asia to Rotterdam ocean lane", None, "Route lane"),
        ("route_lane_chile_china_lithium", "route_lane", "Chile to China lithium chemicals lane", None, "Route lane"),
        ("carrier_maersk", "carrier", "A.P. Moller - Maersk", "DK", "Ocean carrier"),
        ("carrier_cma_cgm", "carrier", "CMA CGM", "FR", "Ocean carrier"),
        ("carrier_evergreen", "carrier", "Evergreen Marine", "TW", "Ocean carrier"),
        ("carrier_dhl", "carrier", "DHL Express", "DE", "Air carrier"),
        ("carrier_fedex", "carrier", "FedEx", "US", "Air carrier"),
    ]
    for node in curated_nodes:
        _add_curated_entity(entities, *node, source_id=PUBLIC_CURATION_SOURCE, external_ids={"curationTemplate": "supply_chain_contract_v2"})

    curated_edges = [
        ("raw_material_high_purity_silicon", "component_silicon_wafer", "material_processed_into", 0.82, 0.72, 0.28),
        ("raw_material_neon", "component_photoresist", "input_to", 0.72, 0.45, 0.34),
        ("raw_material_lithium_carbonate", "component_battery_cathode", "material_processed_into", 0.82, 0.7, 0.31),
        ("raw_material_cobalt", "component_battery_cathode", "input_to", 0.78, 0.62, 0.38),
        ("raw_material_nickel_sulfate", "component_battery_cathode", "input_to", 0.78, 0.6, 0.35),
        ("raw_material_graphite", "component_battery_cell", "input_to", 0.78, 0.62, 0.32),
        ("component_silicon_wafer", "product_advanced_semiconductors", "component_of", 0.84, 0.75, 0.3),
        ("component_photoresist", "product_advanced_semiconductors", "component_of", 0.78, 0.58, 0.27),
        ("component_substrate_abf", "product_advanced_semiconductors", "component_of", 0.76, 0.58, 0.29),
        ("component_battery_cathode", "component_battery_cell", "component_of", 0.82, 0.72, 0.3),
        ("component_battery_cell", "product_ev_batteries", "component_of", 0.84, 0.76, 0.31),
        ("product_grade_logic_5nm", "product_advanced_semiconductors", "qualified_alternative_to", 0.68, 0.26, 0.18),
        ("product_grade_hbm", "product_memory_chips", "qualified_alternative_to", 0.66, 0.24, 0.17),
        ("product_grade_lfp_cell", "product_ev_batteries", "qualified_alternative_to", 0.7, 0.32, 0.18),
        ("product_grade_lfp_cell", "product_grade_hbm", "substitutes", 0.52, 0.12, 0.12),
        ("firm_tsmc", "firm_apple", "supplies_to", 0.74, 0.72, 0.39),
        ("firm_tsmc", "firm_nvidia", "supplies_to", 0.74, 0.75, 0.42),
        ("firm_foxconn", "firm_apple", "supplies_to", 0.73, 0.68, 0.34),
        ("firm_catl", "firm_tesla", "supplies_to", 0.72, 0.67, 0.36),
        ("firm_lg_energy_solution", "firm_tesla", "supplies_to", 0.68, 0.52, 0.28),
        ("factory_tsmc_fab18", "firm_tsmc", "used_by", 0.86, 0.8, 0.33),
        ("product_advanced_semiconductors", "factory_tsmc_fab18", "manufactured_at", 0.82, 0.72, 0.35),
        ("product_memory_chips", "factory_samsung_pyeongtaek", "manufactured_at", 0.82, 0.68, 0.29),
        ("product_ev_batteries", "factory_catl_ningde", "manufactured_at", 0.82, 0.7, 0.31),
        ("component_battery_cell", "warehouse_memphis_electronics_dc", "stored_at", 0.72, 0.44, 0.2),
        ("component_silicon_wafer", "warehouse_singapore_semiconductor_hub", "stored_at", 0.74, 0.48, 0.23),
        ("component_photoresist", "warehouse_rotterdam_components_hub", "stored_at", 0.7, 0.42, 0.2),
        ("factory_tsmc_fab18", "warehouse_singapore_semiconductor_hub", "ships_to", 0.72, 0.55, 0.31),
        ("warehouse_singapore_semiconductor_hub", "warehouse_memphis_electronics_dc", "ships_to", 0.68, 0.5, 0.29),
        ("factory_catl_ningde", "warehouse_memphis_electronics_dc", "ships_to", 0.66, 0.48, 0.3),
        ("route_lane_china_taiwan_us_west_coast", "port_kaohsiung", "route_leg", 0.76, 0.62, 0.42),
        ("route_lane_china_taiwan_us_west_coast", "port_los_angeles", "route_leg", 0.74, 0.6, 0.38),
        ("route_lane_east_asia_rotterdam", "port_singapore", "route_leg", 0.74, 0.62, 0.35),
        ("route_lane_east_asia_rotterdam", "port_rotterdam", "route_leg", 0.72, 0.58, 0.34),
        ("route_lane_chile_china_lithium", "port_wpi_port_of_valparaiso", "route_leg", 0.62, 0.4, 0.26),
        ("carrier_maersk", "route_lane_east_asia_rotterdam", "handled_at", 0.72, 0.58, 0.29),
        ("carrier_evergreen", "route_lane_china_taiwan_us_west_coast", "handled_at", 0.74, 0.62, 0.34),
        ("carrier_dhl", "warehouse_singapore_semiconductor_hub", "handled_at", 0.7, 0.48, 0.24),
        ("carrier_fedex", "warehouse_memphis_electronics_dc", "handled_at", 0.7, 0.5, 0.24),
        ("firm_tsmc", "supplier_tier_1", "classified_as", 0.8, 0.5, 0.2),
        ("component_silicon_wafer", "supplier_tier_2", "classified_as", 0.72, 0.4, 0.18),
        ("raw_material_high_purity_silicon", "supplier_tier_3", "classified_as", 0.7, 0.36, 0.16),
    ]
    for index, (source_id, target_id, edge_type, confidence, weight, risk_score) in enumerate(curated_edges, start=1):
        _add_curated_edge(
            entities,
            edges,
            source_id,
            target_id,
            edge_type,
            source=PUBLIC_CURATION_SOURCE,
            confidence=confidence,
            weight=weight,
            risk_score=risk_score,
            day=10 + index % 12,
            attributes={"curationTemplate": "supply_chain_contract_v2"},
        )


def _read_catalog_file(catalog_path: Path) -> dict[str, Any]:
    with catalog_path.open("r", encoding="utf-8") as handle:
        if catalog_path.suffix.lower() == ".json":
            return json.load(handle)
        return yaml.safe_load(handle)


def _merge_missing_builtin_sources(catalog: dict[str, Any]) -> dict[str, Any]:
    configured_sources = {entry.source_id for entry in load_source_registry().sources}
    catalog_sources = {
        entity.get("source_id")
        for entity in catalog.get("entities", [])
        if isinstance(entity, dict)
    } | {
        edge.get("source")
        for edge in catalog.get("edges", [])
        if isinstance(edge, dict)
    }
    missing_sources = configured_sources - {source for source in catalog_sources if source}
    if not missing_sources:
        return catalog

    builtin = _read_catalog_file(_public_real_node_catalog_path())
    merged_entities = list(catalog.get("entities", []))
    merged_edges = list(catalog.get("edges", []))
    entity_ids = {
        entity["canonical_id"]
        for entity in merged_entities
        if isinstance(entity, dict) and "canonical_id" in entity
    }
    for entity in builtin.get("entities", []):
        if not isinstance(entity, dict) or entity.get("source_id") not in missing_sources:
            continue
        if entity["canonical_id"] in entity_ids:
            continue
        merged_entities.append(entity)
        entity_ids.add(entity["canonical_id"])
    edge_keys = {
        (edge.get("source"), edge.get("source_id"), edge.get("target_id"), edge.get("edge_type"))
        for edge in merged_edges
        if isinstance(edge, dict)
    }
    for edge in builtin.get("edges", []):
        if not isinstance(edge, dict) or edge.get("source") not in missing_sources:
            continue
        if edge.get("source_id") not in entity_ids or edge.get("target_id") not in entity_ids:
            continue
        key = (edge.get("source"), edge.get("source_id"), edge.get("target_id"), edge.get("edge_type"))
        if key in edge_keys:
            continue
        merged_edges.append(edge)
        edge_keys.add(key)
    return {
        **catalog,
        "catalog_version": f"{catalog.get('catalog_version', 'public-real')}-merged-{checksum_payload({'sources': sorted(missing_sources)})[:8]}",
        "entities": merged_entities,
        "edges": merged_edges,
    }


def _catalog_source() -> tuple[str, dict[str, Any] | None]:
    env_catalog_path = os.environ.get("SUPPLY_RISK_REAL_CATALOG_PATH")
    if env_catalog_path:
        return "override", None
    promoted_manifest = load_promoted_manifest()
    if promoted_manifest is not None and load_promoted_catalog() is not None:
        return "promoted", promoted_manifest
    return "builtin_partial", None


def _catalog_records_by_source(catalog: dict[str, Any]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    records: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for entity in catalog.get("entities", []):
        source_id = entity["source_id"]
        records.setdefault(source_id, {"entities": [], "edges": []})["entities"].append(
            {
                "canonical_id": entity["canonical_id"],
                "entity_type": entity["entity_type"],
                "display_name": entity["display_name"],
                "external_ids": entity.get("external_ids", {}),
            }
        )
    for edge in catalog.get("edges", []):
        source_id = edge["source"]
        records.setdefault(source_id, {"entities": [], "edges": []})["edges"].append(
            {
                "source_id": edge["source_id"],
                "target_id": edge["target_id"],
                "edge_type": edge["edge_type"],
            }
        )
    return records


def _catalog_entities(
    catalog: dict[str, Any],
    as_of_time: datetime,
) -> tuple[list[CanonicalEntity], dict[str, str]]:
    entities: list[CanonicalEntity] = []
    source_by_entity: dict[str, str] = {}
    seen: set[str] = set()
    for item in catalog.get("entities", []):
        canonical_id = item["canonical_id"]
        if canonical_id in seen:
            raise ValueError(f"duplicate catalog entity {canonical_id}")
        seen.add(canonical_id)
        source_by_entity[canonical_id] = item["source_id"]
        entities.append(
            CanonicalEntity(
                canonical_id=canonical_id,
                entity_type=item["entity_type"],
                display_name=item["display_name"],
                country=item.get("country"),
                industry=item.get("industry"),
                external_ids={
                    key: str(value)
                    for key, value in (item.get("external_ids") or {}).items()
                    if value is not None
                },
                confidence=float(item["confidence"]),
                created_at=as_of_time - timedelta(days=30),
                updated_at=as_of_time - timedelta(hours=2),
            )
        )
    return entities, source_by_entity


def _catalog_edge_events(
    catalog: dict[str, Any],
    source_manifest_ref: str,
) -> list[EdgeEvent]:
    edge_events: list[EdgeEvent] = []
    entity_ids = {item["canonical_id"] for item in catalog.get("entities", [])}
    for item in catalog.get("edges", []):
        source_id = item["source_id"]
        target_id = item["target_id"]
        if source_id not in entity_ids or target_id not in entity_ids:
            raise ValueError(f"catalog edge references unknown endpoint: {source_id}->{target_id}")
        event_time = _utc(4, int(item.get("day", 2)))
        attributes = dict(item.get("attributes") or {})
        edge_events.append(
            EdgeEvent(
                edge_event_id=_event_id(item["source"], source_id, target_id, item["edge_type"]),
                source_id=source_id,
                target_id=target_id,
                edge_type=item["edge_type"],
                event_type=item.get("event_type", "create"),
                event_time=event_time,
                published_time=event_time + timedelta(hours=2),
                observed_time=event_time + timedelta(hours=6),
                ingest_time=event_time + timedelta(hours=6),
                attributes={
                    "valid_from": event_time,
                    "source_manifest_ref": source_manifest_ref,
                    **attributes,
                },
                confidence=float(item["confidence"]),
                source=item["source"],
            )
        )
    return edge_events


def _ingest_public_real_raw_records(as_of_time: datetime) -> dict[str, Any]:
    catalog = _load_public_real_node_catalog()
    catalog_records_by_source = _catalog_records_by_source(catalog)
    source_payloads: dict[str, dict[str, Any]] = {
        "sec_edgar": {
            "source_record_id": "sec:submissions:0000320193",
            "event_time": _utc(4, 30, 12),
            "payload_format": "json",
            "raw_payload": {
                "cik": "0000320193",
                "name": "Apple Inc.",
                "ticker": "AAPL",
                "source_url": "https://data.sec.gov/submissions/CIK0000320193.json",
            },
        },
        "gleif": {
            "source_record_id": "gleif:lei:semiconductor-public-sample",
            "event_time": _utc(4, 30, 10),
            "payload_format": "json",
            "raw_payload": {
                "entities": [
                    "TSMC / 台积电",
                    "ASML Holding N.V.",
                    "Samsung Electronics Co., Ltd.",
                ],
                "source_url": "https://api.gleif.org/api/v1/lei-records",
            },
        },
        "gdelt": {
            "source_record_id": "gdelt:event:red-sea-semiconductor-logistics",
            "event_time": _utc(4, 25, 6),
            "payload_format": "json",
            "raw_payload": {
                "theme": "shipping_disruption",
                "query": "semiconductor logistics Red Sea disruption",
                "source_url": "https://www.gdeltproject.org/",
            },
        },
        "world_bank": {
            "source_record_id": "world_bank:indicator:logistics-context",
            "event_time": _utc(4, 30, 0),
            "payload_format": "json",
            "raw_payload": {
                "indicator": "trade_logistics_context",
                "countries": ["US", "TW", "NL", "KR"],
                "source_url": "https://api.worldbank.org/v2/",
            },
        },
        "ofac": {
            "source_record_id": "ofac:sanctions:semiconductor-policy-context",
            "event_time": _utc(5, 1, 9),
            "payload_format": "json",
            "raw_payload": {
                "list": "sanctions_list_service",
                "policy_context": "export_controls_and_sanctions_monitoring",
                "source_url": "https://ofac.treasury.gov/sanctions-list-service",
            },
        },
        "ourairports": {
            "source_record_id": "ourairports:airport-reference:tw-nl-us-kr",
            "event_time": _utc(5, 1, 8),
            "payload_format": "csv",
            "raw_payload": {
                "dataset": "airports.csv",
                "countries": ["TW", "NL", "US", "KR"],
                "source_url": "https://ourairports.com/data/",
            },
        },
        "nga_world_port_index": {
            "source_record_id": "nga_wpi:ports:kaohsiung-rotterdam",
            "event_time": _utc(5, 1, 7),
            "payload_format": "zip",
            "raw_payload": {
                "ports": ["Port of Kaohsiung", "Port of Rotterdam"],
                "source_url": "https://msi.nga.mil/Publications/WPI",
            },
        },
        "usgs_earthquakes": {
            "source_record_id": "usgs:earthquakes:m4-5-month",
            "event_time": _utc(5, 1, 6),
            "payload_format": "json",
            "raw_payload": {
                "feed": "M4.5+ earthquakes past month",
                "hazard_context": "recent seismic events that can transmit risk into ports, airports, and regional supply corridors",
                "source_url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson",
            },
        },
    }
    for source_id, records in catalog_records_by_source.items():
        if source_id not in source_payloads:
            continue
        source_payloads[source_id]["raw_payload"]["catalog_version"] = catalog["catalog_version"]
        source_payloads[source_id]["raw_payload"]["catalog_entities"] = records["entities"]
        source_payloads[source_id]["raw_payload"]["catalog_edges"] = records["edges"]
    batches = {}
    for source_id, payload in source_payloads.items():
        connector = connector_for_source(source_id)
        event_time = payload["event_time"]
        batches[source_id] = connector.ingest_sample(
            source_record_id=payload["source_record_id"],
            event_time=event_time,
            published_time=event_time + timedelta(hours=1),
            observed_time=as_of_time - timedelta(hours=2),
            ingest_time=as_of_time,
            raw_payload=payload["raw_payload"],
            payload_format=payload["payload_format"],
        )
    return batches


def public_real_sources(as_of_time: datetime = PUBLIC_REAL_AS_OF_TIME) -> list[SourceRegistry]:
    registry = load_source_registry()
    created_at = as_of_time - timedelta(days=14)
    reliability_by_source = {
        "sec_edgar": 0.95,
        "gleif": 0.96,
        "gdelt": 0.82,
        "world_bank": 0.94,
        "ofac": 0.98,
        "ourairports": 0.88,
        "nga_world_port_index": 0.9,
        "usgs_earthquakes": 0.93,
    }
    return [
        SourceRegistry(
            source_id=entry.source_id,
            source_name=entry.source_name,
            source_type=entry.endpoints[0].name if entry.endpoints else entry.update_cadence,
            license_type=entry.license.name,
            update_frequency=entry.update_cadence,
            reliability_score=reliability_by_source.get(entry.source_id, 0.8),
            owner=entry.owner,
            created_at=created_at,
        )
        for entry in registry.sources
    ]


def build_public_real_dataset(as_of_time: datetime = PUBLIC_REAL_AS_OF_TIME) -> PublicRealDataset:
    catalog = _load_public_real_node_catalog()
    catalog_source, promoted_manifest = _catalog_source()
    sources = public_real_sources(as_of_time)
    raw_batches = _ingest_public_real_raw_records(as_of_time)
    raw_records = [record for batch in raw_batches.values() for record in batch.records]
    source_manifests = [batch.manifest for batch in raw_batches.values()]
    source_ids = sorted(raw_batches)
    source_manifest_checksum = _checksum(
        {
            "sources": source_ids,
            "as_of_time": as_of_time.isoformat(),
            "raw_checksums": sorted(
                checksum for batch in raw_batches.values() for checksum in batch.manifest.raw_checksums
            ),
            "manifest_checksums": sorted(batch.manifest.manifest_checksum for batch in raw_batches.values()),
        }
    )
    source_manifest_ref = f"manifest_public_real_{source_manifest_checksum[:12]}"
    freshness = sorted(
        [
        SourceFreshness(
            source_id=batch.manifest.source_id,
            status="fresh" if batch.manifest.is_fresh else batch.manifest.status,
            last_successful_ingest=batch.manifest.checked_at,
            max_stale_minutes=batch.manifest.freshness_sla_hours * 60,
            record_count=batch.manifest.raw_record_count,
            checksum=batch.manifest.manifest_checksum,
        )
        for batch in raw_batches.values()
        ],
        key=lambda item: item.source_id,
    )
    source_ref_by_id = {
        source_id: SourceReference(
            source_id=batch.records[0].source_id,
            raw_id=batch.records[0].raw_id,
            source_record_id=batch.records[0].source_record_id,
        )
        for source_id, batch in raw_batches.items()
        if batch.records
    }
    entities = [
        CanonicalEntity(
            canonical_id="firm_apple",
            entity_type="firm",
            display_name="Apple Inc.",
            country="US",
            industry="Consumer electronics",
            external_ids={"sec_cik": "0000320193", "ticker": "AAPL"},
            confidence=0.99,
            created_at=as_of_time - timedelta(days=30),
            updated_at=as_of_time - timedelta(hours=2),
        ),
        CanonicalEntity(
            canonical_id="firm_tsmc",
            entity_type="firm",
            display_name="TSMC / 台积电",
            country="TW",
            industry="Semiconductors",
            external_ids={"ticker": "2330.TW"},
            confidence=0.96,
            created_at=as_of_time - timedelta(days=30),
            updated_at=as_of_time - timedelta(hours=3),
        ),
        CanonicalEntity(
            canonical_id="firm_asml",
            entity_type="firm",
            display_name="ASML Holding N.V.",
            country="NL",
            industry="Semiconductor equipment",
            external_ids={"ticker": "ASML"},
            confidence=0.96,
            created_at=as_of_time - timedelta(days=30),
            updated_at=as_of_time - timedelta(hours=4),
        ),
        CanonicalEntity(
            canonical_id="firm_samsung_electronics",
            entity_type="firm",
            display_name="Samsung Electronics Co., Ltd.",
            country="KR",
            industry="Electronics and semiconductors",
            external_ids={"ticker": "005930.KS"},
            confidence=0.95,
            created_at=as_of_time - timedelta(days=30),
            updated_at=as_of_time - timedelta(hours=4),
        ),
        CanonicalEntity(
            canonical_id="country_us",
            entity_type="country",
            display_name="United States",
            country="US",
            industry=None,
            external_ids={"iso2": "US"},
            confidence=1.0,
        ),
        CanonicalEntity(
            canonical_id="region_china_taiwan",
            entity_type="country",
            display_name="中国台湾",
            country="TW",
            industry=None,
            external_ids={"iso2": "TW"},
            confidence=1.0,
        ),
        CanonicalEntity(
            canonical_id="country_nl",
            entity_type="country",
            display_name="Netherlands",
            country="NL",
            industry=None,
            external_ids={"iso2": "NL"},
            confidence=1.0,
        ),
        CanonicalEntity(
            canonical_id="country_kr",
            entity_type="country",
            display_name="South Korea",
            country="KR",
            industry=None,
            external_ids={"iso2": "KR"},
            confidence=1.0,
        ),
        CanonicalEntity(
            canonical_id="port_kaohsiung",
            entity_type="port",
            display_name="Port of Kaohsiung",
            country="TW",
            industry="Maritime logistics",
            external_ids={"source": "NGA World Port Index"},
            confidence=0.92,
        ),
        CanonicalEntity(
            canonical_id="port_rotterdam",
            entity_type="port",
            display_name="Port of Rotterdam",
            country="NL",
            industry="Maritime logistics",
            external_ids={"source": "NGA World Port Index"},
            confidence=0.93,
        ),
        CanonicalEntity(
            canonical_id="product_advanced_semiconductors",
            entity_type="product",
            display_name="Advanced semiconductors",
            country=None,
            industry="HS 8542",
            external_ids={"hs_code": "8542"},
            confidence=0.9,
        ),
        CanonicalEntity(
            canonical_id="policy_ofac_sanctions",
            entity_type="policy",
            display_name="OFAC sanctions exposure",
            country="US",
            industry="Sanctions",
            external_ids={"source": "OFAC Sanctions List Service"},
            confidence=0.98,
        ),
        CanonicalEntity(
            canonical_id="risk_event_red_sea_disruption",
            entity_type="risk_event",
            display_name="Red Sea shipping disruption",
            country=None,
            industry="Logistics risk",
            external_ids={"source": "GDELT"},
            confidence=0.82,
        ),
        CanonicalEntity(
            canonical_id="text_gdelt_semiconductor_logistics",
            entity_type="text_artifact",
            display_name="GDELT semiconductor logistics signal",
            country=None,
            industry="News evidence",
            external_ids={"source": "GDELT"},
            confidence=0.78,
        ),
    ]
    entities, source_by_entity = _catalog_entities(catalog, as_of_time)

    def edge(
        source_id: str,
        target_id: str,
        edge_type: str,
        source: str,
        event_time: datetime,
        confidence: float,
        **attributes: Any,
    ) -> EdgeEvent:
        return EdgeEvent(
            edge_event_id=_event_id(source, source_id, target_id, edge_type),
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            event_type="create",
            event_time=event_time,
            published_time=event_time + timedelta(hours=2),
            observed_time=event_time + timedelta(hours=6),
            ingest_time=event_time + timedelta(hours=6),
            attributes={
                "valid_from": event_time,
                "source_manifest_ref": source_manifest_ref,
                **attributes,
            },
            confidence=confidence,
            source=source,
        )

    edge_events = [
        edge("firm_apple", "country_us", "located_in", "sec_edgar", _utc(4, 2), 0.98, weight=1.0),
        edge("firm_tsmc", "region_china_taiwan", "located_in", "gleif", _utc(4, 2), 0.96, weight=1.0),
        edge("firm_asml", "country_nl", "located_in", "gleif", _utc(4, 2), 0.96, weight=1.0),
        edge("firm_samsung_electronics", "country_kr", "located_in", "gleif", _utc(4, 2), 0.95, weight=1.0),
        edge(
            "firm_tsmc",
            "product_advanced_semiconductors",
            "produces",
            "gleif",
            _utc(4, 3),
            0.88,
            weight=0.91,
            risk_score=0.31,
        ),
        edge(
            "firm_samsung_electronics",
            "product_advanced_semiconductors",
            "produces",
            "gleif",
            _utc(4, 3),
            0.84,
            weight=0.78,
            risk_score=0.24,
        ),
        edge(
            "firm_tsmc",
            "port_kaohsiung",
            "ships_through",
            "nga_world_port_index",
            _utc(4, 5),
            0.82,
            weight=0.74,
            risk_score=0.42,
            route_dependency=0.58,
        ),
        edge(
            "port_kaohsiung",
            "port_rotterdam",
            "route_connects",
            "nga_world_port_index",
            _utc(4, 5),
            0.78,
            weight=0.62,
            risk_score=0.46,
        ),
        edge(
            "policy_ofac_sanctions",
            "product_advanced_semiconductors",
            "policy_targets",
            "ofac",
            _utc(4, 9),
            0.91,
            severity=0.53,
            risk_score=0.53,
        ),
        edge(
            "risk_event_red_sea_disruption",
            "firm_apple",
            "event_affects",
            "gdelt",
            _utc(4, 18),
            0.72,
            severity=0.61,
            risk_score=0.61,
        ),
        edge(
            "risk_event_red_sea_disruption",
            "firm_asml",
            "event_affects",
            "gdelt",
            _utc(4, 18),
            0.69,
            severity=0.49,
            risk_score=0.49,
        ),
        edge(
            "text_gdelt_semiconductor_logistics",
            "firm_tsmc",
            "co_mentions",
            "gdelt",
            _utc(4, 25),
            0.76,
            sentiment=-0.34,
            mention_count=17,
            risk_score=0.57,
        ),
        edge(
            "firm_tsmc",
            "firm_apple",
            "risk_transmits_to",
            "gdelt",
            _utc(4, 26),
            0.68,
            path_risk=0.64,
            lag_days=14,
            risk_score=0.64,
        ),
    ]
    edge_events = _catalog_edge_events(catalog, source_manifest_ref)
    silver_entities = _build_silver_entities(entities, source_ref_by_id, source_by_entity)
    silver_events = _build_silver_events(source_ref_by_id, as_of_time)
    gold_edge_events = [
        GoldEdgeEvent(
            edge_event_id=edge.edge_event_id,
            source_entity_id=edge.source_id,
            target_entity_id=edge.target_id,
            edge_type=edge.edge_type,
            event_type=edge.event_type,
            event_time=edge.event_time,
            published_time=edge.published_time or edge.event_time,
            observed_time=edge.observed_time or edge.ingest_time,
            ingest_time=edge.ingest_time,
            source_refs=[source_ref_by_id[edge.source]],
            evidence_event_ids=[event.event_id for event in silver_events if event.source_refs[0].source_id == edge.source],
            attributes=edge.attributes,
            confidence=edge.confidence,
        )
        for edge in edge_events
    ]
    return PublicRealDataset(
        sources=sources,
        freshness=freshness,
        raw_records=raw_records,
        source_manifests=source_manifests,
        silver_entities=silver_entities,
        silver_events=silver_events,
        gold_edge_events=gold_edge_events,
        entities=entities,
        edge_events=edge_events,
        source_manifest_ref=source_manifest_ref,
        source_manifest_checksum=source_manifest_checksum,
        catalog_source=catalog_source,
        promoted_manifest=promoted_manifest,
    )


def _build_silver_entities(
    entities: list[CanonicalEntity],
    source_ref_by_id: dict[str, SourceReference],
    source_by_entity: dict[str, str],
) -> list[SilverEntity]:
    entity_type_map = {
        "firm": "company",
        "legal_entity": "legal_entity",
        "country": "country",
        "port": "port",
        "airport": "airport",
        "product": "commodity",
        "policy": "sanctioned_party",
        "risk_event": "location",
        "text_artifact": "location",
        "data_source": "data_source",
        "data_category": "data_category",
        "dataset": "dataset",
        "indicator": "indicator",
        "industry": "industry",
        "raw_material": "raw_material",
        "component": "component",
        "product_grade": "product_grade",
        "supplier_tier": "supplier_tier",
        "factory": "factory",
        "warehouse": "warehouse",
        "route_lane": "route_lane",
        "carrier": "carrier",
        "schema_field": "schema_field",
        "license_policy": "license_policy",
        "coverage_area": "coverage_area",
        "source_release": "source_release",
        "observation_series": "observation_series",
    }
    silver_entities: list[SilverEntity] = []
    for entity in entities:
        source_id = source_by_entity[entity.canonical_id]
        silver_entities.append(
            SilverEntity(
                entity_id=entity.canonical_id,
                entity_type=entity_type_map.get(entity.entity_type, "dataset"),
                display_name=entity.display_name,
                source_refs=[source_ref_by_id[source_id]],
                country_code=entity.country,
                external_ids=entity.external_ids,
                attributes={"domain_entity_type": entity.entity_type, "industry": entity.industry},
                confidence=entity.confidence,
                updated_at=entity.updated_at,
            )
        )
    return silver_entities


def _build_silver_events(
    source_ref_by_id: dict[str, SourceReference],
    as_of_time: datetime,
) -> list[SilverEvent]:
    return [
        SilverEvent(
            event_id="silver_event_gdelt_red_sea_disruption",
            event_type="disruption",
            source_refs=[source_ref_by_id["gdelt"]],
            event_time=_utc(4, 25, 6),
            published_time=_utc(4, 25, 8),
            observed_time=as_of_time - timedelta(hours=2),
            ingest_time=as_of_time,
            entities=[
                {"entity_id": "risk_event_red_sea_disruption", "role": "event"},
                {"entity_id": "firm_apple", "role": "affected"},
            ],
            attributes={"source_manifest_stage": "silver"},
            confidence=0.72,
        ),
        SilverEvent(
            event_id="silver_event_ofac_policy_context",
            event_type="sanctions_update",
            source_refs=[source_ref_by_id["ofac"]],
            event_time=_utc(5, 1, 9),
            published_time=_utc(5, 1, 10),
            observed_time=as_of_time - timedelta(hours=2),
            ingest_time=as_of_time,
            entities=[
                {"entity_id": "policy_ofac_sanctions", "role": "policy"},
                {"entity_id": "product_advanced_semiconductors", "role": "target"},
            ],
            attributes={"source_manifest_stage": "silver"},
            confidence=0.91,
        ),
    ]


def _catalog_cache_key() -> str:
    env_catalog_path = os.environ.get("SUPPLY_RISK_REAL_CATALOG_PATH")
    if env_catalog_path:
        path = Path(env_catalog_path)
        try:
            stat = path.stat()
            return f"env:{path.resolve()}:{stat.st_mtime_ns}:{stat.st_size}"
        except OSError:
            return f"env:{env_catalog_path}:missing"
    promoted_manifest = load_promoted_manifest()
    if promoted_manifest:
        return f"promoted:{promoted_manifest.get('checksum') or promoted_manifest.get('catalog_version')}"
    return "builtin"


def run_public_real_pipeline(
    as_of_time: datetime = PUBLIC_REAL_AS_OF_TIME,
    window_start: datetime = PUBLIC_REAL_WINDOW_START,
) -> RealPipelineResult:
    return _run_public_real_pipeline_cached(as_of_time, window_start, _catalog_cache_key())


@lru_cache(maxsize=8)
def _run_public_real_pipeline_cached(
    as_of_time: datetime,
    window_start: datetime,
    catalog_cache_key: str,
) -> RealPipelineResult:
    real = build_public_real_dataset(as_of_time=as_of_time)
    snapshot, edge_states = build_graph_snapshot(
        real.entities,
        real.edge_events,
        as_of_time=as_of_time,
        window_start=window_start,
    )
    features = compute_features(real.entities, edge_states, snapshot)
    labels: list[object] = []
    paths = build_path_index(edge_states)
    samples = build_dataset(
        prediction_time=as_of_time,
        graph_version=snapshot.graph_version,
        feature_values=features,
        labels=[],
        edge_states=edge_states,
        paths=paths,
    )
    model = BaselineRiskModel()
    predictions = [model.predict(sample, created_at=as_of_time + timedelta(minutes=1)) for sample in samples]
    explanations = [
        ExplanationPath(
            explanation_id=f"explain_{prediction.prediction_id.removeprefix('pred_')}",
            prediction_id=prediction.prediction_id,
            path_id=prediction.top_paths[0] if prediction.top_paths else "path_public_real",
            node_sequence=[],
            edge_sequence=[],
            contribution_score=prediction.risk_score,
            causal_score=min(1.0, prediction.risk_score + 0.08),
            confidence=0.68,
            evidence=[
                "public_no_key_source_manifest",
                real.source_manifest_ref,
                "point_in_time_public_graph",
            ],
        )
        for prediction in predictions
    ]
    return RealPipelineResult(
        real=real,
        snapshot=snapshot,
        edge_states=edge_states,
        features=features,
        labels=labels,
        samples=samples,
        predictions=predictions,
        explanations=explanations,
        label_quality=label_quality_report([]),
    )


def real_metadata(result: RealPipelineResult) -> VersionMetadata:
    first_feature_version = result.features[0].feature_version if result.features else "f_none"
    first_model_version = result.predictions[0].model_version if result.predictions else "model_none"
    promoted_status = (result.real.promoted_manifest or {}).get("source_status")
    freshness_status = (
        "partial"
        if result.real.catalog_source != "promoted"
        or promoted_status not in {None, "fresh"}
        or any(item.status != "fresh" for item in result.real.freshness)
        else "fresh"
    )
    return VersionMetadata(
        graph_version=result.snapshot.graph_version,
        feature_version=first_feature_version,
        label_version="l_public_real_unlabeled",
        model_version=first_model_version,
        as_of_time=result.snapshot.as_of_time,
        audit_ref=f"audit_{result.real.source_manifest_ref}",
        lineage_ref=result.real.source_manifest_checksum,
        data_mode="real",
        freshness_status=freshness_status,
        source_count=len(result.real.sources),
        source_manifest_ref=result.real.source_manifest_ref,
    )
