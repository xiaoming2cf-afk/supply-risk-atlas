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
