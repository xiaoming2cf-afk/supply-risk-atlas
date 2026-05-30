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
  ["cheapest_first", "Cheapest first"],
  ["context_run_id", "Context run ID"],
  ["context_source", "Context source"],
  ["context_status", "Context status"],
  ["cvar_95", "CVaR 95"],
  ["cvar95_loss", "CVaR 95 loss"],
  ["data_mode", "Data mode"],
  ["default_fixture", "Default fixture"],
  ["DEMAND_RELATIONSHIP", "Demand relationship"],
  ["deferred_not_allowed", "Deferred"],
  ["depends_on", "Depends on"],
  ["deferred_paid_or_proprietary", "Deferred paid/proprietary"],
  ["demand_fulfillment_loss", "Demand fulfillment loss"],
  ["demand_signal_for", "Demand signal for"],
  ["demand_shock_on", "Demand shock on"],
  ["demands", "Demands"],
  ["deterministic_fixture_suite", "Deterministic fixture suite"],
  ["disabled_review_required", "Disabled pending review"],
  ["edge_count", "Edge count"],
  ["edgeCount", "Edge count"],
  ["enabled_fixture", "Enabled fixture"],
  ["evidence_ref_count", "Evidence ref count"],
  ["evidence_refs", "Evidence refs"],
  ["EVIDENCE_CONTEXT", "Evidence context"],
  ["evidence_context_link", "Evidence-context link"],
  ["exposed_to_hazard", "Exposed to hazard"],
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
  ["forward_context", "Forward context"],
  ["forward_scenario", "Forward scenario"],
  ["graph_mode", "Graph mode"],
  ["graph_version", "Graph version"],
  ["graph_weighted_loss", "Graph-weighted loss"],
  ["heuristic_estimated_after_cvar95", "Estimated after CVaR 95"],
  ["heuristic_estimated_after_expected_loss", "Estimated after expected loss"],
  ["highest_risk_score_protection", "Highest-risk protection"],
  ["include_entity_risk", "Include entity risk"],
  ["include_forward_stress", "Include forward stress"],
  ["include_intervention_optimization", "Include intervention optimization"],
  ["include_reverse_stress", "Include reverse stress"],
  ["improve_recovery_rate", "Improve recovery rate"],
  ["increase_inventory_buffer", "Increase inventory buffer"],
  ["impacted_by", "Impacted by"],
  ["intervention_optimization", "Intervention optimization"],
  ["intervention_type", "Intervention type"],
  ["iterations_per_candidate", "Iterations per candidate"],
  ["investigation_report", "Investigation report"],
  ["L0_policy_macro", "L0 policy / macro"],
  ["L1_raw_minerals", "L1 critical minerals / raw materials"],
  ["L2_materials_chemicals", "L2 semiconductor materials / chemicals"],
  ["L3_design_eda_ip", "L3 design / EDA / IP"],
  ["L4_equipment", "L4 equipment"],
  ["L5_fabrication", "L5 fabrication / front-end process"],
  ["L6_products", "L6 products / chip types"],
  ["L7_packaging_testing", "L7 packaging / testing"],
  ["L8_logistics", "L8 logistics / ports / routes"],
  ["L9_downstream_demand", "L9 downstream demand"],
  ["L10_risk_events", "L10 risk events"],
  ["L11_compliance", "L11 compliance"],
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
  ["manufactured_by", "Manufactured by"],
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
  ["packaged_by", "Packaged by"],
  ["path_id", "Path ID"],
  ["plausibility_cost", "Plausibility cost"],
  ["previous_cvar_95", "Previous CVaR 95"],
  ["previous_expected_loss", "Previous expected loss"],
  ["previous_run_id", "Previous run ID"],
  ["proposed_risk_adjusted_greedy_optimizer", "Proposed risk-adjusted optimizer"],
  ["private_diagnostics_excluded", "Private diagnostics excluded"],
  ["PRODUCTION_DEPENDENCY", "Production dependency"],
  ["provides_capacity", "Provides capacity"],
  ["provides_chemical", "Provides chemical"],
  ["provides_equipment", "Provides equipment"],
  ["provides_ip", "Provides IP"],
  ["provides_material", "Provides material"],
  ["provides_service", "Provides service"],
  ["not_weighted_sum", "Not weighted"],
  ["propagation_mode", "Propagation mode"],
  ["public_evidence_graph", "Public evidence graph"],
  ["public_evidence_promoted", "Public evidence promoted"],
  ["qualify_backup_material", "Qualify backup material"],
  ["random_intervention", "Random intervention"],
  ["raw_payload_excluded", "Raw payload excluded"],
  ["registryReady", "Registry ready"],
  ["regional_diversification", "Regional diversification"],
  ["report_id", "Report ID"],
  ["report_version", "Report version"],
  ["requires", "Requires"],
  ["resilience_integral_loss", "Resilience integral loss"],
  ["resilience_roi", "Resilience ROI"],
  ["reverse_context", "Reverse context"],
  ["reverse_stress", "Reverse stress"],
  ["restricted_by", "Restricted by"],
  ["risk_scoring_method", "Risk scoring method"],
  ["route_redundancy", "Route redundancy"],
  ["routes_through", "Routes through"],
  ["run_id", "Run ID"],
  ["scenario_count", "Scenario count"],
  ["scenario_type", "Scenario type"],
  ["scoring_method", "Scoring method"],
  ["source_concentration_hhi", "Source concentration HHI"],
  ["source_concentration_level", "Source concentration level"],
  ["selected_run_refs", "Selected run refs"],
  ["selected_runs", "Selected runs"],
  ["shock_set_id", "Shock set ID"],
  ["simulation_version", "Simulation version"],
  ["source_manifest_id", "Source manifest ID"],
  ["source_status", "Source status"],
  ["supplies", "Supplies"],
  ["supplies_item", "Supplies item"],
  ["SUPPLY_DEMAND_BALANCE", "Supply-demand balance"],
  ["SUPPLY_RELATIONSHIP", "Supply relationship"],
  ["tested_by", "Tested by"],
  ["used_in_downstream_sector", "Used in downstream sector"],
  ["uses_chemical", "Uses chemical"],
  ["uses_equipment", "Uses equipment"],
  ["uses_ip", "Uses IP"],
  ["uses_material", "Uses material"],
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

const NODE_LABEL_OVERRIDES = new Map<string, string>([
  ["region:china_taiwan", "中国台湾"],
  ["country:CN", "中国"],
  ["country:US", "United States"],
  ["country:KR", "South Korea"],
  ["country:JP", "Japan"],
  ["country:NL", "Netherlands"],
  ["country:DE", "Germany"],
  ["country:SG", "Singapore"],
  ["country:MY", "Malaysia"],
  ["country:VN", "Vietnam"],
  ["company:TSMC", "TSMC"],
  ["company:NVIDIA", "NVIDIA"],
  ["company:AMD", "AMD"],
  ["company:ASML", "ASML"],
  ["company:Applied_Materials", "Applied Materials"],
  ["company:Lam_Research", "Lam Research"],
  ["company:Tokyo_Electron", "Tokyo Electron"],
  ["company:Samsung_Foundry", "Samsung Foundry"],
  ["company:Intel_Foundry", "Intel Foundry"],
  ["company:SMIC", "SMIC"],
  ["company:UMC", "UMC"],
  ["fab:TSMC_Fab_18", "TSMC Fab 18"],
  ["equipment:EUV_scanner", "EUV scanner"],
  ["equipment:DUV_scanner", "DUV scanner"],
  ["product:AI_accelerator", "AI accelerator"],
  ["product:HBM", "HBM"],
  ["product:DRAM", "DRAM"],
  ["product:NAND", "NAND"],
  ["process:CMP", "CMP"],
  ["technology_node:3nm", "3 nm"],
  ["technology_node:5nm", "5 nm"],
  ["technology_node:7nm", "7 nm"],
  ["technology_node:28nm", "28 nm"],
]);

const SOURCE_LABEL_OVERRIDES = new Map<string, string>([
  ["national_policy_macro_public", "National, policy, macro public sources"],
  ["enterprise_public_disclosure", "Enterprise public disclosures"],
  ["industry_public_fixture", "Industry public fixture sources"],
  ["eto_cset_advanced_semiconductor_supply_chain", "ETO/CSET semiconductor supply chain"],
  ["oecd_semiconductor_value_chain_reports", "OECD semiconductor value chain reports"],
  ["wsts_historical_billings", "WSTS billings"],
  ["sec_edgar_lite", "SEC EDGAR public filings"],
  ["gdelt_semiconductor_lite", "GDELT semiconductor events"],
  ["un_comtrade_semiconductor_trade_lite", "UN Comtrade semiconductor trade"],
  ["wits_trade_tariff_lite", "WITS trade and tariff indicators"],
  ["usgs_mineral_commodity_summaries_lite", "USGS mineral summaries"],
  ["usgs_earthquake_lite", "USGS earthquake events"],
  ["nga_world_port_index_lite", "NGA World Port Index"],
  ["ofac_sanctions_list_lite", "OFAC sanctions list"],
  ["consolidated_screening_list_lite", "Consolidated Screening List"],
  ["bis_export_controls_lite", "BIS export controls"],
  ["federal_register_export_controls_lite", "Federal Register export controls"],
  ["company_annual_report_manual_upload", "Company annual reports"],
  ["openalex_crossref_literature_lite", "OpenAlex/Crossref literature"],
  ["world_bank_macro_indicators_lite", "World Bank macro indicators"],
  ["public_source_manifest", "Public source manifest"],
  ["public evidence source", "Public evidence source"],
  ["source_ref", "Evidence source"],
  ["fixture_source", "Fixture evidence source"],
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
  if (!trimmed) return value;
  return LABEL_OVERRIDES.get(trimmed) || formatSourceDisplayRef(trimmed) || formatNodeDisplayRef(trimmed) || value;
}

export function formatNodeDisplayRef(value?: string | null) {
  const trimmed = value?.trim();
  if (!trimmed) return "";
  const override = NODE_LABEL_OVERRIDES.get(trimmed);
  if (override) return override;

  const [prefix, ...tailParts] = trimmed.split(":");
  if (tailParts.length === 0) return "";
  if (!isKnownNodePrefix(prefix)) return "";
  const tail = tailParts.join(":");

  if (prefix === "region" && tail === "china_taiwan") return "中国台湾";
  if (prefix === "country" && tail === "CN") return "中国";
  return formatDisplayLabel(tail);
}

export function formatSourceDisplayRef(value?: string | null) {
  const trimmed = value?.trim();
  if (!trimmed) return "";
  const clean = trimmed.replace(/^source:/, "");
  const firstPart = clean.split(":")[0] ?? clean;
  const override = SOURCE_LABEL_OVERRIDES.get(clean) ?? SOURCE_LABEL_OVERRIDES.get(firstPart);
  if (override) return override;
  if (looksLikeSourceId(firstPart)) return formatDisplayLabel(firstPart.replace(/_lite$/, ""));
  return "";
}

function capitalize(value: string) {
  return value ? `${value[0].toUpperCase()}${value.slice(1)}` : value;
}

function looksLikeSourceId(value: string) {
  return (
    value.endsWith("_lite") ||
    value.includes("_public") ||
    value.includes("_fixture") ||
    value.includes("_source") ||
    value.includes("_reports") ||
    value.includes("_billings") ||
    value.includes("_manual_upload")
  );
}

function isKnownNodePrefix(prefix: string) {
  return [
    "airport",
    "architecture",
    "chemical",
    "company",
    "country",
    "critical_mineral",
    "eda",
    "equipment",
    "event",
    "fab",
    "gas",
    "ip",
    "list",
    "material",
    "packaging",
    "policy",
    "port",
    "process",
    "product",
    "raw_material",
    "region",
    "sector",
    "technology_node",
    "testing",
  ].includes(prefix);
}
