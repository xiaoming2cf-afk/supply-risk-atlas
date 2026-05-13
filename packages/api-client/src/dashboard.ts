import type {
  ApiEnvelope,
  ApiMode,
  ApiResult,
  ApiSourceStatus,
  AnalyticsChartsData,
  AnalyticsExportData,
  AnalyticsNamedTableData,
  AnalyticsTablesData,
  CausalEvidenceBoardData,
  CompanyRisk360Data,
  ForwardScenarioInput,
  ForwardScenarioResult,
  GlobalRiskCockpitData,
  GraphBackendViewData,
  GraphExplorerData,
  GraphEvidenceData,
  GraphGeoData,
  GraphLayersData,
  GraphMatrixData,
  GraphNodeCatalogData,
  GraphRelationshipData,
  GraphScenarioOverlayData,
  GraphSourceCoverageData,
  GraphSupplyDemandBalanceData,
  GraphTimelineData,
  GraphExplorerQuery,
  GraphVersionStudioData,
  InterventionOptimizationInput,
  InterventionOptimizationResult,
  InvestigationReportData,
  InvestigationReportInput,
  PathExplainerData,
  PredictionCenterData,
  ReverseStressInput,
  ReverseStressResult,
  RunDetailData,
  RunHistoryData,
  SemiriskEntityRiskScore,
  SemiriskGraphNeighborhoodData,
  SemiriskGraphSnapshotData,
  SemiriskRiskPortfolioData,
  ShockSimulationInput,
  ShockSimulationResult,
  SystemHealthData,
} from "@supply-risk/shared-types";

export interface SupplyRiskApiClientOptions {
  baseUrl?: string;
  fetcher?: typeof fetch;
  requestTimeoutMs?: number;
}

export interface SupplyRiskApiClient {
  readonly mode: ApiMode;
  getGlobalRiskCockpit(): Promise<ApiResult<GlobalRiskCockpitData>>;
  getGraphExplorer(options?: GraphExplorerQuery): Promise<ApiResult<GraphExplorerData>>;
  getCountryLens(options?: Pick<GraphExplorerQuery, "countryCode" | "provinceCode" | "geoId">): Promise<ApiResult<GraphExplorerData>>;
  getCompanyRisk360(): Promise<ApiResult<CompanyRisk360Data>>;
  getPredictionCenter(): Promise<ApiResult<PredictionCenterData>>;
  getPathExplainer(): Promise<ApiResult<PathExplainerData>>;
  runShockSimulation(input: ShockSimulationInput): Promise<ApiResult<ShockSimulationResult>>;
  getCausalEvidenceBoard(): Promise<ApiResult<CausalEvidenceBoardData>>;
  getGraphVersionStudio(): Promise<ApiResult<GraphVersionStudioData>>;
  getSystemHealthCenter(): Promise<ApiResult<SystemHealthData>>;
  getSemiriskGraphSnapshot(): Promise<ApiResult<SemiriskGraphSnapshotData>>;
  getSemiriskGraphNeighborhood(nodeId: string, depth?: number): Promise<ApiResult<SemiriskGraphNeighborhoodData>>;
  getGraphView(options?: { mode?: string }): Promise<ApiResult<GraphBackendViewData>>;
  getGraphFocus(options?: { nodeId?: string; depth?: number }): Promise<ApiResult<GraphBackendViewData>>;
  getGraphClusters(): Promise<ApiResult<GraphBackendViewData>>;
  getGraphPathView(options?: { sourceNodeId?: string; targetNodeId?: string }): Promise<ApiResult<GraphBackendViewData>>;
  getGraphTimeline(options?: { limit?: number }): Promise<ApiResult<GraphTimelineData>>;
  getGraphGeo(options?: { limit?: number }): Promise<ApiResult<GraphGeoData>>;
  getGraphMatrix(options?: { limit?: number }): Promise<ApiResult<GraphMatrixData>>;
  getGraphLayers(): Promise<ApiResult<GraphLayersData>>;
  getGraphEvidence(options?: { sourceId?: string | null; limit?: number }): Promise<ApiResult<GraphEvidenceData>>;
  getGraphScenarioOverlay(options?: { runId?: string | null }): Promise<ApiResult<GraphScenarioOverlayData>>;
  getGraphNodeCatalog(options?: { limit?: number }): Promise<ApiResult<GraphNodeCatalogData>>;
  getGraphSourceCoverage(options?: { limit?: number }): Promise<ApiResult<GraphSourceCoverageData>>;
  getGraphSupplyRelationships(options?: { limit?: number }): Promise<ApiResult<GraphRelationshipData>>;
  getGraphDemandRelationships(options?: { limit?: number }): Promise<ApiResult<GraphRelationshipData>>;
  getGraphProductionDependencies(options?: { limit?: number }): Promise<ApiResult<GraphRelationshipData>>;
  getGraphSupplyDemandBalance(options?: { limit?: number }): Promise<ApiResult<GraphSupplyDemandBalanceData>>;
  getStageGraph(options?: { stageId?: string; relationshipClass?: string | null; limit?: number }): Promise<ApiResult<Record<string, unknown>>>;
  getAnalyticsCharts(options?: { chartId?: string | null; limit?: number }): Promise<ApiResult<AnalyticsChartsData>>;
  getAnalyticsTables(options?: { tableId?: string | null; limit?: number; offset?: number }): Promise<ApiResult<AnalyticsTablesData>>;
  getAnalyticsTable(tableId: string, options?: { limit?: number; offset?: number }): Promise<ApiResult<AnalyticsNamedTableData>>;
  exportAnalyticsTable(tableId: string, options?: { format?: "json" | "csv" | "markdown"; limit?: number; offset?: number }): Promise<ApiResult<AnalyticsExportData>>;
  getSemiriskEntityRisk(entityId: string): Promise<ApiResult<SemiriskEntityRiskScore>>;
  getSemiriskRiskPortfolio(options?: { nodeType?: string | null; limit?: number }): Promise<ApiResult<SemiriskRiskPortfolioData>>;
  runForwardScenario(input: ForwardScenarioInput): Promise<ApiResult<ForwardScenarioResult>>;
  runReverseStress(input: ReverseStressInput): Promise<ApiResult<ReverseStressResult>>;
  optimizeInterventions(input: InterventionOptimizationInput): Promise<ApiResult<InterventionOptimizationResult>>;
  generateInvestigationReport(input: InvestigationReportInput): Promise<ApiResult<InvestigationReportData>>;
  getInvestigationReport(reportId: string): Promise<ApiResult<InvestigationReportData>>;
  listRuns(): Promise<ApiResult<RunHistoryData>>;
  getRun(runId: string): Promise<ApiResult<RunDetailData>>;
}

export interface SupplyRiskDashboardData {
  globalRiskCockpit: GlobalRiskCockpitData;
  graphExplorer: GraphExplorerData;
  companyRisk360: CompanyRisk360Data;
  predictionCenter: PredictionCenterData;
  pathExplainer: PathExplainerData;
  causalEvidenceBoard: CausalEvidenceBoardData;
  graphVersionStudio: GraphVersionStudioData;
  systemHealthCenter: SystemHealthData;
}

interface RequestJsonOptions {
  fetcher: typeof fetch;
  setEffectiveMode: (mode: ApiMode) => void;
  requestTimeoutMs: number;
}

const MAX_NETWORK_ATTEMPTS = 3;
const NETWORK_RETRY_BACKOFF_MS = 750;

async function requestJson<T>(
  baseUrl: string | undefined,
  endpoint: string,
  init: RequestInit | undefined,
  options: RequestJsonOptions,
): Promise<ApiResult<T>> {
  if (!baseUrl) {
    options.setEffectiveMode("real");
    return createUnavailableResult(endpoint, "unavailable", "No dashboard API base URL configured.");
  }

  let lastError: unknown = undefined;
  for (let attempt = 1; attempt <= MAX_NETWORK_ATTEMPTS; attempt += 1) {
    const controller = typeof AbortController !== "undefined" ? new AbortController() : undefined;
    const timeoutHandle = controller
      ? globalThis.setTimeout(() => controller.abort(), options.requestTimeoutMs)
      : undefined;

    try {
      const headers = new Headers(init?.headers);
      const method = init?.method?.toUpperCase() ?? "GET";
      const sendsJsonBody = init?.body !== undefined && method !== "GET" && method !== "HEAD";
      if (sendsJsonBody && !headers.has("content-type")) headers.set("content-type", "application/json");
      const response = await options.fetcher(`${baseUrl.replace(/\/$/, "")}${endpoint}`, {
        ...init,
        headers,
        signal: init?.signal ?? controller?.signal,
      });
      const payload = await response.json().catch(() => null);
      if (payload && typeof payload === "object" && "status" in payload && "data" in payload) {
        options.setEffectiveMode("real");
        return normalizeApiPayload<T>(payload, response.status, endpoint);
      }
      if (!response.ok) {
        throw new DashboardApiHttpError(`SupplyRiskAtlas API ${response.status} at ${endpoint}`, response.status, payload);
      }
      return createUnavailableResult(endpoint, "partial", "API response did not include a metadata envelope.", undefined, response.status);
    } catch (error) {
      lastError = error;
      if (error instanceof DashboardApiHttpError || attempt === MAX_NETWORK_ATTEMPTS) {
        break;
      }
      await sleep(NETWORK_RETRY_BACKOFF_MS * attempt);
    } finally {
      if (timeoutHandle) globalThis.clearTimeout(timeoutHandle);
    }
  }

  options.setEffectiveMode("real");
  const sourceStatus =
    lastError instanceof DashboardApiHttpError && (lastError.status === 401 || lastError.status === 403)
      ? "unauthorized"
      : "unavailable";
  const message =
    typeof DOMException !== "undefined" && lastError instanceof DOMException && lastError.name === "AbortError"
      ? `SupplyRiskAtlas API request timed out after ${options.requestTimeoutMs} ms at ${endpoint}`
      : lastError instanceof Error
        ? lastError.message
        : "Dashboard API request failed.";
  return createUnavailableResult(endpoint, sourceStatus, message, lastError);
}

function sleep(ms: number) {
  return new Promise((resolve) => globalThis.setTimeout(resolve, ms));
}

class DashboardApiHttpError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly payload: unknown,
  ) {
    super(message);
    this.name = "DashboardApiHttpError";
  }
}

function normalizeApiPayload<T>(
  payload: unknown,
  httpStatus: number | undefined,
  endpoint: string,
): ApiResult<T> {
  if (payload && typeof payload === "object" && "status" in payload && "data" in payload) {
    const envelope = payload as ApiEnvelope<T>;
    const sourceStatus = envelope.source_status ?? inferSourceStatus(envelope);
    const normalizedEnvelope: ApiEnvelope<T> = {
      ...envelope,
      mode: "real",
      source_status: sourceStatus,
    };
    return {
      data: normalizedEnvelope.data ?? null,
      envelope: normalizedEnvelope,
      mode: "real",
      sourceStatus,
      receivedAt: new Date().toISOString(),
      httpStatus,
    };
  }
  return createUnavailableResult(
    endpoint,
    "partial",
    "API response did not include a metadata envelope.",
    undefined,
    httpStatus,
  );
}

function inferSourceStatus<T>(envelope: ApiEnvelope<T>): ApiSourceStatus {
  if (envelope.errors?.some((error) => error.code.toLowerCase().includes("unauthorized"))) return "unauthorized";
  if (envelope.errors?.length || envelope.status === "error") return "error";
  if (envelope.warnings?.some((warning) => /stale/i.test(warning))) return "stale";
  if (envelope.warnings?.some((warning) => /partial/i.test(warning))) return "partial";
  return "fresh";
}

function createUnavailableResult<T>(
  endpoint: string,
  sourceStatus: ApiSourceStatus,
  warning: string,
  cause?: unknown,
  httpStatus?: number,
): ApiResult<T> {
  const now = new Date().toISOString();
  const errors = cause instanceof Error ? [{ code: "dashboard_api_unavailable", message: cause.message }] : [];
  const envelope: ApiEnvelope<T> = {
    request_id: `client-${Math.random().toString(36).slice(2)}`,
    status: "error",
    data: null,
    metadata: {
      graph_version: "unavailable",
      feature_version: "unavailable",
      label_version: "unavailable",
      model_version: "unavailable",
      as_of_time: now,
      audit_ref: "client-real-api-unavailable",
      lineage_ref: `api-unavailable://${endpoint.replace(/^\//, "")}`,
      data_mode: "real",
      freshness_status: "unavailable",
    },
    warnings: [warning],
    errors,
    mode: "real",
    source_status: sourceStatus,
    source: {
      name: "SupplyRiskAtlas API",
      lineage_ref: `api-unavailable://${endpoint.replace(/^\//, "")}`,
      license: "No business payload rendered until a real API envelope is accepted.",
    },
  };

  return {
    data: null,
    envelope,
    mode: "real",
    sourceStatus,
    receivedAt: now,
    httpStatus,
  };
}

function queryString(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}

export function createSupplyRiskApiClient(options: SupplyRiskApiClientOptions = {}): SupplyRiskApiClient {
  const baseUrl = options.baseUrl?.trim();
  let effectiveMode: ApiMode = "real";
  const setEffectiveMode = (mode: ApiMode) => {
    effectiveMode = mode;
  };
  const clientOptions = {
    fetcher: options.fetcher ?? ((input, init) => globalThis.fetch(input, init)),
    requestTimeoutMs: Math.max(1000, options.requestTimeoutMs ?? 60000),
    setEffectiveMode,
  };

  return {
    get mode() {
      return effectiveMode;
    },
    getGlobalRiskCockpit: () => requestJson(baseUrl, "/dashboard/global-risk-cockpit", undefined, clientOptions),
    getGraphExplorer: (options) =>
      requestJson(baseUrl, `/dashboard/graph-explorer${queryString({
        selected_node_id: options?.selectedNodeId,
        path_direction: options?.pathDirection,
        country_code: options?.countryCode ?? undefined,
        province_code: options?.provinceCode ?? undefined,
        geo_id: options?.geoId ?? undefined,
        node_kinds: options?.nodeKinds?.join(","),
        edge_types: options?.edgeTypes?.join(","),
      })}`, undefined, clientOptions),
    getCountryLens: (options) =>
      requestJson(baseUrl, `/dashboard/country-lens${queryString({
        country_code: options?.countryCode ?? undefined,
        province_code: options?.provinceCode ?? undefined,
        geo_id: options?.geoId ?? undefined,
      })}`, undefined, clientOptions),
    getCompanyRisk360: () => requestJson(baseUrl, "/dashboard/company-risk-360", undefined, clientOptions),
    getPredictionCenter: () => requestJson(baseUrl, "/dashboard/prediction-center", undefined, clientOptions),
    getPathExplainer: () => requestJson(baseUrl, "/dashboard/path-explainer", undefined, clientOptions),
    runShockSimulation: (input) =>
      requestJson(
        baseUrl,
        "/dashboard/shock-simulator",
        { method: "POST", body: JSON.stringify(input) },
        clientOptions,
      ),
    getCausalEvidenceBoard: () => requestJson(baseUrl, "/dashboard/causal-evidence-board", undefined, clientOptions),
    getGraphVersionStudio: () => requestJson(baseUrl, "/dashboard/graph-version-studio", undefined, clientOptions),
    getSystemHealthCenter: () => requestJson(baseUrl, "/dashboard/system-health-center", undefined, clientOptions),
    getSemiriskGraphSnapshot: () => requestJson(baseUrl, "/graph/snapshot", undefined, clientOptions),
    getSemiriskGraphNeighborhood: (nodeId, depth = 1) =>
      requestJson(
        baseUrl,
        `/graph/neighborhood${queryString({ node_id: nodeId, depth })}`,
        undefined,
        clientOptions,
      ),
    getGraphView: (options) =>
      requestJson(baseUrl, `/graph/view${queryString({ mode: options?.mode })}`, undefined, clientOptions),
    getGraphFocus: (options) =>
      requestJson(
        baseUrl,
        `/graph/focus${queryString({ node_id: options?.nodeId, depth: options?.depth })}`,
        undefined,
        clientOptions,
      ),
    getGraphClusters: () => requestJson(baseUrl, "/graph/clusters", undefined, clientOptions),
    getGraphPathView: (options) =>
      requestJson(
        baseUrl,
        `/graph/path-view${queryString({
          source_node_id: options?.sourceNodeId,
          target_node_id: options?.targetNodeId,
        })}`,
        undefined,
        clientOptions,
      ),
    getGraphTimeline: (options) =>
      requestJson(baseUrl, `/graph/timeline${queryString({ limit: options?.limit })}`, undefined, clientOptions),
    getGraphGeo: (options) =>
      requestJson(baseUrl, `/graph/geo${queryString({ limit: options?.limit })}`, undefined, clientOptions),
    getGraphMatrix: (options) =>
      requestJson(baseUrl, `/graph/matrix${queryString({ limit: options?.limit })}`, undefined, clientOptions),
    getGraphLayers: () => requestJson(baseUrl, "/graph/layers", undefined, clientOptions),
    getGraphEvidence: (options) =>
      requestJson(
        baseUrl,
        `/graph/evidence${queryString({ source_id: options?.sourceId ?? undefined, limit: options?.limit })}`,
        undefined,
        clientOptions,
      ),
    getGraphScenarioOverlay: (options) =>
      requestJson(
        baseUrl,
        `/graph/scenario-overlay${queryString({ run_id: options?.runId ?? undefined })}`,
        undefined,
        clientOptions,
      ),
    getGraphNodeCatalog: (options) =>
      requestJson(baseUrl, `/graph/node-catalog${queryString({ limit: options?.limit })}`, undefined, clientOptions),
    getGraphSourceCoverage: (options) =>
      requestJson(baseUrl, `/graph/source-coverage${queryString({ limit: options?.limit })}`, undefined, clientOptions),
    getGraphSupplyRelationships: (options) =>
      requestJson(baseUrl, `/graph/supply-relationships${queryString({ limit: options?.limit })}`, undefined, clientOptions),
    getGraphDemandRelationships: (options) =>
      requestJson(baseUrl, `/graph/demand-relationships${queryString({ limit: options?.limit })}`, undefined, clientOptions),
    getGraphProductionDependencies: (options) =>
      requestJson(baseUrl, `/graph/production-dependencies${queryString({ limit: options?.limit })}`, undefined, clientOptions),
    getGraphSupplyDemandBalance: (options) =>
      requestJson(baseUrl, `/graph/supply-demand-balance${queryString({ limit: options?.limit })}`, undefined, clientOptions),
    getStageGraph: (options) =>
      requestJson(
        baseUrl,
        `/stage-graph/${encodeURIComponent(options?.stageId ?? "L5_fabrication")}${queryString({
          limit: options?.limit,
          relationship_class: options?.relationshipClass ?? undefined,
        })}`,
        undefined,
        clientOptions,
      ),
    getAnalyticsCharts: (options) =>
      requestJson(
        baseUrl,
        `/analytics/charts${queryString({ chart_id: options?.chartId ?? undefined, limit: options?.limit })}`,
        undefined,
        clientOptions,
      ),
    getAnalyticsTables: (options) =>
      requestJson(
        baseUrl,
        `/analytics/tables${queryString({ table_id: options?.tableId ?? undefined, limit: options?.limit, offset: options?.offset })}`,
        undefined,
        clientOptions,
      ),
    getAnalyticsTable: (tableId, options) =>
      requestJson(
        baseUrl,
        `/analytics/tables/${encodeURIComponent(tableId)}${queryString({ limit: options?.limit, offset: options?.offset })}`,
        undefined,
        clientOptions,
      ),
    exportAnalyticsTable: (tableId, options) =>
      requestJson(
        baseUrl,
        `/analytics/export/${encodeURIComponent(tableId)}${queryString({
          format: options?.format,
          limit: options?.limit,
          offset: options?.offset,
        })}`,
        undefined,
        clientOptions,
      ),
    getSemiriskEntityRisk: (entityId) =>
      requestJson(baseUrl, `/risk/entities/${encodeURIComponent(entityId)}`, undefined, clientOptions),
    getSemiriskRiskPortfolio: (options) =>
      requestJson(
        baseUrl,
        `/risk/portfolio${queryString({
          node_type: options?.nodeType ?? undefined,
          limit: options?.limit,
        })}`,
        undefined,
        clientOptions,
      ),
    runForwardScenario: (input) =>
      requestJson(
        baseUrl,
        "/scenarios/forward",
        { method: "POST", body: JSON.stringify(input) },
        clientOptions,
      ),
    runReverseStress: (input) =>
      requestJson(
        baseUrl,
        "/scenarios/reverse",
        { method: "POST", body: JSON.stringify(input) },
        clientOptions,
      ),
    optimizeInterventions: (input) =>
      requestJson(
        baseUrl,
        "/optimization/interventions",
        { method: "POST", body: JSON.stringify(input) },
        clientOptions,
      ),
    generateInvestigationReport: (input) =>
      requestJson(
        baseUrl,
        "/reports/investigation",
        { method: "POST", body: JSON.stringify(input) },
        clientOptions,
      ),
    getInvestigationReport: (reportId) =>
      requestJson(baseUrl, `/reports/${encodeURIComponent(reportId)}`, undefined, clientOptions),
    listRuns: () => requestJson(baseUrl, "/runs", undefined, clientOptions),
    getRun: (runId) => requestJson(baseUrl, `/runs/${encodeURIComponent(runId)}`, undefined, clientOptions),
  };
}
