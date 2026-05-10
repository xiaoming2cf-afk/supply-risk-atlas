"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Building2,
  Database,
  Factory,
  Gauge,
  GitBranch,
  Globe2,
  Network,
  RefreshCw,
  Route,
  ServerCog,
  ShieldAlert,
  SlidersHorizontal
} from "lucide-react";
import { createSupplyRiskApiClient, type SupplyRiskDashboardData } from "@supply-risk/api-client";
import { dashboardPages, type ApiResult, type DashboardPageId } from "@supply-risk/shared-types";
import { Button } from "./components";
import {
  I18nProvider,
  pageLanguages,
  translateDashboardPage,
  translateText,
  useI18n,
  type PageLanguage
} from "./i18n";
import { renderPage } from "./pages";

const iconByPage: Record<DashboardPageId, typeof Globe2> = {
  "global-risk-cockpit": Globe2,
  "graph-explorer": Network,
  "company-risk-360": Building2,
  "prediction-center": Gauge,
  "path-analysis": Route,
  "country-lens": Globe2,
  "path-explainer": Route,
  "shock-simulator": SlidersHorizontal,
  "reverse-stress-lab": GitBranch,
  "intervention-optimizer": Factory,
  "causal-evidence-board": ShieldAlert,
  "graph-version-studio": GitBranch,
  "system-health-center": ServerCog
};

const deploymentTarget = "supply-risk-atlas-web.onrender.com";
const publicPageIds = new Set<DashboardPageId>([
  "system-health-center",
  "global-risk-cockpit",
  "graph-explorer",
  "company-risk-360",
  "prediction-center",
  "path-analysis",
  "country-lens",
  "shock-simulator",
  "reverse-stress-lab",
  "intervention-optimizer",
  "causal-evidence-board",
]);
const publicDashboardPages = dashboardPages.filter((page) => publicPageIds.has(page.id));

type DashboardResultMap = Partial<Record<DashboardPageId, ApiResult<unknown>>>;
type DashboardDataState = Partial<SupplyRiskDashboardData>;

function resolveApiBaseUrl(hostname: string | null) {
  const configured = process.env.NEXT_PUBLIC_SUPPLY_RISK_API_URL?.trim();
  if (
    hostname === "supply-risk-atlas-web.onrender.com" &&
    (!configured || configured === "/api/v1")
  ) {
    return "https://supply-risk-atlas-api.onrender.com/api/v1";
  }
  if (configured) {
    return configured;
  }
  if (hostname === "127.0.0.1" || hostname === "localhost") {
    return "/api/v1";
  }
  return "/api/v1";
}

function getHashPage(): DashboardPageId {
  if (typeof window === "undefined") {
    return "system-health-center";
  }
  const hash = window.location.hash.replace("#", "");
  return publicDashboardPages.some((page) => page.id === hash) ? (hash as DashboardPageId) : "system-health-center";
}

function useHashPage() {
  const [pageId, setPageIdState] = useState<DashboardPageId>("system-health-center");

  useEffect(() => {
    const onHashChange = () => setPageIdState(getHashPage());
    onHashChange();
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const setPageId = (nextPageId: DashboardPageId) => {
    if (nextPageId === pageId) return;
    if (typeof window !== "undefined") {
      window.location.hash = nextPageId;
    }
    setPageIdState(nextPageId);
  };

  return [pageId, setPageId] as const;
}

function getInitialLanguage(): PageLanguage {
  if (typeof window === "undefined") return "en";
  const stored = window.localStorage.getItem("supply-risk-atlas-language");
  if (stored === "zh" || stored === "en" || stored === "fr") return stored;
  return "en";
}

export function App() {
  const [pageId, setPageId] = useHashPage();
  const [language, setLanguageState] = useState<PageLanguage>("en");
  const [data, setData] = useState<DashboardDataState | null>(null);
  const [dashboardResults, setDashboardResults] = useState<DashboardResultMap>({});
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState("booting");
  const [error, setError] = useState<string | null>(null);
  const [runtimeHostname, setRuntimeHostname] = useState<string | null>(null);
  const activePageDefinition = publicDashboardPages.find((page) => page.id === pageId) ?? publicDashboardPages[0];
  const localizedPages = useMemo(
    () => publicDashboardPages.map((page) => translateDashboardPage(page, language)),
    [language]
  );
  const activePage = translateDashboardPage(activePageDefinition, language);
  const configuredApiBaseUrl = resolveApiBaseUrl(runtimeHostname);
  const hasResolvedRuntimeHostname = runtimeHostname !== null;
  const apiClient = useMemo(
    () =>
      createSupplyRiskApiClient({
        baseUrl: configuredApiBaseUrl
      }),
    [configuredApiBaseUrl]
  );
  const t = (value: string) => translateText(value, language);
  const activeResultKey: DashboardPageId =
    pageId === "shock-simulator" || pageId === "reverse-stress-lab" || pageId === "intervention-optimizer"
      ? "global-risk-cockpit"
      : pageId === "path-analysis" || pageId === "country-lens"
        ? "graph-explorer"
        : pageId;
  const activeResult = dashboardResults[activeResultKey];
  const runtimeModeLabel = configuredApiBaseUrl ? t("Public data") : t("Data unavailable");
  const dataStatus = getDataStatus(activeResult, Boolean(configuredApiBaseUrl), error);
  const canRenderBusinessData = canRenderPageData(activePage.id, data, activeResult, Boolean(configuredApiBaseUrl));

  const setLanguage = (nextLanguage: PageLanguage) => {
    setLanguageState(nextLanguage);
    if (typeof window !== "undefined") {
      window.localStorage.setItem("supply-risk-atlas-language", nextLanguage);
    }
  };

  const refreshData = useCallback(async () => {
    setIsRefreshing(true);
    setError(null);
    const requests: Array<[DashboardPageId, Promise<ApiResult<unknown>>]> = [
      ["system-health-center", apiClient.getSystemHealthCenter() as Promise<ApiResult<unknown>>],
      ["global-risk-cockpit", apiClient.getGlobalRiskCockpit() as Promise<ApiResult<unknown>>],
      ["graph-explorer", apiClient.getGraphExplorer() as Promise<ApiResult<unknown>>],
      ["company-risk-360", apiClient.getCompanyRisk360() as Promise<ApiResult<unknown>>],
      ["prediction-center", apiClient.getPredictionCenter() as Promise<ApiResult<unknown>>],
      ["path-explainer", apiClient.getPathExplainer() as Promise<ApiResult<unknown>>],
      ["causal-evidence-board", apiClient.getCausalEvidenceBoard() as Promise<ApiResult<unknown>>]
    ];

    try {
      const settledResults = await Promise.allSettled(
        requests.map(async ([requestPageId, request]) => [requestPageId, await request] as const)
      );

      const nextResults: DashboardResultMap = {};
      let rejectedCount = 0;
      for (const settledResult of settledResults) {
        if (settledResult.status === "fulfilled") {
          const [requestPageId, result] = settledResult.value;
          nextResults[requestPageId] = result;
        } else {
          rejectedCount += 1;
        }
      }
      const systemHealthCenterResult =
        nextResults["system-health-center"] as ApiResult<SupplyRiskDashboardData["systemHealthCenter"]> | undefined;
      const globalRiskCockpitResult =
        nextResults["global-risk-cockpit"] as ApiResult<SupplyRiskDashboardData["globalRiskCockpit"]> | undefined;
      const graphExplorerResult =
        nextResults["graph-explorer"] as ApiResult<SupplyRiskDashboardData["graphExplorer"]> | undefined;
      const companyRisk360Result =
        nextResults["company-risk-360"] as ApiResult<SupplyRiskDashboardData["companyRisk360"]> | undefined;
      const predictionCenterResult =
        nextResults["prediction-center"] as ApiResult<SupplyRiskDashboardData["predictionCenter"]> | undefined;
      const pathExplainerResult =
        nextResults["path-explainer"] as ApiResult<SupplyRiskDashboardData["pathExplainer"]> | undefined;
      const causalEvidenceBoardResult =
        nextResults["causal-evidence-board"] as ApiResult<SupplyRiskDashboardData["causalEvidenceBoard"]> | undefined;

      setDashboardResults(nextResults);
      setData((current) => {
        const nextData: DashboardDataState = { ...(current ?? {}) };
        if (hasVerifiedHealthResult(systemHealthCenterResult)) nextData.systemHealthCenter = systemHealthCenterResult.data;
        if (isAcceptedRealResult(globalRiskCockpitResult)) nextData.globalRiskCockpit = globalRiskCockpitResult.data;
        if (isAcceptedRealResult(graphExplorerResult)) nextData.graphExplorer = graphExplorerResult.data;
        if (isAcceptedRealResult(companyRisk360Result)) nextData.companyRisk360 = companyRisk360Result.data;
        if (isAcceptedRealResult(predictionCenterResult)) nextData.predictionCenter = predictionCenterResult.data;
        if (isAcceptedRealResult(pathExplainerResult)) nextData.pathExplainer = pathExplainerResult.data;
        if (isAcceptedRealResult(causalEvidenceBoardResult)) nextData.causalEvidenceBoard = causalEvidenceBoardResult.data;
        return Object.keys(nextData).length > 0 ? nextData : null;
      });
      if (rejectedCount === requests.length) {
        setError("All public dashboard endpoints are unavailable. Page panels show the failed source status.");
      } else if (rejectedCount > 0) {
        setError(`${rejectedCount} public dashboard endpoint(s) did not return. Page panels show degraded source status where needed.`);
      }
      setLastRefresh(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    } catch {
      setError("Public data is temporarily unavailable. Refresh to retry.");
    } finally {
      setIsRefreshing(false);
    }
  }, [apiClient]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setRuntimeHostname(window.location.hostname);
      setLanguageState(getInitialLanguage());
    }
  }, []);

  useEffect(() => {
    if (!hasResolvedRuntimeHostname && !configuredApiBaseUrl) return;
    void refreshData();
  }, [configuredApiBaseUrl, hasResolvedRuntimeHostname, refreshData]);

  useEffect(() => {
    document.documentElement.lang = language === "zh" ? "zh-CN" : language;
  }, [language]);

  return (
    <I18nProvider language={language} setLanguage={setLanguage}>
    <div className="app-shell" data-deploy-target={deploymentTarget}>
      <aside className="side-rail" aria-label="SupplyRiskAtlas navigation">
        <div className="brand-lockup">
          <div className="brand-mark">
            <Factory aria-hidden="true" size={22} />
          </div>
          <div>
            <p className="brand-name">SupplyRiskAtlas</p>
            <span className="brand-system">{t("industrial graph console")}</span>
          </div>
        </div>

        <label className="language-control" data-feature="page-translator">
          <span>{t("Page language")}</span>
          <select
            aria-label={t("Page language")}
            className="page-language-select"
            value={language}
            onChange={(event) => setLanguage(event.target.value as PageLanguage)}
          >
            {pageLanguages.map((option) => (
              <option key={option.code} value={option.code}>
                {option.nativeLabel} / {option.label}
              </option>
            ))}
          </select>
        </label>

        <nav>
          <ul className="nav-list">
            {localizedPages.map((page) => {
              const Icon = iconByPage[page.id];
              return (
                <li key={page.id}>
                  <button
                    aria-current={activePage.id === page.id ? "page" : undefined}
                    className={`nav-button ${activePage.id === page.id ? "is-active" : ""}`}
                    data-page-id={page.id}
                    onClick={() => setPageId(page.id)}
                    type="button"
                  >
                    <Icon aria-hidden="true" />
                    <span className="nav-copy">
                      <span className="nav-label">{page.label}</span>
                      <span className="nav-description">{page.description}</span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="rail-footer">
          <div className="mode-strip">
            <span>{runtimeModeLabel}</span>
            <span className={`dot ${configuredApiBaseUrl ? "" : "mock"}`} />
          </div>
          <div className="mode-strip">
            <span>{t("refresh")}</span>
            <span>{lastRefresh}</span>
          </div>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div className="title-block">
            <h1 className="page-title">{activePage.label}</h1>
            <p className="page-description">{error ? t(error) : activePage.description}</p>
          </div>
          <div className="top-actions">
            <Button disabled={isRefreshing} icon={RefreshCw} onClick={() => void refreshData()} variant="primary">
              {isRefreshing ? "Refreshing" : "Refresh"}
            </Button>
          </div>
        </header>

        <DataLineageBanner status={dataStatus} />

        <div className="content">
          {canRenderBusinessData ? (
            renderPage(activePage.id, { data: data ?? {}, apiClient })
          ) : (
            <RealDataRequiredPanel status={dataStatus} isRefreshing={isRefreshing} />
          )}
        </div>
      </main>
    </div>
    </I18nProvider>
  );
}

function RealDataRequiredPanel({ status, isRefreshing }: { status: DataStatus; isRefreshing: boolean }) {
  const { language } = useI18n();
  const t = (value: string) => translateText(value, language);

  return (
    <section className="empty-state" data-real-data-gate="blocked">
      <div className="empty-state-shell">
        <span className="empty-state-mark" aria-hidden="true">
          <Database size={22} />
        </span>
        <h2>{t(isRefreshing ? "Loading public data" : "Data temporarily unavailable")}</h2>
        <p>{t(status.message)}</p>
        <div className="lineage-chips public-status-chips" aria-label={t("Data status")}>
          <span>{t("Coverage")}: {t(publicCoverageLabel(status.sourceStatus))}</span>
          <span>{t("Source")}: {publicSourceLabel(status.sourceName)}</span>
        </div>
      </div>
    </section>
  );
}

function DataLineageBanner({ status }: { status: DataStatus }) {
  const { language } = useI18n();
  const t = (value: string) => translateText(value, language);

  return (
    <section
      aria-live="polite"
      className={`data-lineage-banner ${status.tone}`}
      data-data-mode={status.mode}
      data-source-status={status.sourceStatus}
    >
      <div className="lineage-copy">
        <div className="lineage-title-row">
          <span className="lineage-pulse" aria-hidden="true" />
          <strong>{t(status.title)}</strong>
        </div>
        <p>{t(status.message)}</p>
      </div>
      <div className="lineage-chips public-status-chips" aria-label={t("Data status")}>
        <span>{t("Coverage")}: {t(publicCoverageLabel(status.sourceStatus))}</span>
        <span>{t("Updated")}: {formatPublicFreshness(status.freshness)}</span>
        <span>{t("Source")}: {publicSourceLabel(status.sourceName)}</span>
      </div>
    </section>
  );
}

interface DataStatus {
  tone: "fresh" | "stale" | "partial" | "blocked" | "fallback";
  title: string;
  message: string;
  mode: string;
  sourceStatus: string;
  freshness: string;
  sourceName: string;
  lineage: string;
  requestId: string;
  details: string[];
}

function getDataStatus(result: ApiResult<unknown> | undefined, hasApiBaseUrl: boolean, error: string | null): DataStatus {
  if (!result) {
    return {
      tone: hasApiBaseUrl ? "partial" : "blocked",
      title: hasApiBaseUrl ? "Connecting to public data" : "Public data unavailable",
      message: hasApiBaseUrl
        ? "The page is connecting to the public evidence graph."
        : "Public data is temporarily unavailable. Refresh or try again shortly.",
      mode: hasApiBaseUrl ? "pending" : "unavailable",
      sourceStatus: hasApiBaseUrl ? "partial" : "unavailable",
      freshness: "unknown",
      sourceName: hasApiBaseUrl ? "SupplyRiskAtlas API" : "not configured",
      lineage: "unavailable",
      requestId: "pending",
      details: error ? [error] : [],
    };
  }

  const envelope = result.envelope;
  const sourceStatus = result.sourceStatus;
  const tone =
    sourceStatus === "unauthorized"
      ? "blocked"
      : sourceStatus === "unavailable" || sourceStatus === "error"
        ? "blocked"
      : sourceStatus === "fallback"
        ? "fallback"
        : sourceStatus === "stale"
          ? "stale"
          : sourceStatus === "partial"
            ? "partial"
            : "fresh";
  const isUnavailable = sourceStatus === "unavailable" || sourceStatus === "error";
  const isFallback = sourceStatus === "fallback" || sourceStatus === "unauthorized" || isUnavailable;
  const title =
    sourceStatus === "unauthorized"
      ? "Public data unavailable"
      : isUnavailable
        ? "Public data unavailable"
      : isFallback
        ? "Public data unavailable"
        : sourceStatus === "stale"
          ? "Public data updating"
          : sourceStatus === "partial"
            ? "Partial public data"
            : "Public data connected";

  return {
    tone,
    title,
    message: isFallback
      ? "Public data is temporarily unavailable. Refresh or try again shortly."
      : sourceStatus === "partial" || sourceStatus === "stale"
        ? "Public source data is connected with limited freshness or coverage."
        : "Public source data is connected and ready for analysis.",
    mode: result.mode,
    sourceStatus,
    freshness: envelope.metadata?.as_of_time ?? result.receivedAt,
    sourceName: envelope.source?.name ?? "SupplyRiskAtlas API",
    lineage: envelope.source?.lineage_ref ?? envelope.metadata?.lineage_ref ?? "unavailable",
    requestId: envelope.request_id,
    details: [...(envelope.warnings ?? []), ...(envelope.errors ?? []).map((item) => `${item.code}: ${item.message}`)],
  };
}

function canRenderPageData(
  pageId: DashboardPageId,
  data: DashboardDataState | null,
  activeResult: ApiResult<unknown> | undefined,
  hasApiBaseUrl: boolean,
) {
  if (pageId === "shock-simulator" || pageId === "reverse-stress-lab" || pageId === "intervention-optimizer") return hasApiBaseUrl;
  if (pageId === "company-risk-360") return hasApiBaseUrl;
  if (pageId === "system-health-center") {
    return Boolean(data?.systemHealthCenter && hasVerifiedHealthResult(activeResult as ApiResult<unknown> | undefined));
  }
  if (!data || !isAcceptedRealResult(activeResult)) return false;
  switch (pageId) {
    case "global-risk-cockpit":
      return Boolean(data.globalRiskCockpit);
    case "graph-explorer":
    case "path-analysis":
    case "country-lens":
      return Boolean(data.graphExplorer && data.pathExplainer);
    case "prediction-center":
      return Boolean(data.predictionCenter);
    case "causal-evidence-board":
      return Boolean(data.causalEvidenceBoard);
    default:
      return false;
  }
}

function hasVerifiedHealthResult<T>(result: ApiResult<T> | undefined): result is ApiResult<T> & { data: T } {
  if (!result || result.data === null) return false;
  if (result.envelope.status !== "success") return false;
  return !["fallback", "unavailable", "unauthorized", "error"].includes(result.sourceStatus);
}

function publicCoverageLabel(sourceStatus: string) {
  if (sourceStatus === "fresh") return "Current";
  if (sourceStatus === "partial" || sourceStatus === "stale") return "Limited";
  if (sourceStatus === "unavailable" || sourceStatus === "error" || sourceStatus === "unauthorized") return "Unavailable";
  return "Checking";
}

function publicSourceLabel(sourceName: string) {
  if (!sourceName || sourceName === "not configured") return "Public evidence graph";
  if (sourceName.includes("SupplyRiskAtlas")) return "Public evidence graph";
  if (sourceName.includes("Public")) return "Public evidence graph";
  return sourceName;
}

function formatPublicFreshness(value: string) {
  if (!value || ["unknown", "unavailable", "pending"].includes(value)) return "Checking";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Checking";
  return parsed.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function isAcceptedRealResult<T>(result: ApiResult<T> | undefined): result is ApiResult<T> & { data: T } {
  if (!result || result.data === null) return false;
  if (result.envelope.status !== "success") return false;
  return !["fallback", "unavailable", "unauthorized", "error"].includes(result.sourceStatus);
}
