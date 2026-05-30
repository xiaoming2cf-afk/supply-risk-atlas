const ACRONYMS = new Map<string, string>([
  ["api", "API"],
  ["cvar", "CVaR"],
  ["cvar95", "CVaR 95"],
  ["eda", "EDA"],
  ["euv", "EUV"],
  ["hhi", "HHI"],
  ["id", "ID"],
  ["ip", "IP"],
  ["p50", "P50"],
  ["p90", "P90"],
  ["p95", "P95"],
  ["roi", "ROI"],
  ["tsmc", "TSMC"],
]);

const LABEL_OVERRIDES = new Map<string, string>([
  ["affected_critical_nodes", "Affected critical nodes"],
  ["affected_mean", "Affected mean"],
  ["add_alternative_supplier", "Add alternative supplier"],
  ["add_policy_monitoring", "Add policy monitoring"],
  ["after_cvar95", "After CVaR 95"],
  ["after_expected_loss", "After expected loss"],
  ["after_run_count", "After run count"],
  ["after_simulation_run_ids", "After simulation run IDs"],
  ["baseline_comparison", "Baseline comparison"],
  ["baseline_run_ids", "Baseline run IDs"],
  ["beam_width", "Beam width"],
  ["additive_cap", "Capped cumulative spread"],
  ["auto_semiconductor", "Auto semiconductor propagation"],
  ["before_cvar95", "Before CVaR 95"],
  ["before_expected_loss", "Before expected loss"],
  ["before_run_count", "Before run count"],
  ["before_simulation_run_ids", "Before simulation run IDs"],
  ["capacity_functionality_loss", "Capacity functionality loss"],
  ["capacity_fulfillment", "Capacity fulfillment"],
  ["context_run_id", "Context run ID"],
  ["context_source", "Context source"],
  ["cvar_95", "CVaR 95"],
  ["cvar95_loss", "CVaR 95 loss"],
  ["data_mode", "Data mode"],
  ["default_fixture", "Default fixture"],
  ["deferred_not_allowed", "Deferred"],
  ["deferred_paid_or_proprietary", "Deferred paid/proprietary"],
  ["demand_fulfillment_loss", "Demand fulfillment loss"],
  ["deterministic_fixture_suite", "Deterministic fixture suite"],
  ["disabled_review_required", "Disabled pending review"],
  ["edge_count", "Edge count"],
  ["edgeCount", "Edge count"],
  ["enabled_fixture", "Enabled fixture"],
  ["evidence_ref_count", "Evidence ref count"],
  ["evidence_refs", "Evidence refs"],
  ["expected_effect", "Expected effect"],
  ["expected_loss", "Expected loss"],
  ["failed_endpoint", "Failed endpoint"],
  ["failure_threshold", "Failure threshold"],
  ["failure_threshold_input", "Failure threshold input"],
  ["failure_threshold_normalized", "Normalized failure threshold"],
  ["feature_version", "Feature version"],
  ["fixture_graph", "Fixture graph"],
  ["fixture_connector", "Fixture connector"],
  ["fixture_ready", "Fixture ready"],
  ["fixtureGraph", "Fixture graph"],
  ["fixtureGraphReady", "Fixture graph ready"],
  ["fixtureManifestReady", "Fixture manifest ready"],
  ["fixture_promoted_public_evidence", "Fixture/promoted public evidence"],
  ["formula_refs", "Formula refs"],
  ["formula_version", "Formula version"],
  ["forward_scenario", "Forward scenario"],
  ["graph_mode", "Graph mode"],
  ["graph_version", "Graph version"],
  ["graph_weighted_loss", "Graph-weighted loss"],
  ["heuristic_estimated_after_cvar95", "Estimated after CVaR 95"],
  ["heuristic_estimated_after_expected_loss", "Estimated after expected loss"],
  ["include_entity_risk", "Include entity risk"],
  ["include_forward_stress", "Include forward stress"],
  ["include_intervention_optimization", "Include intervention optimization"],
  ["include_reverse_stress", "Include reverse stress"],
  ["improve_recovery_rate", "Improve recovery rate"],
  ["increase_inventory_buffer", "Increase inventory buffer"],
  ["intervention_optimization", "Intervention optimization"],
  ["intervention_type", "Intervention type"],
  ["iterations_per_candidate", "Iterations per candidate"],
  ["investigation_report", "Investigation report"],
  ["latest_cvar_95", "Latest CVaR 95"],
  ["latest_expected_loss", "Latest expected loss"],
  ["latest_run_id", "Latest run ID"],
  ["likelihood_impact_vulnerability_framework", "Likelihood x impact x vulnerability framework"],
  ["leontief_bottleneck", "Bottleneck-limited spread"],
  ["literature_proxy_not_calibrated", "Literature proxy not calibrated"],
  ["loss_contribution", "Loss contribution"],
  ["loss_mode", "Loss mode"],
  ["loss_score", "Loss score"],
  ["max_combination_size", "Max shock set size"],
  ["max_combination_size_cap", "Max shock set size cap"],
  ["node_count", "Node count"],
  ["nodeCount", "Node count"],
  ["node_id", "Node ID"],
  ["node_type", "Node type"],
  ["noisy_or", "Independent exposure spread"],
  ["normalized_threshold", "Normalized threshold"],
  ["optimization_context_type", "Optimization context"],
  ["optimization_version", "Optimization version"],
  ["ontologyReady", "Ontology ready"],
  ["p50_loss", "P50 loss"],
  ["p90_loss", "P90 loss"],
  ["p95_loss", "P95 loss"],
  ["path_id", "Path ID"],
  ["plausibility_cost", "Plausibility cost"],
  ["previous_cvar_95", "Previous CVaR 95"],
  ["previous_expected_loss", "Previous expected loss"],
  ["previous_run_id", "Previous run ID"],
  ["private_diagnostics_excluded", "Private diagnostics excluded"],
  ["not_weighted_sum", "Not weighted"],
  ["propagation_mode", "Propagation mode"],
  ["public_evidence_graph", "Public evidence graph"],
  ["public_evidence_promoted", "Public evidence promoted"],
  ["qualify_backup_material", "Qualify backup material"],
  ["raw_payload_excluded", "Raw payload excluded"],
  ["registryReady", "Registry ready"],
  ["regional_diversification", "Regional diversification"],
  ["report_id", "Report ID"],
  ["report_version", "Report version"],
  ["resilience_integral_loss", "Resilience integral loss"],
  ["resilience_roi", "Resilience ROI"],
  ["reverse_stress", "Reverse stress"],
  ["risk_scoring_method", "Risk scoring method"],
  ["route_redundancy", "Route redundancy"],
  ["run_id", "Run ID"],
  ["scenario_count", "Scenario count"],
  ["scenario_type", "Scenario type"],
  ["scoring_method", "Scoring method"],
  ["source_concentration_hhi", "Source concentration HHI"],
  ["source_concentration_level", "Source concentration level"],
  ["selected_run_refs", "Selected run refs"],
  ["shock_set_id", "Shock set ID"],
  ["simulation_version", "Simulation version"],
  ["source_manifest_id", "Source manifest ID"],
  ["source_status", "Source status"],
  ["unavailable_terms_review", "Unavailable pending terms review"],
  ["api_commit_reported", "API commit reported"],
  ["country_concentration_hhi", "Country concentration HHI"],
  ["country_concentration_level", "Country concentration level"],
  ["staleSourceCount", "Stale source count"],
  ["target_id", "Target ID"],
  ["target_metric", "Target metric"],
  ["threshold_metric_basis", "Threshold metric basis"],
  ["time_to_recover_days", "Time to recover"],
  ["time_to_survive_days", "Time to survive"],
  ["unresolvedEntityCount", "Unresolved entity count"],
  ["vulnerability_modifier", "Vulnerability modifier"],
  ["weighting_method", "Weighting method"],
]);

export function formatDisplayLabel(label: string) {
  const trimmed = label.trim();
  if (!trimmed) return trimmed;
  const override = LABEL_OVERRIDES.get(trimmed);
  if (override) return override;
  if (/\s/.test(trimmed)) return trimmed;

  const normalized = trimmed
    .replace(/[-_]+/g, " ")
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1 $2");

  if (normalized === trimmed && !trimmed.includes(" ")) {
    const lower = trimmed.toLowerCase();
    const acronym = ACRONYMS.get(lower);
    if (acronym) return acronym;
    if (/^[a-z][a-z0-9]*$/.test(trimmed)) return capitalize(lower);
    return trimmed;
  }

  return normalized
    .split(/\s+/)
    .filter(Boolean)
    .map((part, index) => {
      const lower = part.toLowerCase();
      const acronym = ACRONYMS.get(lower);
      if (acronym) return acronym;
      if (index === 0) return capitalize(lower);
      return lower;
    })
    .join(" ");
}

export function formatDisplayValue(value: string): string;
export function formatDisplayValue<T>(value: T): T;
export function formatDisplayValue(value: unknown) {
  if (typeof value !== "string") return value;
  const trimmed = value.trim();
  if (!trimmed || !trimmed.includes("_")) return value;
  return LABEL_OVERRIDES.get(trimmed) ?? value;
}

function capitalize(value: string) {
  return value ? `${value[0].toUpperCase()}${value.slice(1)}` : value;
}
