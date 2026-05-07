from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

import yaml

from graph_kernel.snapshot_builder import checksum_payload
from sra_core.contracts.data import payload_checksum
from sra_core.ingestion.registry import load_source_registry


DEFAULT_USER_AGENT = "SupplyRiskAtlas/0.1 public-real-ingestion contact=ops@supplyriskatlas.local"
DEFAULT_CACHE_DIR = Path("data/cache/public_real")
DEFAULT_PROMOTED_DIR = Path("data/promoted/public_real/latest")


@dataclass(frozen=True)
class BulkLimits:
    sec_companies: int = 300
    gleif_legal_entities: int = 200
    world_bank_indicators: int = 180
    world_bank_countries: int = 120
    ourairports_airports: int = 300
    gdelt_articles: int = 60
    ofac_entries: int = 100
    usgs_earthquakes: int = 80


@dataclass(frozen=True)
class CachedSourceFile:
    source_id: str
    url: str
    path: Path
    checksum: str
    status: str
    message: str
    byte_count: int


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_catalog_path() -> Path:
    return project_root() / "configs" / "sources" / "public_real_node_catalog.yaml"


def promoted_catalog_path(root: Path | None = None) -> Path:
    base = root or project_root()
    return base / DEFAULT_PROMOTED_DIR / "catalog.json"


def promoted_manifest_path(root: Path | None = None) -> Path:
    base = root or project_root()
    return base / DEFAULT_PROMOTED_DIR / "manifest.json"


def load_promoted_manifest(root: Path | None = None) -> dict[str, Any] | None:
    path = promoted_manifest_path(root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_promoted_catalog(root: Path | None = None) -> dict[str, Any] | None:
    path = promoted_catalog_path(root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_bulk_catalog(
    *,
    mode: str = "online",
    cache_dir: Path | None = None,
    limits: BulkLimits = BulkLimits(),
    as_of_time: datetime | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    as_of_time = as_of_time or datetime(2026, 5, 2, tzinfo=timezone.utc)
    cache_dir = cache_dir or project_root() / DEFAULT_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    base_catalog = _load_base_catalog()
    builder = _BulkCatalogBuilder(base_catalog)
    source_files = _download_or_seed_sources(mode=mode, cache_dir=cache_dir, limits=limits)

    source_registry = load_source_registry()
    source_by_id = {source.source_id: source for source in source_registry.sources}
    builder.add_source_governance_nodes(source_by_id, source_files, as_of_time)
    builder.add_sec_company_nodes(_load_sec_company_tickers(source_files, limits.sec_companies))
    builder.add_gleif_legal_entity_nodes(_load_gleif_lei_records(source_files, limits.gleif_legal_entities))
    builder.add_world_bank_nodes(
        _load_world_bank_countries(source_files, limits.world_bank_countries),
        _load_world_bank_indicators(source_files, limits.world_bank_indicators),
    )
    builder.add_ourairports_nodes(_load_ourairports_airports(source_files, limits.ourairports_airports))
    builder.add_gdelt_nodes(_load_gdelt_articles(source_files, limits.gdelt_articles))
    builder.add_ofac_nodes(_load_ofac_entries(source_files, limits.ofac_entries))
    builder.add_wpi_seed_ports()
    builder.add_usgs_earthquake_nodes(_load_usgs_earthquakes(source_files, limits.usgs_earthquakes))

    catalog = builder.catalog()
    manifest = {
        "schema_version": "promoted-public-real-v1",
        "catalog_version": catalog["catalog_version"],
        "generated_at": as_of_time.isoformat(),
        "as_of_time": as_of_time.isoformat(),
        "cache_dir": str(cache_dir.as_posix()),
        "raw_data_in_git": False,
        "mode": mode,
        "source_status": "fresh"
        if all(item.status == "ok" for item in source_files.values())
        else "partial",
        "source_files": [
            {
                "source_id": item.source_id,
                "url": item.url,
                "cache_path": str(item.path.as_posix()),
                "checksum": item.checksum,
                "status": item.status,
                "message": item.message,
                "byte_count": item.byte_count,
            }
            for item in sorted(source_files.values(), key=lambda value: value.source_id)
        ],
        "record_counts": {
            "entities": len(catalog["entities"]),
            "edges": len(catalog["edges"]),
            "raw_files": len(source_files),
        },
        "checksum": checksum_payload(
            {
                "catalog_version": catalog["catalog_version"],
                "entities": catalog["entities"],
                "edges": catalog["edges"],
            }
        ),
    }
    return catalog, manifest


def write_promoted_catalog(
    *,
    mode: str = "online",
    cache_dir: Path | None = None,
    promoted_dir: Path | None = None,
    limits: BulkLimits = BulkLimits(),
) -> dict[str, Any]:
    catalog, manifest = build_bulk_catalog(mode=mode, cache_dir=cache_dir, limits=limits)
    promoted_dir = promoted_dir or project_root() / DEFAULT_PROMOTED_DIR
    promoted_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = promoted_dir / "catalog.json"
    manifest_path = promoted_dir / "manifest.json"
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    return {
        **manifest,
        "catalog_path": str(catalog_path),
        "manifest_path": str(manifest_path),
    }


class _BulkCatalogBuilder:
    def __init__(self, base_catalog: dict[str, Any]) -> None:
        self.entities: dict[str, dict[str, Any]] = {
            entity["canonical_id"]: dict(entity)
            for entity in base_catalog.get("entities", [])
        }
        self.edges: dict[tuple[str, str, str, str], dict[str, Any]] = {
            (edge["source"], edge["source_id"], edge["target_id"], edge["edge_type"]): dict(edge)
            for edge in base_catalog.get("edges", [])
        }

    def catalog(self) -> dict[str, Any]:
        digest = checksum_payload(
            {
                "entities": sorted(self.entities),
                "edges": sorted("|".join(key) for key in self.edges),
            }
        )[:12]
        return {
            "catalog_version": f"public-real-bulk-{digest}",
            "entities": sorted(self.entities.values(), key=lambda item: item["canonical_id"]),
            "edges": sorted(
                self.edges.values(),
                key=lambda item: (item["source"], item["edge_type"], item["source_id"], item["target_id"]),
            ),
        }

    def add_entity(
        self,
        canonical_id: str,
        entity_type: str,
        display_name: str,
        source_id: str,
        *,
        country: str | None = None,
        industry: str | None = None,
        confidence: float = 0.82,
        external_ids: dict[str, Any] | None = None,
    ) -> None:
        if canonical_id in self.entities:
            return
        geo = _geo_metadata(canonical_id, entity_type, country)
        external_id_values = {
            key: str(value)
            for key, value in (external_ids or {}).items()
            if value is not None and value != ""
        }
        external_id_values.update(
            {
                key: str(value)
                for key, value in {
                    "geoId": geo.get("geoId"),
                    "geoLevel": geo.get("geoLevel"),
                    "countryCode": geo.get("countryCode"),
                    "provinceCode": geo.get("provinceCode"),
                    "parentGeoId": geo.get("parentGeoId"),
                    "sourceCountryCode": geo.get("sourceCountryCode"),
                }.items()
                if value is not None and value != ""
            }
        )
        self.entities[canonical_id] = {
            "canonical_id": canonical_id,
            "entity_type": entity_type,
            "display_name": display_name,
            "displayName": display_name,
            "country": geo.get("countryCode") or country,
            "industry": industry,
            "geoId": geo.get("geoId"),
            "geoLevel": geo.get("geoLevel"),
            "countryCode": geo.get("countryCode"),
            "provinceCode": geo.get("provinceCode"),
            "parentGeoId": geo.get("parentGeoId"),
            "sourceCountryCode": geo.get("sourceCountryCode"),
            "external_ids": external_id_values,
            "confidence": confidence,
            "source_id": source_id,
        }

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        source: str,
        *,
        confidence: float = 0.8,
        day: int = 2,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        if source_id not in self.entities or target_id not in self.entities:
            return
        key = (source, source_id, target_id, edge_type)
        if key in self.edges:
            return
        self.edges[key] = {
            "source_id": source_id,
            "target_id": target_id,
            "edge_type": edge_type,
            "source": source,
            "confidence": confidence,
            "day": max(1, min(28, day)),
            "attributes": {
                "weight": round(confidence, 4),
                "risk_score": round(max(0.01, 1.0 - confidence), 4),
                **(attributes or {}),
            },
        }

    def add_source_governance_nodes(
        self,
        source_by_id: dict[str, Any],
        source_files: dict[str, CachedSourceFile],
        as_of_time: datetime,
    ) -> None:
        self.add_entity(
            "coverage_area_global",
            "coverage_area",
            "Global public-source coverage",
            "world_bank",
            industry="Data coverage",
            confidence=0.95,
            external_ids={"coverage": "global"},
        )
        for source_id, source in source_by_id.items():
            data_source_id = f"data_source_{source_id}"
            self.add_entity(
                data_source_id,
                "data_source",
                source.source_name,
                source_id,
                industry="Public data source",
                confidence=0.97,
                external_ids={"source_id": source_id, "homepage_url": source.homepage_url},
            )
            license_id = f"license_policy_{source_id}"
            self.add_entity(
                license_id,
                "license_policy",
                source.license.name,
                source_id,
                industry="Data license",
                confidence=0.94,
                external_ids={
                    "license_url": source.license.url,
                    "commercial_use_allowed": source.license.commercial_use_allowed,
                    "redistribution_allowed": source.license.redistribution_allowed,
                },
            )
            release_id = f"source_release_{source_id}_{as_of_time.strftime('%Y%m%d')}"
            source_file = source_files.get(source_id) or next(
                (item for item in source_files.values() if item.source_id == source_id),
                None,
            )
            self.add_entity(
                release_id,
                "source_release",
                f"{source.source_name} cached pull {as_of_time.date().isoformat()}",
                source_id,
                industry="Bulk source release",
                confidence=0.9 if source_file and source_file.status == "ok" else 0.62,
                external_ids={
                    "checksum": source_file.checksum if source_file else "unavailable",
                    "status": source_file.status if source_file else "unavailable",
                    "cache_path": source_file.path.as_posix() if source_file else "",
                },
            )
            self.add_edge(data_source_id, license_id, "licensed_under", source_id, confidence=0.94, day=2)
            self.add_edge(data_source_id, release_id, "released_as", source_id, confidence=0.9, day=2)
            self.add_edge(release_id, "coverage_area_global", "dataset_covers", source_id, confidence=0.76, day=2)

    def add_sec_company_nodes(self, rows: list[dict[str, Any]]) -> None:
        self.add_entity(
            "dataset_sec_company_tickers",
            "dataset",
            "SEC company tickers",
            "sec_edgar",
            industry="Issuer reference data",
            confidence=0.96,
            external_ids={"endpoint": "https://www.sec.gov/files/company_tickers.json"},
        )
        self.add_edge("data_source_sec_edgar", "dataset_sec_company_tickers", "source_provides", "sec_edgar", confidence=0.96)
        self.add_edge("dataset_sec_company_tickers", "license_policy_sec_edgar", "licensed_under", "sec_edgar", confidence=0.94)
        self._add_schema_fields("dataset_sec_company_tickers", "sec_edgar", ["cik_str", "ticker", "title"])
        self.add_entity("industry_public_companies", "industry", "Public companies", "sec_edgar", confidence=0.9)
        for index, row in enumerate(rows, start=1):
            cik = str(row.get("cik_str") or row.get("cik") or "").zfill(10)
            title = str(row.get("title") or row.get("name") or "").strip()
            ticker = str(row.get("ticker") or "").strip()
            if not cik or not title:
                continue
            firm_id = self._find_entity_by_external_id("sec_cik", cik) or f"firm_sec_{cik}"
            if firm_id not in self.entities:
                self.add_entity(
                    firm_id,
                    "firm",
                    title,
                    "sec_edgar",
                    country="US",
                    industry="Public company",
                    confidence=0.9,
                    external_ids={"sec_cik": cik, "ticker": ticker},
                )
            self.add_edge("dataset_sec_company_tickers", firm_id, "dataset_observes", "sec_edgar", confidence=0.88, day=3 + index % 20)
            self.add_edge(firm_id, "country_us", "located_in", "sec_edgar", confidence=0.86, day=3 + index % 20)
            self.add_edge(firm_id, "industry_public_companies", "classified_as", "sec_edgar", confidence=0.78, day=3 + index % 20)

    def add_gleif_legal_entity_nodes(self, rows: list[dict[str, Any]]) -> None:
        self.add_entity(
            "dataset_gleif_lei_records_bulk",
            "dataset",
            "GLEIF LEI records",
            "gleif",
            industry="Legal entity reference data",
            confidence=0.97,
            external_ids={"endpoint": "https://api.gleif.org/api/v1/lei-records"},
        )
        self.add_edge("data_source_gleif", "dataset_gleif_lei_records_bulk", "source_provides", "gleif", confidence=0.97)
        self.add_edge("dataset_gleif_lei_records_bulk", "license_policy_gleif", "licensed_under", "gleif", confidence=0.96)
        self._add_schema_fields("dataset_gleif_lei_records_bulk", "gleif", ["lei", "legalName", "legalAddress.country"])
        for index, row in enumerate(rows, start=1):
            lei = str(row.get("lei") or "").strip()
            name = str(row.get("name") or "").strip()
            country = _country_code(row.get("country"))
            if not lei or not name:
                continue
            entity_id = f"legal_entity_lei_{_slug(lei, max_length=24)}"
            self.add_entity(
                entity_id,
                "legal_entity",
                name,
                "gleif",
                country=country,
                industry="Legal entity",
                confidence=0.89,
                external_ids={"lei": lei},
            )
            country_id = self._ensure_country(country, "gleif")
            self.add_edge("dataset_gleif_lei_records_bulk", entity_id, "dataset_observes", "gleif", confidence=0.9, day=3 + index % 20)
            if country_id:
                self.add_edge(entity_id, country_id, "located_in", "gleif", confidence=0.84, day=3 + index % 20)

    def add_world_bank_nodes(
        self,
        countries: list[dict[str, Any]],
        indicators: list[dict[str, Any]],
    ) -> None:
        self.add_entity(
            "dataset_world_bank_indicator_bulk",
            "dataset",
            "World Bank indicator catalog bulk",
            "world_bank",
            industry="Macro indicators",
            confidence=0.96,
            external_ids={"endpoint": "https://api.worldbank.org/v2/indicator"},
        )
        self.add_edge("data_source_world_bank", "dataset_world_bank_indicator_bulk", "source_provides", "world_bank", confidence=0.96)
        self.add_edge("dataset_world_bank_indicator_bulk", "license_policy_world_bank", "licensed_under", "world_bank", confidence=0.95)
        self._add_schema_fields("dataset_world_bank_indicator_bulk", "world_bank", ["id", "name", "sourceNote", "sourceOrganization"])
        country_ids: list[str] = []
        for country in countries:
            iso2 = _country_code(country.get("iso2") or country.get("id"))
            name = str(country.get("name") or "").strip()
            if not iso2 or not name:
                continue
            country_id = self._ensure_country(iso2, "world_bank", name=name)
            if country_id:
                country_ids.append(country_id)
                self.add_edge("dataset_world_bank_indicator_bulk", country_id, "dataset_covers", "world_bank", confidence=0.9, day=4)
        for index, indicator in enumerate(indicators, start=1):
            indicator_code = str(indicator.get("id") or "").strip()
            name = str(indicator.get("name") or "").strip()
            if not indicator_code or not name:
                continue
            indicator_id = f"indicator_wb_{_slug(indicator_code, max_length=42)}"
            self.add_entity(
                indicator_id,
                "indicator",
                name,
                "world_bank",
                industry="World Bank indicator",
                confidence=0.92,
                external_ids={
                    "indicator_code": indicator_code,
                    "source_note": str(indicator.get("sourceNote") or "")[:240],
                },
            )
            self.add_edge("dataset_world_bank_indicator_bulk", indicator_id, "dataset_measures", "world_bank", confidence=0.92, day=5 + index % 20)
            if country_ids:
                target_country = country_ids[index % len(country_ids)]
                target_source_code = _source_code_for_geo_id(target_country)
                series_id = f"observation_series_wb_{_slug(indicator_code, max_length=34)}_{_slug(target_country, max_length=24)}"
                self.add_entity(
                    series_id,
                    "observation_series",
                    f"{indicator_code} observations for {target_source_code}",
                    "world_bank",
                    country=target_source_code,
                    industry="Macro time series",
                    confidence=0.86,
                    external_ids={"indicator_code": indicator_code, "country_node": target_country},
                )
                self.add_edge(indicator_id, target_country, "indicator_context_for", "world_bank", confidence=0.82, day=5 + index % 20)
                self.add_edge(series_id, target_country, "observed_for", "world_bank", confidence=0.82, day=5 + index % 20)

    def add_ourairports_nodes(self, rows: list[dict[str, Any]]) -> None:
        self.add_entity(
            "dataset_ourairports_airports_bulk",
            "dataset",
            "OurAirports airports.csv bulk",
            "ourairports",
            industry="Airport infrastructure",
            confidence=0.94,
            external_ids={"endpoint": "https://davidmegginson.github.io/ourairports-data/airports.csv"},
        )
        self.add_edge("data_source_ourairports", "dataset_ourairports_airports_bulk", "source_provides", "ourairports", confidence=0.94)
        self.add_edge("dataset_ourairports_airports_bulk", "license_policy_ourairports", "licensed_under", "ourairports", confidence=0.94)
        self._add_schema_fields("dataset_ourairports_airports_bulk", "ourairports", ["ident", "type", "name", "iso_country", "latitude_deg", "longitude_deg"])
        for index, row in enumerate(rows, start=1):
            ident = str(row.get("ident") or row.get("gps_code") or row.get("iata_code") or "").strip()
            name = str(row.get("name") or "").strip()
            iso2 = _country_code(row.get("iso_country"))
            if not ident or not name or not iso2:
                continue
            airport_id = f"airport_{_slug(ident, max_length=18)}"
            self.add_entity(
                airport_id,
                "airport",
                name,
                "ourairports",
                country=iso2,
                industry=str(row.get("type") or "Airport"),
                confidence=0.87,
                external_ids={
                    "ident": ident,
                    "iata_code": row.get("iata_code") or "",
                    "latitude": row.get("latitude_deg") or "",
                    "longitude": row.get("longitude_deg") or "",
                },
            )
            country_id = self._ensure_country(iso2, "ourairports")
            self.add_edge("dataset_ourairports_airports_bulk", airport_id, "dataset_observes", "ourairports", confidence=0.88, day=6 + index % 18)
            if country_id:
                self.add_edge(airport_id, country_id, "located_in", "ourairports", confidence=0.86, day=6 + index % 18)

    def add_gdelt_nodes(self, rows: list[dict[str, Any]]) -> None:
        self.add_entity(
            "dataset_gdelt_supply_chain_articles",
            "dataset",
            "GDELT supply-chain risk article stream",
            "gdelt",
            industry="News event stream",
            confidence=0.82,
            external_ids={"endpoint": "https://api.gdeltproject.org/api/v2/doc/doc"},
        )
        self.add_edge("data_source_gdelt", "dataset_gdelt_supply_chain_articles", "source_provides", "gdelt", confidence=0.82)
        self.add_edge("dataset_gdelt_supply_chain_articles", "license_policy_gdelt", "licensed_under", "gdelt", confidence=0.8)
        self._add_schema_fields("dataset_gdelt_supply_chain_articles", "gdelt", ["title", "url", "domain", "seendate", "sourceCountry"])
        for index, row in enumerate(rows, start=1):
            title = str(row.get("title") or "").strip()
            url = str(row.get("url") or "").strip()
            if not title:
                continue
            artifact_id = f"text_gdelt_{_slug(title, max_length=52)}"
            self.add_entity(
                artifact_id,
                "text_artifact",
                title[:160],
                "gdelt",
                country=_country_code(row.get("sourceCountry")),
                industry="News evidence",
                confidence=0.72,
                external_ids={"url": url, "domain": row.get("domain") or ""},
            )
            self.add_edge("dataset_gdelt_supply_chain_articles", artifact_id, "dataset_observes", "gdelt", confidence=0.74, day=8 + index % 16)

    def add_usgs_earthquake_nodes(self, rows: list[dict[str, Any]]) -> None:
        self.add_entity(
            "dataset_usgs_m45_earthquakes_month",
            "dataset",
            "USGS M4.5+ earthquakes past month GeoJSON",
            "usgs_earthquakes",
            industry="Natural hazard event stream",
            confidence=0.95,
            external_ids={"endpoint": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson"},
        )
        self.add_edge("data_source_usgs_earthquakes", "dataset_usgs_m45_earthquakes_month", "source_provides", "usgs_earthquakes", confidence=0.95)
        self.add_edge("dataset_usgs_m45_earthquakes_month", "license_policy_usgs_earthquakes", "licensed_under", "usgs_earthquakes", confidence=0.93)
        self._add_schema_fields("dataset_usgs_m45_earthquakes_month", "usgs_earthquakes", ["id", "mag", "place", "time", "updated", "url", "geometry.coordinates"])
        for index, row in enumerate(rows, start=1):
            event_id = str(row.get("id") or row.get("code") or "").strip()
            place = str(row.get("place") or "").strip()
            magnitude = _float_or_none(row.get("mag"))
            if not event_id or not place or magnitude is None:
                continue
            iso2 = _country_from_usgs_place(place)
            canonical_id = f"risk_event_usgs_eq_{_slug(event_id, max_length=34)}"
            risk_score = min(0.96, max(0.44, 0.12 + (magnitude / 8.0)))
            self.add_entity(
                canonical_id,
                "risk_event",
                f"M{magnitude:.1f} earthquake near {place}",
                "usgs_earthquakes",
                country=iso2,
                industry="Earthquake hazard",
                confidence=0.9,
                external_ids={
                    "usgs_event_id": event_id,
                    "magnitude": f"{magnitude:.1f}",
                    "place": place,
                    "time": row.get("time") or "",
                    "url": row.get("url") or "",
                    "longitude": row.get("longitude") or "",
                    "latitude": row.get("latitude") or "",
                    "depth_km": row.get("depth_km") or "",
                },
            )
            self.add_edge(
                "dataset_usgs_m45_earthquakes_month",
                canonical_id,
                "dataset_observes",
                "usgs_earthquakes",
                confidence=0.9,
                day=9 + index % 17,
                attributes={"risk_score": risk_score, "weight": 0.92, "magnitude": magnitude},
            )
            country_id = self._ensure_country(iso2, "usgs_earthquakes") if iso2 else None
            if country_id:
                self.add_edge(
                    canonical_id,
                    country_id,
                    "event_affects",
                    "usgs_earthquakes",
                    confidence=0.86,
                    day=9 + index % 17,
                    attributes={"risk_score": risk_score, "weight": min(1.0, magnitude / 7.0)},
                )
                for target_id in self._country_targets(iso2, limit=4):
                    self.add_edge(
                        canonical_id,
                        target_id,
                        "risk_transmits_to",
                        "usgs_earthquakes",
                        confidence=0.76,
                        day=9 + index % 17,
                        attributes={"risk_score": min(0.98, risk_score + 0.08), "weight": min(1.0, magnitude / 6.5)},
                    )

    def add_ofac_nodes(self, rows: list[dict[str, Any]]) -> None:
        self.add_entity(
            "dataset_ofac_sdn_bulk",
            "dataset",
            "OFAC SDN public sanctions bulk",
            "ofac",
            industry="Sanctions list",
            confidence=0.94,
            external_ids={"endpoint": "OFAC Sanctions List Service"},
        )
        self.add_edge("data_source_ofac", "dataset_ofac_sdn_bulk", "source_provides", "ofac", confidence=0.94)
        self.add_edge("dataset_ofac_sdn_bulk", "license_policy_ofac", "licensed_under", "ofac", confidence=0.94)
        self._add_schema_fields("dataset_ofac_sdn_bulk", "ofac", ["uid", "name", "sdnType", "programList"])
        for index, row in enumerate(rows, start=1):
            uid = str(row.get("uid") or row.get("id") or index)
            name = str(row.get("name") or row.get("lastName") or row.get("title") or "").strip()
            if not name:
                continue
            entity_id = f"legal_entity_ofac_{_slug(uid + '-' + name, max_length=48)}"
            self.add_entity(
                entity_id,
                "legal_entity",
                name[:160],
                "ofac",
                country=_country_code(row.get("country")) or "US",
                industry="Sanctions listed party",
                confidence=0.82,
                external_ids={"ofac_uid": uid, "sdn_type": row.get("sdnType") or ""},
            )
            self.add_edge("dataset_ofac_sdn_bulk", entity_id, "dataset_observes", "ofac", confidence=0.84, day=8 + index % 16)
            self.add_edge("policy_ofac_sanctions", entity_id, "policy_targets", "ofac", confidence=0.76, day=8 + index % 16)

    def add_wpi_seed_ports(self) -> None:
        self.add_entity(
            "dataset_nga_wpi_seed_ports",
            "dataset",
            "NGA World Port Index priority port subset",
            "nga_world_port_index",
            industry="Maritime port reference",
            confidence=0.88,
            external_ids={"endpoint": "https://msi.nga.mil/Publications/WPI"},
        )
        self.add_edge("data_source_nga_world_port_index", "dataset_nga_wpi_seed_ports", "source_provides", "nga_world_port_index", confidence=0.88)
        self.add_edge("dataset_nga_wpi_seed_ports", "license_policy_nga_world_port_index", "licensed_under", "nga_world_port_index", confidence=0.84)
        self._add_schema_fields("dataset_nga_wpi_seed_ports", "nga_world_port_index", ["port_name", "country", "latitude", "longitude"])
        for index, (name, iso2) in enumerate(_WPI_PRIORITY_PORTS, start=1):
            port_id = f"port_wpi_{_slug(name, max_length=42)}"
            self.add_entity(
                port_id,
                "port",
                name,
                "nga_world_port_index",
                country=iso2,
                industry="Maritime logistics",
                confidence=0.84,
                external_ids={"source": "NGA World Port Index"},
            )
            country_id = self._ensure_country(iso2, "nga_world_port_index")
            self.add_edge("dataset_nga_wpi_seed_ports", port_id, "dataset_observes", "nga_world_port_index", confidence=0.84, day=10 + index % 15)
            if country_id:
                self.add_edge(port_id, country_id, "located_in", "nga_world_port_index", confidence=0.83, day=10 + index % 15)

    def _add_schema_fields(self, dataset_id: str, source_id: str, fields: list[str]) -> None:
        for index, field in enumerate(fields, start=1):
            field_id = f"schema_field_{_slug(dataset_id, max_length=34)}_{_slug(field, max_length=26)}"
            self.add_entity(
                field_id,
                "schema_field",
                field,
                source_id,
                industry="Dataset schema",
                confidence=0.86,
                external_ids={"dataset_id": dataset_id, "field_name": field},
            )
            self.add_edge(dataset_id, field_id, "dataset_has_field", source_id, confidence=0.86, day=2 + index)

    def _ensure_country(self, iso2: str | None, source_id: str, *, name: str | None = None) -> str | None:
        iso2 = _country_code(iso2)
        if not iso2:
            return None
        if iso2 == "TW":
            self._ensure_country("CN", source_id, name=_COUNTRY_NAMES["CN"])
            province_id = "province_cn_tw"
            self.add_entity(
                province_id,
                "coverage_area",
                _TAIWAN_PROVINCE_DISPLAY_NAME,
                source_id,
                country="TW",
                confidence=0.9,
                external_ids={
                    "provinceCode": "TW",
                    "sourceCountryCode": "TW",
                    "countryCode": "CN",
                    "parentGeoId": "country_cn",
                    "iso3166_2": "CN-TW",
                },
            )
            self.add_edge(province_id, "country_cn", "part_of", source_id, confidence=0.9, day=4)
            return province_id
        country_id = f"country_{iso2.lower()}"
        self.add_entity(
            country_id,
            "country",
            name or _COUNTRY_NAMES.get(iso2, iso2),
            source_id,
            country=iso2,
            confidence=0.9,
            external_ids={"iso2": iso2},
        )
        return country_id

    def _find_entity_by_external_id(self, key: str, value: str) -> str | None:
        for entity_id, entity in self.entities.items():
            if str((entity.get("external_ids") or {}).get(key) or "") == value:
                return entity_id
        return None

    def _country_targets(self, iso2: str, *, limit: int) -> list[str]:
        source_code = _country_code(iso2)
        country_code = _sovereign_country_code(source_code)
        priority_types = {"port", "airport", "firm", "legal_entity"}
        targets = [
            entity_id
            for entity_id, entity in sorted(self.entities.items())
            if entity.get("country") == country_code
            and entity.get("entity_type") in priority_types
            and (
                source_code == country_code
                or (entity.get("external_ids") or {}).get("sourceCountryCode") == source_code
                or (entity.get("external_ids") or {}).get("provinceCode") == source_code
            )
        ]
        return targets[:limit]


def _download_or_seed_sources(
    *,
    mode: str,
    cache_dir: Path,
    limits: BulkLimits,
) -> dict[str, CachedSourceFile]:
    endpoints = {
        "sec_edgar": "https://www.sec.gov/files/company_tickers.json",
        "gleif": f"https://api.gleif.org/api/v1/lei-records?page[size]={limits.gleif_legal_entities}",
        "world_bank_indicators": f"https://api.worldbank.org/v2/indicator?format=json&per_page={limits.world_bank_indicators}",
        "world_bank_countries": f"https://api.worldbank.org/v2/country?format=json&per_page={limits.world_bank_countries}",
        "ourairports": "https://davidmegginson.github.io/ourairports-data/airports.csv",
        "gdelt": f"https://api.gdeltproject.org/api/v2/doc/doc?query=supply%20chain%20risk&mode=ArtList&format=json&maxrecords={limits.gdelt_articles}",
        "ofac": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.json",
        "nga_world_port_index": "https://msi.nga.mil/Publications/WPI",
        "usgs_earthquakes": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson",
    }
    files: dict[str, CachedSourceFile] = {}
    for source_id, url in endpoints.items():
        path = cache_dir / f"{source_id}.raw"
        if mode == "cache":
            if path.exists() and path.stat().st_size > 0:
                files[source_id] = _cached_file(source_id, url, path, "ok", "reused cached file")
            else:
                payload = _fixture_payload(source_id)
                path.write_bytes(payload)
                files[source_id] = _cached_file(source_id, url, path, "partial", "seeded fixture because cache file was missing")
            continue
        if mode == "fixture":
            payload = _fixture_payload(source_id)
            path.write_bytes(payload)
            files[source_id] = _cached_file(source_id, url, path, "ok", "fixture payload")
            continue
        try:
            req = Request(
                url,
                headers={
                    "User-Agent": DEFAULT_USER_AGENT,
                    "Accept": "application/json,text/csv,*/*",
                },
            )
            with urlopen(req, timeout=30) as response:
                payload = response.read()
            if source_id != "ourairports" and not _payload_looks_json(payload):
                raise ValueError("downloaded payload was not JSON")
            path.write_bytes(payload)
            files[source_id] = _cached_file(source_id, url, path, "ok", "downloaded")
        except (OSError, URLError, TimeoutError, ValueError) as exc:
            if not isinstance(exc, ValueError) and path.exists() and path.stat().st_size > 0:
                files[source_id] = _cached_file(source_id, url, path, "ok", f"reused cached file after {type(exc).__name__}")
            else:
                payload = _fixture_payload(source_id)
                path.write_bytes(payload)
                files[source_id] = _cached_file(source_id, url, path, "partial", f"seeded fixture after {type(exc).__name__}: {exc}")
    return files


def _payload_looks_json(payload: bytes) -> bool:
    stripped = payload.lstrip()
    return stripped.startswith(b"{") or stripped.startswith(b"[")


def _cached_file(source_id: str, url: str, path: Path, status: str, message: str) -> CachedSourceFile:
    payload = path.read_bytes()
    return CachedSourceFile(
        source_id=_normalize_source_id(source_id),
        url=url,
        path=path,
        checksum=sha256(payload).hexdigest(),
        status=status,
        message=message,
        byte_count=len(payload),
    )


def _normalize_source_id(source_id: str) -> str:
    return "world_bank" if source_id.startswith("world_bank") else source_id


def _load_base_catalog() -> dict[str, Any]:
    with default_catalog_path().open("r", encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle)
    if not isinstance(catalog, dict):
        raise ValueError("public real catalog must be a mapping")
    return catalog


def _load_json(path: Path, fixture_source_id: str | None = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        if fixture_source_id is None:
            return {}
        return json.loads(_fixture_payload(fixture_source_id).decode("utf-8"))


def _load_sec_company_tickers(source_files: dict[str, CachedSourceFile], limit: int) -> list[dict[str, Any]]:
    path = source_files["sec_edgar"].path
    payload = _load_json(path, "sec_edgar")
    if isinstance(payload, dict):
        values = list(payload.values())
    elif isinstance(payload, list):
        values = payload
    else:
        values = []
    return [row for row in values if isinstance(row, dict)][:limit]


def _load_gleif_lei_records(source_files: dict[str, CachedSourceFile], limit: int) -> list[dict[str, Any]]:
    path = source_files["gleif"].path
    payload = _load_json(path, "gleif")
    rows = []
    for item in payload.get("data", []) if isinstance(payload, dict) else []:
        attributes = item.get("attributes", {}) if isinstance(item, dict) else {}
        entity = attributes.get("entity", {}) if isinstance(attributes, dict) else {}
        legal_name = entity.get("legalName", {}) if isinstance(entity, dict) else {}
        legal_address = entity.get("legalAddress", {}) if isinstance(entity, dict) else {}
        rows.append(
            {
                "lei": attributes.get("lei") or item.get("id"),
                "name": legal_name.get("name"),
                "country": legal_address.get("country"),
            }
        )
    return rows[:limit]


def _load_world_bank_indicators(source_files: dict[str, CachedSourceFile], limit: int) -> list[dict[str, Any]]:
    payload = _load_json(source_files["world_bank_indicators"].path, "world_bank_indicators")
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list) else []
    return [row for row in rows if isinstance(row, dict)][:limit]


def _load_world_bank_countries(source_files: dict[str, CachedSourceFile], limit: int) -> list[dict[str, Any]]:
    payload = _load_json(source_files["world_bank_countries"].path, "world_bank_countries")
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list) else []
    return [
        {
            "id": row.get("id"),
            "iso2": row.get("iso2Code") or row.get("id"),
            "name": row.get("name"),
        }
        for row in rows
        if isinstance(row, dict) and _is_world_bank_country_row(row)
    ][:limit]


def _load_ourairports_airports(source_files: dict[str, CachedSourceFile], limit: int) -> list[dict[str, Any]]:
    text = source_files["ourairports"].path.read_text(encoding="utf-8", errors="replace")
    rows = list(csv.DictReader(text.splitlines()))
    major = [row for row in rows if row.get("type") in {"large_airport", "medium_airport"}]
    return major[:limit]


def _load_gdelt_articles(source_files: dict[str, CachedSourceFile], limit: int) -> list[dict[str, Any]]:
    payload = _load_json(source_files["gdelt"].path, "gdelt")
    if isinstance(payload, dict):
        rows = payload.get("articles") or payload.get("results") or []
    elif isinstance(payload, list):
        rows = payload
    else:
        rows = []
    return [row for row in rows if isinstance(row, dict)][:limit]


def _load_ofac_entries(source_files: dict[str, CachedSourceFile], limit: int) -> list[dict[str, Any]]:
    payload = _load_json(source_files["ofac"].path, "ofac")
    if isinstance(payload, dict):
        rows = payload.get("sdnList", {}).get("sdnEntry", []) if isinstance(payload.get("sdnList"), dict) else []
        rows = rows or payload.get("entries") or payload.get("data") or []
    elif isinstance(payload, list):
        rows = payload
    else:
        rows = []
    return [row for row in rows if isinstance(row, dict)][:limit]


def _load_usgs_earthquakes(source_files: dict[str, CachedSourceFile], limit: int) -> list[dict[str, Any]]:
    payload = _load_json(source_files["usgs_earthquakes"].path, "usgs_earthquakes")
    features = payload.get("features", []) if isinstance(payload, dict) else []
    rows: list[dict[str, Any]] = []
    for feature in features:
        if not isinstance(feature, dict):
            continue
        properties = feature.get("properties", {}) if isinstance(feature.get("properties"), dict) else {}
        geometry = feature.get("geometry", {}) if isinstance(feature.get("geometry"), dict) else {}
        coordinates = geometry.get("coordinates") if isinstance(geometry, dict) else None
        longitude = latitude = depth_km = ""
        if isinstance(coordinates, list) and len(coordinates) >= 2:
            longitude = coordinates[0]
            latitude = coordinates[1]
            depth_km = coordinates[2] if len(coordinates) > 2 else ""
        rows.append(
            {
                "id": feature.get("id"),
                "mag": properties.get("mag"),
                "place": properties.get("place"),
                "time": properties.get("time"),
                "updated": properties.get("updated"),
                "url": properties.get("url"),
                "alert": properties.get("alert"),
                "sig": properties.get("sig"),
                "longitude": longitude,
                "latitude": latitude,
                "depth_km": depth_km,
            }
        )
    return rows[:limit]


def _fixture_payload(source_id: str) -> bytes:
    if source_id == "sec_edgar":
        return json.dumps(
            {
                str(index): {"cik_str": cik, "ticker": ticker, "title": name}
                for index, (cik, ticker, name) in enumerate(_SEC_FIXTURE_COMPANIES)
            },
            sort_keys=True,
        ).encode("utf-8")
    if source_id == "gleif":
        return json.dumps({"data": _GLEIF_FIXTURE_RECORDS}, sort_keys=True).encode("utf-8")
    if source_id == "world_bank_indicators":
        return json.dumps([{"page": 1}, _WORLD_BANK_FIXTURE_INDICATORS], sort_keys=True).encode("utf-8")
    if source_id == "world_bank_countries":
        return json.dumps([{"page": 1}, _WORLD_BANK_FIXTURE_COUNTRIES], sort_keys=True).encode("utf-8")
    if source_id == "ourairports":
        columns = ["ident", "type", "name", "iso_country", "iata_code", "latitude_deg", "longitude_deg"]
        rows = [",".join(f'"{column}"' for column in columns)]
        for row in _OURAIRPORTS_FIXTURE_AIRPORTS:
            rows.append(",".join(f'"{str(row.get(column, ""))}"' for column in columns))
        return "\n".join(rows).encode("utf-8")
    if source_id == "gdelt":
        return json.dumps({"articles": _GDELT_FIXTURE_ARTICLES}, sort_keys=True).encode("utf-8")
    if source_id == "ofac":
        return json.dumps({"sdnList": {"sdnEntry": _OFAC_FIXTURE_ENTRIES}}, sort_keys=True).encode("utf-8")
    if source_id == "nga_world_port_index":
        return json.dumps(
            {"ports": [{"name": name, "country": country} for name, country in _WPI_PRIORITY_PORTS]},
            sort_keys=True,
        ).encode("utf-8")
    if source_id == "usgs_earthquakes":
        return json.dumps(
            {
                "type": "FeatureCollection",
                "metadata": {"title": "USGS M4.5+ earthquakes fixture", "count": len(_USGS_FIXTURE_EARTHQUAKES)},
                "features": [
                    {
                        "type": "Feature",
                        "id": event_id,
                        "properties": {
                            "mag": mag,
                            "place": place,
                            "time": 1777500000000 + index * 3600000,
                            "updated": 1777500000000 + index * 3600000,
                            "url": "https://earthquake.usgs.gov/earthquakes/eventpage/" + event_id,
                            "alert": alert,
                            "sig": int(mag * 100),
                        },
                        "geometry": {"type": "Point", "coordinates": [lon, lat, depth]},
                    }
                    for index, (event_id, mag, place, alert, lon, lat, depth) in enumerate(_USGS_FIXTURE_EARTHQUAKES)
                ],
            },
            sort_keys=True,
        ).encode("utf-8")
    return b"{}"


def _country_code(value: Any) -> str | None:
    text = str(value or "").strip().upper()
    if len(text) == 2 and text != "XX":
        return text
    return None


def _sovereign_country_code(source_country_code: str | None) -> str | None:
    if source_country_code == "TW":
        return "CN"
    return source_country_code


def _source_code_for_geo_id(geo_id: str) -> str:
    if geo_id == "province_cn_tw":
        return "TW"
    if geo_id.startswith("country_"):
        return geo_id.replace("country_", "", 1).upper()
    return geo_id.upper()


def _geo_metadata(canonical_id: str, entity_type: str, source_country_code: Any) -> dict[str, str | None]:
    source_code = _country_code(source_country_code)
    country_code = _sovereign_country_code(source_code)
    if not country_code:
        return {
            "geoId": None,
            "geoLevel": None,
            "countryCode": None,
            "provinceCode": None,
            "parentGeoId": None,
            "sourceCountryCode": None,
        }
    if source_code == "TW":
        return {
            "geoId": "province_cn_tw",
            "geoLevel": "province" if canonical_id == "province_cn_tw" else "province_context",
            "countryCode": "CN",
            "provinceCode": "TW",
            "parentGeoId": "country_cn",
            "sourceCountryCode": "TW",
        }
    return {
        "geoId": canonical_id if entity_type == "country" else f"country_{country_code.lower()}",
        "geoLevel": "country" if entity_type == "country" else "country_context",
        "countryCode": country_code,
        "provinceCode": None,
        "parentGeoId": None,
        "sourceCountryCode": source_code,
    }


def _is_world_bank_country_row(row: dict[str, Any]) -> bool:
    iso2 = _country_code(row.get("iso2Code") or row.get("id"))
    if not iso2:
        return False
    region = row.get("region") if isinstance(row.get("region"), dict) else {}
    if str(region.get("id") or "").upper() == "NA":
        return False
    if str(region.get("value") or "").strip().lower() == "aggregates":
        return False
    code = str(row.get("id") or "").upper()
    return code not in _WORLD_BANK_AGGREGATE_CODES


def _country_from_usgs_place(place: str) -> str | None:
    normalized = place.lower()
    country_markers = {
        "taiwan": "TW",
        "japan": "JP",
        "philippines": "PH",
        "indonesia": "ID",
        "china": "CN",
        "south korea": "KR",
        "korea": "KR",
        "california": "US",
        "alaska": "US",
        "mexico": "MX",
        "chile": "CL",
        "peru": "PE",
        "new zealand": "NZ",
        "fiji": "FJ",
        "papua new guinea": "PG",
        "singapore": "SG",
        "netherlands": "NL",
    }
    for marker, iso2 in country_markers.items():
        if marker in normalized:
            return iso2
    return None


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _slug(value: str, *, max_length: int = 64) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    normalized = re.sub(r"_+", "_", normalized)
    return (normalized or "unknown")[:max_length].strip("_")


_COUNTRY_NAMES = {
    "US": "United States",
    "CN": "China",
    "JP": "Japan",
    "KR": "South Korea",
    "NL": "Netherlands",
    "DE": "Germany",
    "FR": "France",
    "GB": "United Kingdom",
    "SG": "Singapore",
    "HK": "Hong Kong",
    "AE": "United Arab Emirates",
    "IN": "India",
    "CA": "Canada",
    "MX": "Mexico",
    "BR": "Brazil",
    "AR": "Argentina",
    "AT": "Austria",
    "AU": "Australia",
    "BD": "Bangladesh",
    "CH": "Switzerland",
    "PH": "Philippines",
    "ID": "Indonesia",
    "CL": "Chile",
    "CO": "Colombia",
    "CZ": "Czechia",
    "DK": "Denmark",
    "EG": "Egypt",
    "ES": "Spain",
    "FI": "Finland",
    "GR": "Greece",
    "IE": "Ireland",
    "IL": "Israel",
    "IT": "Italy",
    "LU": "Luxembourg",
    "MA": "Morocco",
    "PE": "Peru",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SA": "Saudi Arabia",
    "SE": "Sweden",
    "TH": "Thailand",
    "TR": "Turkiye",
    "VN": "Vietnam",
    "ZA": "South Africa",
    "NZ": "New Zealand",
    "FJ": "Fiji",
    "PG": "Papua New Guinea",
    "BE": "Belgium",
    "MY": "Malaysia",
}

_TAIWAN_PROVINCE_DISPLAY_NAME = "中国台湾省"

_WORLD_BANK_AGGREGATE_CODES = {
    "ARB",
    "CEB",
    "CSS",
    "EAP",
    "EAR",
    "EAS",
    "ECA",
    "ECS",
    "EMU",
    "EUU",
    "FCS",
    "HIC",
    "HPC",
    "IBD",
    "IBT",
    "IDA",
    "IDB",
    "IDX",
    "LAC",
    "LCN",
    "LDC",
    "LIC",
    "LMC",
    "LMY",
    "LTE",
    "MEA",
    "MIC",
    "MNA",
    "NAC",
    "OED",
    "OSS",
    "PRE",
    "PSS",
    "PST",
    "SAS",
    "SSA",
    "SSF",
    "SST",
    "TEA",
    "TEC",
    "TLA",
    "TMN",
    "TSA",
    "TSS",
    "UMC",
    "WLD",
}


_SEC_FIXTURE_COMPANIES = [
    (1045810, "NVDA", "NVIDIA CORP"),
    (320193, "AAPL", "Apple Inc."),
    (789019, "MSFT", "MICROSOFT CORP"),
    (1018724, "AMZN", "AMAZON COM INC"),
    (1652044, "GOOGL", "Alphabet Inc."),
    (1318605, "TSLA", "Tesla, Inc."),
    (2488, "AMD", "ADVANCED MICRO DEVICES INC"),
    (50863, "INTC", "INTEL CORP"),
    (732712, "TSM", "TAIWAN SEMICONDUCTOR MANUFACTURING CO LTD"),
    (93751, "TXN", "TEXAS INSTRUMENTS INC"),
]


_GLEIF_FIXTURE_RECORDS = [
    {
        "id": lei,
        "attributes": {
            "lei": lei,
            "entity": {
                "legalName": {"name": name},
                "legalAddress": {"country": country},
            },
        },
    }
    for lei, name, country in [
        ("5493006MHB84DD0ZWV18", "ASML HOLDING N.V.", "NL"),
        ("5493001KJTIIGC8Y1R12", "SAMSUNG ELECTRONICS CO., LTD.", "KR"),
        ("529900T8BM49AURSDO55", "SIEMENS AKTIENGESELLSCHAFT", "DE"),
        ("HWUPKR0MPOU8FGXBT394", "TOYOTA MOTOR CORPORATION", "JP"),
        ("549300J1K12F2X1J1N49", "HON HAI PRECISION INDUSTRY CO., LTD.", "TW"),
    ]
]


_WORLD_BANK_FIXTURE_COUNTRIES = [
    {"id": iso2, "iso2Code": iso2, "name": name}
    for iso2, name in sorted(_COUNTRY_NAMES.items())
] + [
    {"id": "WLD", "iso2Code": "1W", "name": "World", "region": {"id": "NA", "value": "Aggregates"}},
    {"id": "EUU", "iso2Code": "EU", "name": "European Union", "region": {"id": "NA", "value": "Aggregates"}},
]


_WORLD_BANK_FIXTURE_INDICATORS = [
    {"id": code, "name": name, "sourceNote": "World Bank public indicator fixture."}
    for code, name in [
        ("NY.GDP.MKTP.CD", "GDP (current US$)"),
        ("NE.EXP.GNFS.CD", "Exports of goods and services (current US$)"),
        ("NE.IMP.GNFS.CD", "Imports of goods and services (current US$)"),
        ("TX.VAL.TECH.MF.ZS", "High-technology exports (% of manufactured exports)"),
        ("IS.SHP.GOOD.TU", "Container port traffic (TEU: 20 foot equivalent units)"),
        ("LP.LPI.OVRL.XQ", "Logistics performance index: Overall"),
    ]
]


_OURAIRPORTS_FIXTURE_AIRPORTS = [
    {"ident": ident, "type": "large_airport", "name": name, "iso_country": iso2, "iata_code": iata, "latitude_deg": lat, "longitude_deg": lon}
    for ident, name, iso2, iata, lat, lon in [
        ("KJFK", "John F Kennedy International Airport", "US", "JFK", "40.6398", "-73.7789"),
        ("KLAX", "Los Angeles International Airport", "US", "LAX", "33.9425", "-118.408"),
        ("RCTP", "Taiwan Taoyuan International Airport", "TW", "TPE", "25.0777", "121.233"),
        ("WSSS", "Singapore Changi Airport", "SG", "SIN", "1.35019", "103.994"),
        ("EHAM", "Amsterdam Airport Schiphol", "NL", "AMS", "52.3086", "4.76389"),
        ("RKSI", "Incheon International Airport", "KR", "ICN", "37.4691", "126.451"),
    ]
]


_GDELT_FIXTURE_ARTICLES = [
    {"title": "Supply chain risk and semiconductor logistics disruption", "url": "https://www.gdeltproject.org/", "domain": "gdeltproject.org", "sourceCountry": "US"},
    {"title": "Port congestion pressure rises around electronics trade lanes", "url": "https://www.gdeltproject.org/", "domain": "gdeltproject.org", "sourceCountry": "SG"},
    {"title": "Sanctions and export control debate affects advanced chips", "url": "https://www.gdeltproject.org/", "domain": "gdeltproject.org", "sourceCountry": "US"},
]


_OFAC_FIXTURE_ENTRIES = [
    {"uid": "ofac-001", "name": "Example SDN semiconductor procurement entity", "sdnType": "Entity", "country": "US"},
    {"uid": "ofac-002", "name": "Example export control logistics entity", "sdnType": "Entity", "country": "CN"},
]


_USGS_FIXTURE_EARTHQUAKES = [
    ("usgs-fixture-tw-001", 6.2, "28 km E of Hualien City, Taiwan", "orange", 121.9, 24.0, 18.0),
    ("usgs-fixture-jp-001", 5.7, "near the east coast of Honshu, Japan", "yellow", 142.1, 37.8, 31.0),
    ("usgs-fixture-ph-001", 5.5, "Mindanao, Philippines", "yellow", 126.5, 7.1, 45.0),
    ("usgs-fixture-id-001", 5.9, "Molucca Sea, Indonesia", "orange", 126.2, 1.8, 35.0),
    ("usgs-fixture-us-001", 4.8, "Central California", "green", -121.1, 36.7, 9.0),
]


_WPI_PRIORITY_PORTS = [
    ("Port of Shanghai", "CN"),
    ("Port of Singapore", "SG"),
    ("Port of Ningbo-Zhoushan", "CN"),
    ("Port of Shenzhen", "CN"),
    ("Port of Busan", "KR"),
    ("Port of Los Angeles", "US"),
    ("Port of Long Beach", "US"),
    ("Port of Rotterdam", "NL"),
    ("Port of Hamburg", "DE"),
    ("Port of Antwerp-Bruges", "BE"),
    ("Port of Kaohsiung", "TW"),
    ("Port of Yokohama", "JP"),
    ("Jebel Ali Port", "AE"),
    ("Port Klang", "MY"),
    ("Port of Santos", "BR"),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build promoted public-real bulk graph cache.")
    parser.add_argument("--mode", choices=["online", "cache", "fixture"], default="online")
    parser.add_argument("--cache-dir", type=Path, default=project_root() / DEFAULT_CACHE_DIR)
    parser.add_argument("--promoted-dir", type=Path, default=project_root() / DEFAULT_PROMOTED_DIR)
    parser.add_argument("--sec-limit", type=int, default=BulkLimits.sec_companies)
    parser.add_argument("--gleif-limit", type=int, default=BulkLimits.gleif_legal_entities)
    parser.add_argument("--world-bank-indicator-limit", type=int, default=BulkLimits.world_bank_indicators)
    parser.add_argument("--world-bank-country-limit", type=int, default=BulkLimits.world_bank_countries)
    parser.add_argument("--airport-limit", type=int, default=BulkLimits.ourairports_airports)
    parser.add_argument("--gdelt-limit", type=int, default=BulkLimits.gdelt_articles)
    parser.add_argument("--ofac-limit", type=int, default=BulkLimits.ofac_entries)
    parser.add_argument("--usgs-earthquake-limit", type=int, default=BulkLimits.usgs_earthquakes)
    args = parser.parse_args(argv)
    limits = BulkLimits(
        sec_companies=args.sec_limit,
        gleif_legal_entities=args.gleif_limit,
        world_bank_indicators=args.world_bank_indicator_limit,
        world_bank_countries=args.world_bank_country_limit,
        ourairports_airports=args.airport_limit,
        gdelt_articles=args.gdelt_limit,
        ofac_entries=args.ofac_limit,
        usgs_earthquakes=args.usgs_earthquake_limit,
    )
    manifest = write_promoted_catalog(
        mode=args.mode,
        cache_dir=args.cache_dir,
        promoted_dir=args.promoted_dir,
        limits=limits,
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
