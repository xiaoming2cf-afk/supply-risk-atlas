from __future__ import annotations

import json
import urllib.request

import pytest

from sra_core.ingestion import bulk_public
from sra_core.ingestion.bulk_public import BulkLimits, build_bulk_catalog, write_promoted_catalog


class ChunkedResponse:
    def __init__(self, chunks: list[bytes], headers: dict[str, str] | None = None) -> None:
        self.chunks = list(chunks)
        self.headers = headers or {}
        self.read_sizes: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.read_sizes.append(size)
        return self.chunks.pop(0) if self.chunks else b""


def _small_limits() -> BulkLimits:
    return BulkLimits(
        sec_companies=2,
        gleif_legal_entities=2,
        world_bank_indicators=2,
        world_bank_countries=4,
        ourairports_airports=2,
        gdelt_articles=2,
        ofac_entries=1,
        usgs_earthquakes=1,
    )


def test_bulk_public_fixture_builds_data_governance_nodes(tmp_path) -> None:
    catalog, manifest = build_bulk_catalog(
        mode="fixture",
        cache_dir=tmp_path / "cache",
        limits=BulkLimits(
            sec_companies=20,
            gleif_legal_entities=10,
            world_bank_indicators=20,
            world_bank_countries=20,
            ourairports_airports=20,
            gdelt_articles=10,
            ofac_entries=10,
            usgs_earthquakes=5,
        ),
    )

    entity_types = {entity["entity_type"] for entity in catalog["entities"]}
    edge_types = {edge["edge_type"] for edge in catalog["edges"]}

    assert manifest["raw_data_in_git"] is False
    assert manifest["mode"] == "fixture"
    assert manifest["requested_mode"] == "fixture"
    assert manifest["effective_mode"] == "fixture"
    assert manifest["live_fetch_requested"] is False
    assert manifest["live_fetch_effective"] is False
    assert manifest["source_status"] == "fresh"
    assert len(catalog["entities"]) >= 240
    assert len(catalog["edges"]) >= 340
    assert {
        "schema_field",
        "license_policy",
        "coverage_area",
        "source_release",
        "observation_series",
        "legal_entity",
        "risk_event",
    } <= entity_types
    assert {
        "dataset_has_field",
        "licensed_under",
        "released_as",
        "observed_for",
        "dataset_observes",
        "event_affects",
        "risk_transmits_to",
    } <= edge_types
    assert any(entity["source_id"] == "usgs_earthquakes" for entity in catalog["entities"])


def test_bulk_public_default_build_is_offline_safe(monkeypatch, tmp_path) -> None:
    calls: list[object] = []

    def fail_urlopen(*args, **kwargs):  # pragma: no cover - should never be reached
        calls.append((args, kwargs))
        raise AssertionError("network call during default bulk catalog build")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)

    _catalog, manifest = build_bulk_catalog(
        cache_dir=tmp_path / "cache",
        limits=_small_limits(),
    )

    assert calls == []
    assert manifest["mode"] == "cache"
    assert manifest["requested_mode"] == "cache"
    assert manifest["effective_mode"] == "cache"
    assert manifest["live_fetch_requested"] is False
    assert manifest["live_fetch_effective"] is False


def test_bulk_public_online_without_allow_live_downgrades_without_network(monkeypatch, tmp_path) -> None:
    calls: list[object] = []

    def fail_urlopen(*args, **kwargs):  # pragma: no cover - should never be reached
        calls.append((args, kwargs))
        raise AssertionError("network call without explicit allow-live guard")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)

    _catalog, manifest = build_bulk_catalog(
        mode="online",
        cache_dir=tmp_path / "cache",
        limits=_small_limits(),
    )

    assert calls == []
    assert manifest["requested_mode"] == "online"
    assert manifest["effective_mode"] == "cache"
    assert manifest["mode"] == "cache"
    assert manifest["live_fetch_requested"] is True
    assert manifest["live_fetch_effective"] is False
    assert manifest["live_fetch_guard"] == "blocked_explicit_allow_live_fetch_required"
    assert "bulk_public_live_fetch_blocked_without_explicit_allow" in manifest["warnings"]


def test_bulk_public_cli_default_is_offline_safe(monkeypatch, tmp_path, capsys) -> None:
    calls: list[object] = []

    def fail_urlopen(*args, **kwargs):  # pragma: no cover - should never be reached
        calls.append((args, kwargs))
        raise AssertionError("network call during default bulk catalog CLI")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)

    exit_code = bulk_public.main(
        [
            "--cache-dir",
            str(tmp_path / "cache"),
            "--promoted-dir",
            str(tmp_path / "promoted"),
            "--sec-limit",
            "2",
            "--gleif-limit",
            "2",
            "--world-bank-indicator-limit",
            "2",
            "--world-bank-country-limit",
            "4",
            "--airport-limit",
            "2",
            "--gdelt-limit",
            "2",
            "--ofac-limit",
            "1",
            "--usgs-earthquake-limit",
            "1",
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert calls == []
    assert output["requested_mode"] == "cache"
    assert output["effective_mode"] == "cache"
    assert output["live_fetch_effective"] is False


def test_bulk_public_writer_creates_promoted_manifest(tmp_path) -> None:
    promoted_dir = tmp_path / "promoted" / "public_real" / "latest"

    manifest = write_promoted_catalog(
        mode="fixture",
        cache_dir=tmp_path / "cache",
        promoted_dir=promoted_dir,
        limits=BulkLimits(sec_companies=12),
    )

    catalog_path = promoted_dir / "catalog.json"
    manifest_path = promoted_dir / "manifest.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["catalog_path"] == str(catalog_path)
    assert manifest["manifest_path"] == str(manifest_path)
    assert written_manifest["schema_version"] == "promoted-public-real-v1"
    assert written_manifest["requested_mode"] == "fixture"
    assert written_manifest["effective_mode"] == "fixture"
    assert written_manifest["live_fetch_effective"] is False
    assert written_manifest["record_counts"]["entities"] == len(catalog["entities"])
    assert written_manifest["record_counts"]["edges"] == len(catalog["edges"])


def test_bulk_public_download_rejects_declared_oversize_payload() -> None:
    response = ChunkedResponse(
        [b"{}"],
        headers={"Content-Length": str(bulk_public.DEFAULT_MAX_DOWNLOAD_BYTES + 1)},
    )

    with pytest.raises(bulk_public.PayloadTooLargeError):
        bulk_public._read_limited_response(response, "gdelt")


def test_bulk_public_download_streams_with_byte_cap(monkeypatch) -> None:
    monkeypatch.setitem(bulk_public.MAX_DOWNLOAD_BYTES_BY_SOURCE, "gdelt", 5)
    response = ChunkedResponse([b"abc", b"def"])

    with pytest.raises(bulk_public.PayloadTooLargeError):
        bulk_public._read_limited_response(response, "gdelt")

    assert response.read_sizes
    assert all(size == bulk_public.DOWNLOAD_CHUNK_BYTES for size in response.read_sizes)
