import type {
  ApiEnvelope,
  Entity,
  EvidenceLineageSummary,
  GraphSnapshotPayload,
  Prediction,
  SimulationResult,
  SourceRegistrySummary,
} from "@supply-risk/shared-types";

export interface SupplyRiskClient {
  health(): Promise<ApiEnvelope<Record<string, unknown>>>;
  entities(options?: { entityType?: string; query?: string; limit?: number; offset?: number }): Promise<ApiEnvelope<Entity[]>>;
  sources(sourceId?: string): Promise<ApiEnvelope<SourceRegistrySummary>>;
  lineage(options?: { sourceId?: string; targetId?: string }): Promise<ApiEnvelope<EvidenceLineageSummary>>;
  graphSnapshot(): Promise<ApiEnvelope<GraphSnapshotPayload>>;
  predictions(): Promise<ApiEnvelope<Prediction[]>>;
  simulations(): Promise<ApiEnvelope<SimulationResult>>;
  reports(): Promise<ApiEnvelope<Record<string, unknown>>>;
}

async function request<T>(baseUrl: string, path: string): Promise<ApiEnvelope<T>> {
  const response = await fetch(`${baseUrl}${path}`);
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
    predictions: () => request(baseUrl, "/api/v1/predictions"),
    simulations: () => request(baseUrl, "/api/v1/simulations"),
    reports: () => request(baseUrl, "/api/v1/reports"),
  };
}

export * from "./dashboard";
