export interface SemiconductorCoverageCounts {
  country_region_count: number;
  value_chain_layer_count: number;
  entity_profile_count: number;
  relationship_edge_count: number;
  chokepoint_count: number;
  source_family_count: number;
}

export interface SemiconductorCountryExposure {
  geo_id: string;
  display_name: string;
  parent_country_id?: string;
  parent_country_display?: string;
  region_group: string;
  semiconductor_role_summary: string;
  upstream_strengths: string[];
  midstream_strengths: string[];
  downstream_strengths: string[];
  chokepoint_exposure: string[];
  policy_exposure: string[];
  logistics_exposure: string[];
  substitution_notes: string;
  evidence_summary: string;
  coverage_level: string;
  provenance: string[];
}

export interface SemiconductorValueChainLayer {
  layer_id: string;
  layer_name: string;
  stage: "upstream" | "midstream" | "downstream" | "support" | string;
  role_in_chain: string;
  key_inputs: string[];
  key_outputs: string[];
  representative_entities: string[];
  concentration_risk: string;
  substitutability: string;
  lead_time_or_switching_cost_notes: string;
  shock_sensitivity: string;
  downstream_impact: string;
  evidence_summary: string;
  coverage_level: string;
  provenance: string[];
}

export interface SemiconductorEntityProfile {
  entity_id: string;
  name: string;
  entity_type: string;
  headquarters_country: string;
  value_chain_roles: string[];
  primary_layers: string[];
  risk_tags: string[];
  dependency_tags: string[];
  substitution_notes: string;
  evidence_summary: string;
  coverage_level: string;
  provenance: string[];
}

export interface SemiconductorChokepoint {
  chokepoint_id: string;
  layer_id: string;
  title: string;
  countries_regions: string[];
  representative_entities: string[];
  substitutability: string;
  shock_sensitivity: string;
  downstream_impact: string;
  evidence_summary: string;
  provenance: string[];
}

export interface SemiconductorRelationship {
  source_id: string;
  source_node_id: string;
  target_id: string;
  target_node_id: string;
  relationship_type: string;
  relationship_class: "SUPPLY_RELATIONSHIP" | "DEMAND_RELATIONSHIP" | "PRODUCTION_DEPENDENCY" | "EVIDENCE_CONTEXT" | string;
  edge_type: string;
  confidence: string;
  rationale: string;
  evidence_summary: string;
  provenance: string[];
  source_refs: string[];
  evidence_refs: string[];
  valid_from: string;
  valid_to: string | null;
  calibration_status: string;
  source_families: string[];
  stage_context: string[];
  can_propagate_risk: boolean;
}

export interface SemiconductorStageSourceCoverage {
  layer_id: string;
  layer_name: string;
  stage: string;
  coverage_level: string;
  source_refs: string[];
  source_families: string[];
  relationship_classes: string[];
  relationship_count: number;
  entity_count: number;
  chokepoint_count: number;
  relationship_coverage: {
    supply: boolean;
    demand: boolean;
    production_dependency: boolean;
    evidence_context: boolean;
  };
  source_gaps: string[];
  connector_status: string;
  live_fetch_default: "disabled" | string;
  fixture_required: boolean;
}

export interface SemiconductorContentBase {
  content_scope: string;
  content_version: string;
  graph_version: string;
  source_manifest_id: string;
  data_mode: string;
  graph_mode: string;
  source_status: string;
  calibration_status: string;
  last_updated: string;
  fixture_required: boolean;
  live_fetch_default: "disabled" | string;
  warnings: string[];
  audit: Record<string, unknown>;
}

export interface SemiconductorCoverageOverview extends SemiconductorContentBase {
  coverage_counts: SemiconductorCoverageCounts;
  source_family_counts: Record<string, number>;
  source_summaries: Record<string, unknown>;
  coverage_gaps: string[];
  representative_country_region_exposures: SemiconductorCountryExposure[];
  representative_value_chain_layers: SemiconductorValueChainLayer[];
  representative_entities: SemiconductorEntityProfile[];
  representative_chokepoints: SemiconductorChokepoint[];
}

export interface SemiconductorValueChainLayersData extends SemiconductorContentBase {
  filters: Record<string, string | null>;
  total: number;
  layers: SemiconductorValueChainLayer[];
}

export interface SemiconductorCountryExposuresData extends SemiconductorContentBase {
  filters: Record<string, string | null>;
  total: number;
  country_region_exposures: SemiconductorCountryExposure[];
}

export interface SemiconductorEntityProfilesData extends SemiconductorContentBase {
  filters: Record<string, string | null>;
  total: number;
  entity_profiles: SemiconductorEntityProfile[];
}

export interface SemiconductorChokepointsData extends SemiconductorContentBase {
  filters: Record<string, string | null>;
  total: number;
  chokepoints: SemiconductorChokepoint[];
}

export interface SemiconductorRelationshipsData extends SemiconductorContentBase {
  filters: Record<string, string | null>;
  total: number;
  relationship_class_counts: Record<string, number>;
  relationships: SemiconductorRelationship[];
}

export interface SemiconductorSourceCoverageData extends SemiconductorContentBase {
  filters: Record<string, string | null>;
  total: number;
  source_family_counts: Record<string, number>;
  relationship_class_counts: Record<string, number>;
  source_families: Record<string, unknown>;
  coverage_gaps: string[];
  stage_source_coverage: SemiconductorStageSourceCoverage[];
}
