from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_SOURCE = REPO_ROOT / "apps" / "web" / "src" / "app" / "App.tsx"
CLIENT_SOURCE = REPO_ROOT / "packages" / "api-client" / "src" / "dashboard.ts"


def test_deployed_web_wires_same_origin_read_fallback_without_changing_write_base() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")

    assert "function resolveApiReadFallbackBaseUrl" in source
    assert 'const sameOriginProxyBaseUrl = "/api/v1";' in source
    assert "if (hostname === deploymentTarget) return sameOriginProxyBaseUrl;" in source
    assert "readFallbackBaseUrl: configuredApiReadFallbackBaseUrl" in source
    assert "writeBaseUrl: configuredApiWriteBaseUrl" in source


def test_dashboard_client_retries_only_idempotent_reads_and_reports_http_status() -> None:
    source = CLIENT_SOURCE.read_text(encoding="utf-8")

    assert "const isIdempotentRead = method === \"GET\" || method === \"HEAD\";" in source
    assert "const attemptsPerBaseUrl = isIdempotentRead ? MAX_NETWORK_ATTEMPTS : 1;" in source
    assert "uniqueBaseUrls([baseUrl, options.readFallbackBaseUrl])" in source
    assert "lastError instanceof DashboardApiHttpError ? lastError.status : undefined" in source
    assert "transport_attempts: transportAttempts" in source
    assert "retry_hint:" in source
