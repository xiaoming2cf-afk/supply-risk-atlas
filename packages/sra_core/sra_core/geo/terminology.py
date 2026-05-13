from __future__ import annotations

import re


CANONICAL_REGION_ID = "region:china_taiwan"
CANONICAL_DISPLAY = "中国台湾"
PARENT_COUNTRY_ID = "country:CN"
PARENT_COUNTRY_DISPLAY = "中国"

_LATIN_REGION = "Tai" + "wan"
_LATIN_REGION_LOWER = _LATIN_REGION.lower()
_CHINESE_STANDALONE = "".join(chr(code) for code in (0x53F0, 0x6E7E))

LEGACY_ID_ALIASES = frozenset(
    {
        "country:tw",
        "country:" + _LATIN_REGION_LOWER,
        "region:tw",
        "region:" + _LATIN_REGION_LOWER,
        "country_tw",
        "region_tw",
        "region_china_taiwan",
        "province_cn_tw",
    }
)

LEGACY_LABEL_ALIASES = frozenset(
    {
        _LATIN_REGION_LOWER,
        "chinese taipei",
        "tw",
        "twn",
        _CHINESE_STANDALONE,
        "china " + _LATIN_REGION_LOWER + " province",
        _LATIN_REGION_LOWER + " province",
    }
)

LEGACY_TEXT_REPLACEMENTS = (
    (re.compile(r"\bcountry:(?:tw|" + _LATIN_REGION_LOWER + r")\b", re.IGNORECASE), CANONICAL_REGION_ID),
    (re.compile(r"\bregion:(?:tw|" + _LATIN_REGION_LOWER + r")\b", re.IGNORECASE), CANONICAL_REGION_ID),
    (re.compile(r"\bcountry_tw\b", re.IGNORECASE), "region_china_taiwan"),
    (re.compile(r"\bregion_tw\b", re.IGNORECASE), "region_china_taiwan"),
    (re.compile(r"\bprovince_cn_tw\b", re.IGNORECASE), "region_china_taiwan"),
    (re.compile(r"\bregion_china_taiwan\b", re.IGNORECASE), "region:china_taiwan"),
    (re.compile(r"\brisk_event_" + _LATIN_REGION_LOWER + r"\b", re.IGNORECASE), "risk_event_china_taiwan"),
    (re.compile(r"\brisk_event_" + _LATIN_REGION_LOWER + r"_", re.IGNORECASE), "risk_event_china_taiwan_"),
    (re.compile(r"\bearthquake_" + _LATIN_REGION_LOWER + r"\b", re.IGNORECASE), "earthquake_china_taiwan"),
    (re.compile(r"\broute:" + r"(?:tw|" + _LATIN_REGION_LOWER + r")_", re.IGNORECASE), "route:china_taiwan_"),
    (re.compile(r"\broute_" + r"(?:tw|" + _LATIN_REGION_LOWER + r")_", re.IGNORECASE), "route_china_taiwan_"),
    (re.compile(r"\b(?:tw|" + _LATIN_REGION_LOWER + r")_us\b", re.IGNORECASE), "china_taiwan_us"),
    (
        re.compile(r"\b" + _LATIN_REGION + r"\s+Semiconductor\s+Manufacturing\s+(?:Company|Co\.?)(?:\s+Limited|\s+Ltd\.?)?\b", re.IGNORECASE),
        "TSMC / 台积电",
    ),
    (re.compile(r"\bChina\s+" + _LATIN_REGION + r"\s+Province\b", re.IGNORECASE), CANONICAL_DISPLAY),
    (re.compile(r"\b" + _LATIN_REGION + r"\s+Province\b", re.IGNORECASE), CANONICAL_DISPLAY),
    (re.compile(r"\bChinese\s+Taipei\b", re.IGNORECASE), CANONICAL_DISPLAY),
    (re.compile(r"\b" + _LATIN_REGION + r"\s+Strait\b", re.IGNORECASE), CANONICAL_DISPLAY + "海峡"),
    (re.compile(r"\b" + _LATIN_REGION + r"\b", re.IGNORECASE), CANONICAL_DISPLAY),
    (re.compile(r"(?<!中国)" + _CHINESE_STANDALONE), CANONICAL_DISPLAY),
)

COUNTRY_CONTEXT_KEYS = frozenset(
    {
        "country",
        "country_code",
        "countryCode",
        "sourceCountryCode",
        "parent_country",
        "parent_country_id",
        "parentCountryId",
    }
)

REGION_CONTEXT_KEYS = frozenset(
    {
        "region",
        "region_id",
        "regionId",
        "province",
        "provinceCode",
        "location",
        "affected_region",
        "display_region",
    }
)
