from __future__ import annotations

import importlib.util
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
