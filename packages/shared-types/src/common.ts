export type ApiStatus = "success" | "error";

export type ApiMode = "real";

export type ApiSourceStatus = "fresh" | "stale" | "partial" | "unavailable" | "unauthorized" | "fallback" | "error";

export interface VersionMetadata {
  graph_version: string;
  feature_version: string;
  label_version: string;
  model_version: string;
  as_of_time: string;
  audit_ref?: string | null;
  lineage_ref?: string | null;
  data_mode?: "real";
  freshness_status?: "fresh" | "stale" | "partial" | "unavailable";
  source_count?: number;
  source_manifest_ref?: string | null;
}

export interface ApiError {
  code: string;
  message: string;
  field?: string | null;
}

export interface ApiEnvelope<T> {
  request_id: string;
  status: ApiStatus;
  data: T | null;
  metadata: VersionMetadata;
  warnings: string[];
  errors: ApiError[];
  mode?: ApiMode;
  source_status?: ApiSourceStatus;
  source?: {
    name?: string;
    url?: string;
    lineage_ref?: string | null;
    license?: string | null;
  };
}

export interface ApiResult<T> {
  data: T | null;
  envelope: ApiEnvelope<T>;
  mode: ApiMode;
  sourceStatus: ApiSourceStatus;
  receivedAt: string;
  httpStatus?: number;
}

export interface Entity {
  canonical_id: string;
  entity_type: string;
  display_name: string;
  country?: string | null;
  industry?: string | null;
  external_ids?: Record<string, string>;
  confidence: number;
  geoId?: string;
  geoLevel?: "country" | "province" | "region" | "aggregate" | "unknown" | string;
  countryCode?: string;
  provinceCode?: string | null;
  parentGeoId?: string | null;
  sourceCountryCode?: string | null;
  displayName?: string;
}

export type RiskLevel = "low" | "guarded" | "elevated" | "severe" | "critical";

export type TrendDirection = "up" | "down" | "flat";
