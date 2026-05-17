from __future__ import annotations

import importlib.util
from email.message import Message
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "check-deployed-version.py"


def _load_checker_module():
    spec = importlib.util.spec_from_file_location("check_deployed_version", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_commit_match_accepts_short_expected_sha_against_full_observed_sha() -> None:
    checker = _load_checker_module()

    assert checker.commits_match(
        "8942950",
        "8942950abcdef1234567890abcdef1234567890",
    )


def test_commit_match_accepts_full_expected_sha_against_short_observed_sha() -> None:
    checker = _load_checker_module()

    assert checker.commits_match(
        "9674e6005021597182b05aac4700247b89f81464",
        "9674e60",
    )


def test_commit_match_rejects_unknown_or_unrelated_values() -> None:
    checker = _load_checker_module()

    assert not checker.commits_match("unknown", "9674e60")
    assert not checker.commits_match("1234567", "9674e6005021597182b05aac4700247b89f81464")
    assert not checker.commits_match("abcdef1", "abcdef1notasha")
    assert not checker.commits_match("9674e6", "9674e6005021597182b05aac4700247b89f81464")


def test_web_commit_visible_rejects_seven_character_html_match() -> None:
    checker = _load_checker_module()

    assert not checker.web_commit_visible(
        '<html><body>build hint 9674e60</body></html>',
        "9674e60",
    )


def test_web_commit_visible_accepts_bounded_twelve_character_prefix() -> None:
    checker = _load_checker_module()

    assert checker.web_commit_visible(
        '<html><meta name="web-commit" content="9674e6005021"></html>',
        "9674e6005021597182b05aac4700247b89f81464",
    )


def test_web_commit_visible_rejects_embedded_prefix_inside_longer_hex_token() -> None:
    checker = _load_checker_module()

    assert not checker.web_commit_visible(
        '<html><body>9674e6005021aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</body></html>',
        "9674e6005021597182b05aac4700247b89f81464",
    )


def test_deployment_status_requires_api_web_proxy_and_html_match() -> None:
    checker = _load_checker_module()

    status, warnings = checker.deployment_status(
        expected_commit="9674e6005021597182b05aac4700247b89f81464",
        api_result={"status": "ok"},
        api_commit="9674e60",
        web_html_result={"status": "verified"},
        web_build_result={"status": "ok", "cache_control": "no-store, max-age=0"},
        web_build_commit="9674e6005021597182b05aac4700247b89f81464",
        web_proxy_result={"status": "ok"},
        web_proxy_commit="9674e6005021597182b05aac4700247b89f81464",
    )

    assert status == "deployed_verified"
    assert warnings == []


def test_deployment_status_reports_stale_mismatch_without_success() -> None:
    checker = _load_checker_module()

    status, warnings = checker.deployment_status(
        expected_commit="9674e6005021597182b05aac4700247b89f81464",
        api_result={"status": "ok"},
        api_commit="8942950",
        web_html_result={"status": "commit_not_visible"},
        web_build_result={"status": "ok", "cache_control": "no-store, max-age=0"},
        web_build_commit="8942950",
        web_proxy_result={"status": "ok"},
        web_proxy_commit="8942950",
    )

    assert status == "deployed_stale_or_unverified"
    assert "api_commit_mismatch" in warnings
    assert "web_build_info_commit_mismatch" in warnings
    assert "web_proxy_commit_mismatch" in warnings
    assert "web_html_commit_not_visible" in warnings


def test_deployment_status_honors_api_reported_stale_state() -> None:
    checker = _load_checker_module()

    status, warnings = checker.deployment_status(
        expected_commit="9674e6005021597182b05aac4700247b89f81464",
        api_result={"status": "ok", "deployment_stale_or_unverified": True},
        api_commit="9674e6005021597182b05aac4700247b89f81464",
        web_html_result={"status": "verified"},
        web_build_result={"status": "ok", "cache_control": "no-store, max-age=0"},
        web_build_commit="9674e6005021597182b05aac4700247b89f81464",
        web_proxy_result={"status": "ok"},
        web_proxy_commit="9674e6005021597182b05aac4700247b89f81464",
    )

    assert status == "deployed_stale_or_unverified"
    assert warnings == ["api_reported_deployment_stale_or_unverified"]


def test_deployment_status_honors_api_reported_unavailable_state() -> None:
    checker = _load_checker_module()

    status, warnings = checker.deployment_status(
        expected_commit="9674e6005021597182b05aac4700247b89f81464",
        api_result={"status": "ok", "deployment_unavailable": True},
        api_commit="9674e6005021597182b05aac4700247b89f81464",
        web_html_result={"status": "verified"},
        web_build_result={"status": "ok", "cache_control": "no-store, max-age=0"},
        web_build_commit="9674e6005021597182b05aac4700247b89f81464",
        web_proxy_result={"status": "ok"},
        web_proxy_commit="9674e6005021597182b05aac4700247b89f81464",
    )

    assert status == "deployed_stale_or_unverified"
    assert warnings == ["api_reported_deployment_unavailable"]


def test_deployment_status_reports_unavailable_when_all_public_probes_fail() -> None:
    checker = _load_checker_module()

    status, warnings = checker.deployment_status(
        expected_commit="9674e6005021597182b05aac4700247b89f81464",
        api_result={"status": "failed"},
        api_commit="unknown",
        web_html_result={"status": "failed"},
        web_build_result={"status": "failed"},
        web_build_commit="unknown",
        web_proxy_result={"status": "failed"},
        web_proxy_commit="unknown",
    )

    assert status == "deployed_unavailable"
    assert warnings == [
        "api_unavailable",
        "web_unavailable",
        "web_build_info_unavailable",
        "web_proxy_unavailable",
    ]


def test_deployment_status_reports_probe_error_for_unknown_expected_commit() -> None:
    checker = _load_checker_module()

    status, warnings = checker.deployment_status(
        expected_commit="unknown",
        api_result={"status": "ok"},
        api_commit="9674e60",
        web_html_result={"status": "verified"},
        web_build_result={"status": "ok", "cache_control": "no-store, max-age=0"},
        web_build_commit="9674e60",
        web_proxy_result={"status": "ok"},
        web_proxy_commit="9674e60",
    )

    assert status == "probe_error"
    assert warnings == ["expected_commit_unknown"]


def test_retry_probe_records_attempt_count_and_stops_on_success() -> None:
    checker = _load_checker_module()
    responses = iter(
        [
            {"status": "failed", "latency_class": "failed"},
            {"status": "ok", "latency_class": "normal"},
        ]
    )

    result = checker.retry_probe(lambda: next(responses), attempts=3)

    assert result["status"] == "ok"
    assert result["attempts"] == 2


def test_retry_probe_reports_exhausted_attempt_count() -> None:
    checker = _load_checker_module()

    result = checker.retry_probe(
        lambda: {"status": "failed", "latency_class": "failed"},
        attempts=3,
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 3


def test_retry_probe_sanitizes_factory_exceptions() -> None:
    checker = _load_checker_module()

    def failing_probe() -> dict[str, str]:
        raise RuntimeError("private transport details")

    result = checker.retry_probe(failing_probe, attempts=1)

    assert result == {
        "status": "failed",
        "error": "RuntimeError",
        "latency_class": "failed",
        "attempts": 1,
    }


def test_fetch_web_build_info_extracts_sanitized_metadata(monkeypatch) -> None:
    checker = _load_checker_module()

    class FakeResponse:
        headers = Message()
        headers["Cache-Control"] = "no-store, max-age=0"

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, _limit: int) -> bytes:
            return (
                b'{"status":"success","data":{"web_commit":"9674e6005021597182b05aac4700247b89f81464",'
                b'"deployment_readiness_state":"web_build_metadata"}}'
            )

    monkeypatch.setattr(checker, "urlopen", lambda *_args, **_kwargs: FakeResponse())

    result = checker.fetch_web_build_info("https://example.test", 1)

    assert result["status"] == "ok"
    assert result["web_commit"] == "9674e6005021597182b05aac4700247b89f81464"
    assert result["deployment_readiness_state"] == "web_build_metadata"
    assert result["cache_control"] == "no-store, max-age=0"


def test_fetch_web_build_info_sanitizes_transport_failure(monkeypatch) -> None:
    checker = _load_checker_module()

    def failing_urlopen(*_args, **_kwargs):
        raise OSError("private transport details")

    monkeypatch.setattr(checker, "urlopen", failing_urlopen)

    result = checker.fetch_web_build_info("https://example.test", 1)

    assert result == {
        "status": "failed",
        "error": "OSError",
        "latency_class": "failed",
    }


def test_deployment_status_requires_web_build_info_no_store() -> None:
    checker = _load_checker_module()

    status, warnings = checker.deployment_status(
        expected_commit="9674e6005021597182b05aac4700247b89f81464",
        api_result={"status": "ok"},
        api_commit="9674e6005021597182b05aac4700247b89f81464",
        web_html_result={"status": "verified"},
        web_build_result={"status": "ok", "cache_control": "public, max-age=3600"},
        web_build_commit="9674e6005021597182b05aac4700247b89f81464",
        web_proxy_result={"status": "ok"},
        web_proxy_commit="9674e6005021597182b05aac4700247b89f81464",
    )

    assert status == "deployed_stale_or_unverified"
    assert warnings == ["web_build_info_cache_control_missing"]
