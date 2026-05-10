from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypeAlias

from pydantic import Field

from sra_core.contracts.data import PayloadFormat, RawRecord, SourceManifest
from sra_core.contracts.domain import StrictModel
from sra_core.ingestion.registry import load_source_registry

ConnectorOutput: TypeAlias = tuple[list[RawRecord], SourceManifest]


class ConnectorBatch(StrictModel):
    records: list[RawRecord] = Field(default_factory=list)
    manifest: SourceManifest


@dataclass(frozen=True)
class PublicSourceConnector:
    source_id: str

    def ingest_sample(
        self,
        *,
        source_record_id: str,
        event_time: datetime,
        published_time: datetime | None = None,
        observed_time: datetime | None = None,
        ingest_time: datetime,
        raw_payload: dict[str, Any],
        payload_format: PayloadFormat = "json",
    ) -> ConnectorBatch:
        source = self._source_entry()
        record = RawRecord.from_payload(
            source_id=self.source_id,
            source_record_id=source_record_id,
            event_time=event_time,
            published_time=published_time,
            observed_time=observed_time,
            ingest_time=ingest_time,
            payload_format=payload_format,
            raw_payload=raw_payload,
            license_name=source.license.name,
            allowed_use=source.license.allowed_use,
            attribution=source.publisher,
        )
        manifest = SourceManifest.from_records(
            source_id=self.source_id,
            records=[record],
            checked_at=ingest_time,
            freshness_sla_hours=source.freshness_sla_hours,
        )
        return ConnectorBatch(records=[record], manifest=manifest)

    def _source_entry(self):
        registry = load_source_registry()
        matches = [source for source in registry.sources if source.source_id == self.source_id]
        if not matches:
            raise ValueError(f"source_id is not configured: {self.source_id}")
        return matches[0]


class SecEdgarConnector(PublicSourceConnector):
    def __init__(self) -> None:
        super().__init__("sec_edgar")


class GleifConnector(PublicSourceConnector):
    def __init__(self) -> None:
        super().__init__("gleif")


class GdeltConnector(PublicSourceConnector):
    def __init__(self) -> None:
        super().__init__("gdelt")


class WorldBankConnector(PublicSourceConnector):
    def __init__(self) -> None:
        super().__init__("world_bank")


class OfacConnector(PublicSourceConnector):
    def __init__(self) -> None:
        super().__init__("ofac")


class OurAirportsConnector(PublicSourceConnector):
    def __init__(self) -> None:
        super().__init__("ourairports")


class NgaWorldPortIndexConnector(PublicSourceConnector):
    def __init__(self) -> None:
        super().__init__("nga_world_port_index")


class UsgsEarthquakesConnector(PublicSourceConnector):
    def __init__(self) -> None:
        super().__init__("usgs_earthquakes")


def connector_for_source(source_id: str) -> PublicSourceConnector:
    connectors: dict[str, type[PublicSourceConnector]] = {
        "sec_edgar": SecEdgarConnector,
        "gleif": GleifConnector,
        "gdelt": GdeltConnector,
        "world_bank": WorldBankConnector,
        "ofac": OfacConnector,
        "ourairports": OurAirportsConnector,
        "nga_world_port_index": NgaWorldPortIndexConnector,
        "usgs_earthquakes": UsgsEarthquakesConnector,
    }
    try:
        return connectors[source_id]()
    except KeyError as exc:
        raise ValueError(f"unsupported public source connector: {source_id}") from exc
