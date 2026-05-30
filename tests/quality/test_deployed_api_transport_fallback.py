from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_SOURCE = REPO_ROOT / "apps" / "web" / "src" / "app" / "App.tsx"
CLIENT_SOURCE = REPO_ROOT / "packages" / "api-client" / "src" / "dashboard.ts"


def test_deployed_web_wires_same_origin_read_and_write_paths_without_post_retries() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")

    assert "if (hostname === deploymentTarget) {\n    return \"/api/v1\";\n  }" in source
    assert "function resolveApiWriteBaseUrl" in source
    assert "NEXT_PUBLIC_SUPPLY_RISK_API_WRITE_URL" in source
    assert "function resolveApiReadFallbackBaseUrl" in source
    assert 'const sameOriginProxyBaseUrl = "/api/v1";' in source
    assert "https://supply-risk-atlas-api.onrender.com/api/v1" not in source
    assert "function resolveApiRequestTimeoutMs" in source
    assert "if (hostname === deploymentTarget) return 45000;" in source
    assert "readFallbackBaseUrl: configuredApiReadFallbackBaseUrl" in source
    assert "writeBaseUrl: configuredApiWriteBaseUrl" in source
    assert "requestTimeoutMs: configuredApiRequestTimeoutMs" in source
    assert "runDashboardRequestsSequentially" in source
    assert "dashboardRequestsForPage" in source
    assert "void refreshData(pageId)" in source
    assert "setDashboardResults((current) => ({ ...current, ...nextResults }))" in source
    assert "Promise.allSettled" not in source


def test_dashboard_client_retries_only_idempotent_reads_and_reports_http_status() -> None:
    source = CLIENT_SOURCE.read_text(encoding="utf-8")

    assert "const isIdempotentRead = method === \"GET\" || method === \"HEAD\";" in source
    assert "const MAX_PRIMARY_READ_ATTEMPTS_WITH_FALLBACK = 1;" in source
    assert "function attemptsForBaseUrl" in source
    assert "attemptsForBaseUrl(baseUrlIndex, baseUrls.length, isIdempotentRead)" in source
    assert "uniqueBaseUrls([baseUrl, options.readFallbackBaseUrl])" in source
    assert "lastError instanceof DashboardApiHttpError ? lastError.status : undefined" in source
    assert "transport_attempts: transportAttempts" in source
    assert "retry_hint:" in source
