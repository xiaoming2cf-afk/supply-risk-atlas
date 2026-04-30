from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from random import Random
from typing import Any

from sra_core.contracts.domain import CanonicalEntity, EdgeEvent, EventFact


@dataclass(frozen=True)
class SyntheticDataset:
    seed: int
    entities: list[CanonicalEntity]
    edge_events: list[EdgeEvent]
    event_facts: list[EventFact]


def _id(prefix: str, value: str) -> str:
    digest = sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _dt(days: int) -> datetime:
    return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=days)


def generate_synthetic_dataset(seed: int = 42) -> SyntheticDataset:
    rng = Random(seed)
    countries = [
        ("country_us", "United States", "US"),
        ("country_jp", "Japan", "JP"),
        ("country_tw", "Taiwan", "TW"),
        ("country_de", "Germany", "DE"),
    ]
    firms = [
        ("firm_anchor", "Atlas Motors", "US", "Automotive"),
        ("firm_chip", "Formosa Silicon", "TW", "Semiconductors"),
        ("firm_sensor", "Kyoto Sensors", "JP", "Electronics"),
        ("firm_logistics", "NorthStar Logistics", "US", "Logistics"),
        ("firm_chem", "RhineChem", "DE", "Chemicals"),
    ]
    ports = [
        ("port_la", "Port of Los Angeles", "US"),
        ("port_kaohsiung", "Port of Kaohsiung", "TW"),
        ("port_yokohama", "Port of Yokohama", "JP"),
    ]
    products = [
        ("product_ev", "EV Platform", "EV-PLATFORM"),
        ("product_chip", "Automotive MCU", "HS854231"),
        ("product_sensor", "Lidar Sensor", "HS903149"),
        ("material_lithium", "Lithium Carbonate", "HS283691"),
    ]

    entities: list[CanonicalEntity] = []
    for canonical_id, name, iso2 in countries:
        entities.append(
            CanonicalEntity(
                canonical_id=canonical_id,
                entity_type="country",
                display_name=name,
                country=iso2,
                confidence=1.0,
                external_ids={"iso2": iso2},
            )
        )
    for canonical_id, name, country, industry in firms:
        entities.append(
            CanonicalEntity(
                canonical_id=canonical_id,
                entity_type="firm",
                display_name=name,
                country=country,
                industry=industry,
                external_ids={"synthetic_ticker": canonical_id.upper()},
                confidence=0.98,
            )
        )
    for canonical_id, name, country in ports:
        entities.append(
            CanonicalEntity(
                canonical_id=canonical_id,
                entity_type="port",
                display_name=name,
                country=country,
                confidence=0.99,
            )
        )
    for canonical_id, name, code in products:
        entity_type = "raw_material" if canonical_id.startswith("material") else "product"
        entities.append(
            CanonicalEntity(
                canonical_id=canonical_id,
                entity_type=entity_type,
                display_name=name,
                external_ids={"product_code": code},
                confidence=0.97,
            )
        )
    entities.extend(
        [
            CanonicalEntity(
                canonical_id="risk_event_typhoon",
                entity_type="risk_event",
                display_name="Typhoon disruption near Taiwan Strait",
                country="TW",
                confidence=0.92,
            ),
            CanonicalEntity(
                canonical_id="policy_export_control",
                entity_type="policy",
                display_name="Advanced chip export control",
                country="US",
                confidence=0.94,
            ),
        ]
    )

    edge_specs: list[tuple[str, str, str, str, int, float, dict[str, Any]]] = [
        ("firm_chip", "firm_anchor", "supplies_to", "create", 1, 0.91, {"trade_value": 120.0, "weight": 0.86}),
        ("firm_sensor", "firm_anchor", "supplies_to", "create", 2, 0.88, {"trade_value": 50.0, "weight": 0.61}),
        ("firm_chem", "firm_chip", "supplies_to", "create", 3, 0.84, {"trade_value": 35.0, "weight": 0.44}),
        ("firm_anchor", "product_ev", "produces", "create", 3, 0.90, {"volume": 2000, "weight": 0.75}),
        ("firm_chip", "product_chip", "produces", "create", 3, 0.92, {"volume": 9000, "weight": 0.82}),
        ("firm_sensor", "product_sensor", "produces", "create", 4, 0.87, {"volume": 3200, "weight": 0.68}),
        ("firm_chip", "port_kaohsiung", "ships_through", "create", 4, 0.86, {"volume": 280.0, "delay": 1.0, "weight": 0.58}),
        ("firm_sensor", "port_yokohama", "ships_through", "create", 5, 0.83, {"volume": 140.0, "delay": 0.5, "weight": 0.49}),
        ("port_kaohsiung", "port_la", "route_connects", "create", 5, 0.93, {"distance": 10900, "weight": 0.72}),
        ("port_yokohama", "port_la", "route_connects", "create", 6, 0.90, {"distance": 8800, "weight": 0.65}),
        ("risk_event_typhoon", "firm_chip", "event_affects", "create", 20, 0.81, {"severity": 0.72, "weight": 0.77}),
        ("policy_export_control", "product_chip", "policy_targets", "create", 24, 0.89, {"severity": 0.67, "weight": 0.64}),
        ("firm_chip", "firm_anchor", "supplies_to", "update", 26, 0.90, {"trade_value": 85.0, "weight": 0.70, "risk_score": 0.66}),
        ("firm_sensor", "firm_anchor", "supplies_to", "remove", 65, 0.86, {"reason": "synthetic disruption", "weight": 0.0}),
    ]

    edge_events: list[EdgeEvent] = []
    for idx, (source_id, target_id, edge_type, event_type, day, confidence, attributes) in enumerate(edge_specs):
        event_time = _dt(day)
        ingest_time = event_time + timedelta(hours=rng.choice([2, 8, 24]))
        edge_events.append(
            EdgeEvent(
                edge_event_id=_id("edge_event", f"{seed}:{idx}:{source_id}:{target_id}:{edge_type}:{event_type}:{day}"),
                source_id=source_id,
                target_id=target_id,
                edge_type=edge_type,
                event_type=event_type,  # type: ignore[arg-type]
                event_time=event_time,
                ingest_time=ingest_time,
                attributes=attributes,
                confidence=confidence,
                source="synthetic_supply_risk_seed",
            )
        )

    event_facts = [
        EventFact(
            event_id="event_typhoon_tw_2026_01",
            event_type="weather_event",
            event_time=_dt(20),
            ingest_time=_dt(20) + timedelta(hours=4),
            location="TW",
            severity=0.72,
            source_id="synthetic_weather",
            raw_id=None,
            attributes={"affected_region": "Taiwan Strait"},
            confidence=0.91,
        ),
        EventFact(
            event_id="event_export_control_2026_01",
            event_type="export_control",
            event_time=_dt(24),
            ingest_time=_dt(24) + timedelta(hours=6),
            location="US",
            severity=0.67,
            source_id="synthetic_policy",
            raw_id=None,
            attributes={"target": "Automotive MCU"},
            confidence=0.89,
        ),
    ]
    return SyntheticDataset(seed=seed, entities=entities, edge_events=edge_events, event_facts=event_facts)
