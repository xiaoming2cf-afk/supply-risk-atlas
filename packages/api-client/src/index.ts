import type {
  ApiEnvelope,
  Entity,
  EvidenceLineageSummary,
  GraphExplorerData,
  GraphExplorerQuery,
  GraphSnapshotPayload,
  InvestigationReportData,
  InvestigationReportInput,
  Prediction,
  SemiriskEntityRiskScore,
  SemiriskRiskPortfolioData,
  SimulationResult,
  SourceRegistrySummary,
} from "@supply-risk/shared-types";

export interface SupplyRiskClient {
  health(): Promise<ApiEnvelope<Record<string, unknown>>>;
  entities(options?: { entityType?: string; query?: string; limit?: number; offset?: number }): Promise<ApiEnvelope<Entity[]>>;
  sources(sourceId?: string): Promise<ApiEnvelope<SourceRegistrySummary>>;
  lineage(options?: { sourceId?: string; targetId?: string }): Promise<ApiEnvelope<EvidenceLineageSummary>>;
  graphSnapshot(): Promise<ApiEnvelope<GraphSnapshotPayload>>;
  graphExplorer(options?: GraphExplorerQuery): Promise<ApiEnvelope<GraphExplorerData>>;
  countryLens(options?: Pick<GraphExplorerQuery, "countryCode" | "provinceCode" | "geoId">): Promise<ApiEnvelope<GraphExplorerData>>;
  predictions(): Promise<ApiEnvelope<Prediction[]>>;
  simulations(): Promise<ApiEnvelope<SimulationResult>>;
  reports(): Promise<ApiEnvelope<Record<string, unknown>>>;
  investigationReport(input: InvestigationReportInput): Promise<ApiEnvelope<InvestigationReportData>>;
  semiriskEntityRisk(entityId: string): Promise<ApiEnvelope<SemiriskEntityRiskScore>>;
  semiriskRiskPortfolio(options?: { nodeType?: string | null; limit?: number }): Promise<ApiEnvelope<SemiriskRiskPortfolioData>>;
}

async function request<T>(baseUrl: string, path: string): Promise<ApiEnvelope<T>> {
  const response = await fetch(`${baseUrl}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as ApiEnvelope<T>;
}

async function post<T>(baseUrl: string, path: string, body: unknown): Promise<ApiEnvelope<T>> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as ApiEnvelope<T>;
}

function queryString(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}

export function createSupplyRiskClient(baseUrl = "http://127.0.0.1:8000"): SupplyRiskClient {
  return {
    health: () => request(baseUrl, "/api/v1/health"),
    entities: (options) =>
      request(
        baseUrl,
        `/api/v1/entities${queryString({
          entity_type: options?.entityType,
          q: options?.query,
          limit: options?.limit,
          offset: options?.offset,
        })}`,
      ),
    sources: (sourceId) =>
      request(baseUrl, sourceId ? `/api/v1/sources/${encodeURIComponent(sourceId)}` : "/api/v1/sources"),
    lineage: (options) =>
      request(
        baseUrl,
        `/api/v1/lineage${queryString({
          source_id: options?.sourceId,
          target_id: options?.targetId,
        })}`,
      ),
    graphSnapshot: () => request(baseUrl, "/api/v1/graph/snapshots"),
    graphExplorer: (options) =>
      request(
        baseUrl,
        `/api/v1/dashboard/graph-explorer${queryString({
          selected_node_id: options?.selectedNodeId,
          path_direction: options?.pathDirection,
          country_code: options?.countryCode ?? undefined,
          province_code: options?.provinceCode ?? undefined,
          geo_id: options?.geoId ?? undefined,
          node_kinds: options?.nodeKinds?.join(","),
          edge_types: options?.edgeTypes?.join(","),
        })}`,
      ),
    countryLens: (options) =>
      request(
        baseUrl,
        `/api/v1/dashboard/country-lens${queryString({
          country_code: options?.countryCode ?? undefined,
          province_code: options?.provinceCode ?? undefined,
          geo_id: options?.geoId ?? undefined,
        })}`,
      ),
    predictions: () => request(baseUrl, "/api/v1/predictions"),
    simulations: () => request(baseUrl, "/api/v1/simulations"),
    reports: () => request(baseUrl, "/api/v1/reports"),
    investigationReport: (input) => post(baseUrl, "/api/v1/reports/investigation", input),
    semiriskEntityRisk: (entityId) =>
      request(baseUrl, `/api/v1/risk/entities/${encodeURIComponent(entityId)}`),
    semiriskRiskPortfolio: (options) =>
      request(
        baseUrl,
        `/api/v1/risk/portfolio${queryString({
          node_type: options?.nodeType ?? undefined,
          limit: options?.limit,
        })}`,
      ),
  };
}

export * from "./dashboard";
