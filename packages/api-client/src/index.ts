import type {
  ApiEnvelope,
  Entity,
  GraphSnapshotPayload,
  Prediction,
  SimulationResult,
} from "@supply-risk/shared-types";

export interface SupplyRiskClient {
  health(): Promise<ApiEnvelope<Record<string, unknown>>>;
  entities(): Promise<ApiEnvelope<Entity[]>>;
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

export function createSupplyRiskClient(baseUrl = "http://127.0.0.1:8000"): SupplyRiskClient {
  return {
    health: () => request(baseUrl, "/api/v1/health"),
    entities: () => request(baseUrl, "/api/v1/entities"),
    graphSnapshot: () => request(baseUrl, "/api/v1/graph/snapshots"),
    predictions: () => request(baseUrl, "/api/v1/predictions"),
    simulations: () => request(baseUrl, "/api/v1/simulations"),
    reports: () => request(baseUrl, "/api/v1/reports"),
  };
}

export * from "./dashboard";
