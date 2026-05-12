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
  warnings: string[];
  sourceRegistryReadiness?: SourceRegistryReadiness;
}

export interface SourceRegistryReadiness {
  registry_version: string;
  generated_at: string;
  status: "ready" | "degraded" | "unavailable" | string;
  source_count: number;
  enabled_count: number;
  disabled_count: number;
  unavailable_count: number;
  connector_status_counts: Record<string, number>;
  license_status_counts: Record<string, number>;
  warnings: string[];
  sources: Array<{
    source_id: string;
    publisher: string;
    runtime_status: string;
    connector_status: string;
    license_terms_status: string;
    terms_url: string;
    source_url: string;
    freshness_sla_hours: number;
    review_status: string;
    owner: string;
  }>;
}

export interface SystemHealthData {
  services: ServiceHealth[];
  stages: PipelineStage[];
  logs: string[];
  sourceRegistry: SourceRegistrySummary;
  entityResolution: EntityResolutionSummary;
  evidenceLineage: EvidenceLineageSummary;
  dataCatalog?: DataCatalogSummary;
  semiconductorGraph?: SemiconductorGraphHealth;
  sourceRegistryReadiness?: SourceRegistryReadiness;
}
