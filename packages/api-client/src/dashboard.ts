import type {
  ApiEnvelope,
  ApiMode,
  ApiResult,
  ApiSourceStatus,
  CausalEvidenceBoardData,
  CompanyRisk360Data,
  ForwardScenarioInput,
  ForwardScenarioResult,
  GlobalRiskCockpitData,
  GraphExplorerData,
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
  getSemiriskEntityRisk(entityId: string): Promise<ApiResult<SemiriskEntityRiskScore>>;
  getSemiriskRiskPortfolio(options?: { nodeType?: string | null; limit?: number }): Promise<ApiResult<SemiriskRiskPortfolioData>>;
  runForwardScenario(input: ForwardScenarioInput): Promise<ApiResult<ForwardScenarioResult>>;
  runReverseStress(input: ReverseStressInput): Promise<ApiResult<ReverseStressResult>>;
  optimizeInterventions(input: InterventionOptimizationInput): Promise<ApiResult<InterventionOptimizationResult>>;
  generateInvestigationReport(input: InvestigationReportInput): Promise<ApiResult<InvestigationReportData>>;
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

  const controller = typeof AbortController !== "undefined" ? new AbortController() : undefined;
  const timeoutHandle = controller
    ? globalThis.setTimeout(() => controller.abort(), options.requestTimeoutMs)
    : undefined;

  try {
    const headers = new Headers(init?.headers);
    if (!headers.has("content-type")) headers.set("content-type", "application/json");
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
    options.setEffectiveMode("real");
    const sourceStatus = error instanceof DashboardApiHttpError && (error.status === 401 || error.status === 403) ? "unauthorized" : "unavailable";
    const message =
      typeof DOMException !== "undefined" && error instanceof DOMException && error.name === "AbortError"
        ? `SupplyRiskAtlas API request timed out after ${options.requestTimeoutMs} ms at ${endpoint}`
        : error instanceof Error
          ? error.message
          : "Dashboard API request failed.";
    return createUnavailableResult(endpoint, sourceStatus, message, error);
  } finally {
    if (timeoutHandle) globalThis.clearTimeout(timeoutHandle);
  }
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
    requestTimeoutMs: Math.max(1000, options.requestTimeoutMs ?? 12000),
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
  };
}
