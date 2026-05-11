from __future__ import annotations

import os


def security_headers() -> dict[str, str]:
    return {
        "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Cross-Origin-Opener-Policy": "same-origin",
    }


def cors_origins() -> list[str]:
    configured = os.getenv("SUPPLY_RISK_CORS_ORIGINS", "").strip()
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    if os.getenv("SUPPLY_RISK_ENV", "development").strip().lower() in {"prod", "production"}:
        return ["https://supply-risk-atlas-web.onrender.com"]
    return ["*"]
