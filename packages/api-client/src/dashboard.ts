import type {
  ApiEnvelope,
  ApiMode,
  ApiResult,
  ApiSourceStatus,
  CausalEvidenceBoardData,
  CompanyRisk360Data,
  GlobalRiskCockpitData,
  GraphExplorerData,
  GraphVersionStudioData,
  PathExplainerData,
  ShockSimulationInput,
  ShockSimulationResult,
  SystemHealthData,
} from "@supply-risk/shared-types";

export interface SupplyRiskApiClientOptions {
  baseUrl?: string;
  fetcher?: typeof fetch;
}

export interface SupplyRiskApiClient {
  readonly mode: ApiMode;
  getGlobalRiskCockpit(): Promise<ApiResult<GlobalRiskCockpitData>>;
  getGraphExplorer(): Promise<ApiResult<GraphExplorerData>>;
  getCompanyRisk360(): Promise<ApiResult<CompanyRisk360Data>>;
  getPathExplainer(): Promise<ApiResult<PathExplainerData>>;
  runShockSimulation(input: ShockSimulationInput): Promise<ApiResult<ShockSimulationResult>>;
  getCausalEvidenceBoard(): Promise<ApiResult<CausalEvidenceBoardData>>;
  getGraphVersionStudio(): Promise<ApiResult<GraphVersionStudioData>>;
  getSystemHealthCenter(): Promise<ApiResult<SystemHealthData>>;
}

export interface SupplyRiskDashboardData {
  globalRiskCockpit: GlobalRiskCockpitData;
  graphExplorer: GraphExplorerData;
  companyRisk360: CompanyRisk360Data;
  pathExplainer: PathExplainerData;
  causalEvidenceBoard: CausalEvidenceBoardData;
  graphVersionStudio: GraphVersionStudioData;
  systemHealthCenter: SystemHealthData;
}

interface RequestJsonOptions {
  fetcher: typeof fetch;
  setEffectiveMode: (mode: ApiMode) => void;
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

  try {
    const response = await options.fetcher(`${baseUrl.replace(/\/$/, "")}${endpoint}`, {
      headers: { "content-type": "application/json" },
      ...init,
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
    const message = error instanceof Error ? error.message : "Dashboard API request failed.";
    return createUnavailableResult(endpoint, sourceStatus, message, error);
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

export function createSupplyRiskApiClient(options: SupplyRiskApiClientOptions = {}): SupplyRiskApiClient {
  const baseUrl = options.baseUrl?.trim();
  let effectiveMode: ApiMode = "real";
  const setEffectiveMode = (mode: ApiMode) => {
    effectiveMode = mode;
  };
  const clientOptions = {
    fetcher: options.fetcher ?? ((input, init) => globalThis.fetch(input, init)),
    setEffectiveMode,
  };

  return {
    get mode() {
      return effectiveMode;
    },
    getGlobalRiskCockpit: () => requestJson(baseUrl, "/dashboard/global-risk-cockpit", undefined, clientOptions),
    getGraphExplorer: () => requestJson(baseUrl, "/dashboard/graph-explorer", undefined, clientOptions),
    getCompanyRisk360: () => requestJson(baseUrl, "/dashboard/company-risk-360", undefined, clientOptions),
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
  };
}
