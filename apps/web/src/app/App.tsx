"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Building2,
  Database,
  Factory,
  GitBranch,
  Globe2,
  Layers3,
  Network,
  RefreshCw,
  Route,
  ServerCog,
  ShieldAlert,
  SlidersHorizontal
} from "lucide-react";
import { createSupplyRiskApiClient, getMockSupplyRiskData, type SupplyRiskMockData } from "@supply-risk/api-client";
import { dashboardPages, type DashboardPageId } from "@supply-risk/shared-types";
import { Button, IconButton } from "./components";
import { renderPage } from "./pages";

const iconByPage: Record<DashboardPageId, typeof Globe2> = {
  "global-risk-cockpit": Globe2,
  "graph-explorer": Network,
  "company-risk-360": Building2,
  "path-explainer": Route,
  "shock-simulator": SlidersHorizontal,
  "causal-evidence-board": ShieldAlert,
  "graph-version-studio": GitBranch,
  "system-health-center": ServerCog
};

function getHashPage(): DashboardPageId {
  if (typeof window === "undefined") {
    return "global-risk-cockpit";
  }
  const hash = window.location.hash.replace("#", "");
  return dashboardPages.some((page) => page.id === hash) ? (hash as DashboardPageId) : "global-risk-cockpit";
}

function useHashPage() {
  const [pageId, setPageIdState] = useState<DashboardPageId>(getHashPage);

  useEffect(() => {
    const onHashChange = () => setPageIdState(getHashPage());
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

export function App() {
  const [pageId, setPageId] = useHashPage();
  const [data, setData] = useState<SupplyRiskMockData>(() => getMockSupplyRiskData());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState("booting");
  const [error, setError] = useState<string | null>(null);
  const activePage = dashboardPages.find((page) => page.id === pageId) ?? dashboardPages[0];
  const configuredApiBaseUrl = process.env.NEXT_PUBLIC_SUPPLY_RISK_API_URL?.trim();
  const apiClient = useMemo(
    () =>
      createSupplyRiskApiClient({
        baseUrl: configuredApiBaseUrl,
        useMockFallback: true
      }),
    [configuredApiBaseUrl]
  );
  const runtimeModeLabel = configuredApiBaseUrl ? (apiClient.mode === "real" ? "API linked" : "API fallback") : "mock data";
  const runtimeNotice =
    configuredApiBaseUrl && apiClient.mode !== "real" ? "Using mock fallback; API endpoint unavailable." : null;

  const refreshData = async () => {
    setIsRefreshing(true);
    setError(null);
    try {
      const [
        globalRiskCockpit,
        graphExplorer,
        companyRisk360,
        pathExplainer,
        causalEvidenceBoard,
        graphVersionStudio,
        systemHealthCenter
      ] = await Promise.all([
        apiClient.getGlobalRiskCockpit(),
        apiClient.getGraphExplorer(),
        apiClient.getCompanyRisk360(),
        apiClient.getPathExplainer(),
        apiClient.getCausalEvidenceBoard(),
        apiClient.getGraphVersionStudio(),
        apiClient.getSystemHealthCenter()
      ]);

      setData({
        globalRiskCockpit,
        graphExplorer,
        companyRisk360,
        pathExplainer,
        causalEvidenceBoard,
        graphVersionStudio,
        systemHealthCenter
      });
      setLastRefresh(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to refresh SupplyRiskAtlas data.");
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    void refreshData();
  }, []);

  return (
    <div className="app-shell">
      <aside className="side-rail" aria-label="SupplyRiskAtlas navigation">
        <div className="brand-lockup">
          <div className="brand-mark">
            <Factory aria-hidden="true" size={22} />
          </div>
          <div>
            <p className="brand-name">SupplyRiskAtlas</p>
            <span className="brand-system">industrial graph console</span>
          </div>
        </div>

        <nav>
          <ul className="nav-list">
            {dashboardPages.map((page) => {
              const Icon = iconByPage[page.id];
              return (
                <li key={page.id}>
                  <button
                    aria-current={activePage.id === page.id ? "page" : undefined}
                    className={`nav-button ${activePage.id === page.id ? "is-active" : ""}`}
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
            <span className={`dot ${apiClient.mode === "mock" ? "mock" : ""}`} />
          </div>
          <div className="mode-strip">
            <span>refresh</span>
            <span>{lastRefresh}</span>
          </div>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div className="title-block">
            <h1 className="page-title">{activePage.label}</h1>
            <p className="page-description">{error ?? runtimeNotice ?? activePage.description}</p>
          </div>
          <div className="top-actions">
            <IconButton icon={Activity} label="Open live monitor" />
            <IconButton icon={Layers3} label="Open layer catalog" />
            <Button icon={Database}>Graph build</Button>
            <Button disabled={isRefreshing} icon={RefreshCw} onClick={() => void refreshData()} variant="primary">
              {isRefreshing ? "Refreshing" : "Refresh"}
            </Button>
          </div>
        </header>

        <div className="content">{renderPage(activePage.id, { data, apiClient })}</div>
      </main>
    </div>
  );
}
