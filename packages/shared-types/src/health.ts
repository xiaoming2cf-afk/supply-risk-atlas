export interface ServiceHealth {
  id: string;
  service: string;
  owner: string;
  status: "operational" | "degraded" | "down";
  latencyMs: number;
  freshnessMinutes: number;
  errorRate: number;
}

export interface PipelineStage {
  id: string;
  label: string;
  status: "complete" | "running" | "queued" | "blocked";
  processed: number;
  total: number;
}

export interface SourceRegistryRow {
  id: string;
  name: string;
  type: string;
  license: string;
  updateFrequency: string;
  reliabilityScore: number;
  owner: string;
  status: "fresh" | "stale" | "partial" | "unavailable";
  recordCount: number;
  maxStaleMinutes: number;
  checksum: string;
  latestRecordTime: string | null;
}

export interface SourceRegistrySummary {
  manifestRef: string;
  checksum: string;
  asOfTime: string;
  catalogSource?: string;
  promotedGraph?: {
    status: "promoted" | "partial";
    manifest: Record<string, unknown> | null;
  };
  sourceCount: number;
  rawRecordCount: number;
  silverEntityCount: number;
  silverEventCount: number;
  goldEdgeEventCount: number;
  dataNodeCount?: number;
  sources: SourceRegistryRow[];
}

export interface SourceRegistryReadiness {
  registry_version: string;
  generated_at: string | null;
  status: "ready" | "degraded" | "unavailable";
  source_count: number;
  enabled_count: number;
  disabled_count: number;
  live_default_count: number;
  terms_review_count: number;
  deferred_count: number;
  source_status_counts: Record<string, number>;
  connector_status_counts: Record<string, number>;
  source_tier_counts: Record<string, number>;
  sources: Array<{
    source_id: string;
    publisher: string;
    source_tier: string;
    data_category: string;
    enabled_by_default: boolean;
    live_fetch_default: boolean;
    status: string;
    connector_status: string;
    license_policy: {
      api_visible_summary_allowed: boolean;
      payload_storage_allowed: boolean;
      redistribution_allowed: boolean;
      attribution_required: boolean;
      terms_review_required: boolean;
      manual_review_note: string;
    };
  } & Record<string, unknown>>;
  warnings: string[];
}

export interface EntityResolutionSummary {
  totalEntities: number;
  averageConfidence: number;
  byEntityType: Array<{
    entityType: string;
    count: number;
  }>;
  bySource: Array<{
    sourceId: string;
    entityCount: number;
  }>;
}

export interface EvidenceLineageRecord {
  id: string;
  sourceId: string;
  sourceName: string;
  rawId: string;
  sourceRecordId: string;
  rawChecksum: string;
  rawObservedTime: string;
  silverEventIds: string[];
  silverEntityIds: string[];
  goldEdgeEventIds: string[];
  edgeTypes: string[];
  targetEntities: string[];
  confidence: number;
}

export interface EvidenceLineageSummary {
  manifestRef: string;
  checksum: string;
  asOfTime: string;
  rawRecordCount: number;
  silverEventCount: number;
  goldEdgeEventCount: number;
  records: EvidenceLineageRecord[];
}

export interface DataCatalogSummary {
  catalogSource: string;
  promoted: boolean;
  totalDataNodes: number;
  byType: Array<{
    entityType: string;
    count: number;
  }>;
  bySource: Array<{
    sourceId: string;
    count: number;
  }>;
  licensePolicies: Array<{
    id: string;
    name: string;
    sourceIds: string[];
    licenseUrl: string;
  }>;
  topNodes: Array<{
    id: string;
    name: string;
    entityType: string;
    sourceIds: string[];
    confidence: number;
  }>;
}

export interface SemiconductorGraphHealth {
  label: string;
  status: "ready" | "degraded" | "unavailable";
  fixtureGraph: boolean;
  registryReady: boolean;
  ontologyReady: boolean;
  fixtureManifestReady: boolean;
  fixtureGraphReady: boolean;
  graphVersion: string;
  ontologyVersion: string;
  sourceManifestId: string;
  asOfTime: string;
  nodeCount: number;
  edgeCount: number;
  nodeCountByType: Record<string, number>;
  edgeCountByType: Record<string, number>;
  missingProvenanceCount: number;
  unresolvedEntityCount: number;
  staleSourceCount: number;
  dataMode?: "fixture" | "promoted" | "live_disabled" | "live_enabled" | string;
  graphMode?: "fixture" | "promoted" | string;
  productionStatus?: "not_production_ready" | "research_fixture" | "public_evidence_promoted" | string;
  notProductionReady?: boolean;
  calibrationStatus?: string;
  warnings: string[];
}

export interface PlatformStatus {
  apiReadiness: string;
  graphReadiness: string;
  sourceRegistryReadiness: string;
  connectorReadiness: string;
  storageReadiness: {
    status: string;
    storageMode: "memory" | "sqlite" | string;
    pathRedacted: boolean;
    path: "redacted" | string;
  };
  modelReadiness: string;
  deploymentVersionReadiness: {
    status: string;
    apiVersion: string;
    webVersion: string;
    warnings: string[];
  };
  dataMode: "fixture" | "promoted" | "live_disabled" | "live_enabled" | string;
  graphMode: "fixture" | "promoted" | string;
  productionStatus: "not_production_ready" | "research_fixture" | "public_evidence_promoted" | string;
  notProductionReady: boolean;
  calibrationStatus: string[];
  sourceManifestId: string;
  graphVersion: string;
  connectorStatusCounts: Record<string, number>;
  sourceStatusCounts: Record<string, number>;
  sourceCount: number;
  enabledSourceCount: number;
  liveDefaultCount: number;
  warnings: string[];
}

export interface SystemHealthData {
  services: ServiceHealth[];
  stages: PipelineStage[];
  logs: string[];
  sourceRegistry: SourceRegistrySummary;
  sourceRegistryReadiness?: SourceRegistryReadiness;
  entityResolution: EntityResolutionSummary;
  evidenceLineage: EvidenceLineageSummary;
  dataCatalog?: DataCatalogSummary;
  semiconductorGraph?: SemiconductorGraphHealth;
  platformStatus?: PlatformStatus;
}
