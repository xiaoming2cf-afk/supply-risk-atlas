Feature: SupplyRiskAtlas analyst workflows
  Supply-risk analysts need explainable, traceable risk views across suppliers,
  graph relationships, and evidence so they can prioritize interventions.

  @smoke @foundation
  Scenario: Open the public System Health Center
    Given the analyst opens the public SupplyRiskAtlas deployment
    When the analyst navigates to "#system-health-center"
    Then the page title is "System Health Center"
    And System Health Center is the first public navigation item
    And the page shows API health, source registry, freshness, source manifest, and graph status when verified data is available
    And unavailable, stale, partial, or degraded health data is labeled explicitly without fake metrics

  @smoke @risk
  Scenario: View portfolio risk overview
    Given the analyst has access to a populated supply-risk workspace
    When the analyst opens the portfolio overview
    Then the page shows ranked risk entities with score, severity, geography, and last updated time
    And the analyst can distinguish critical, elevated, and normal risk states
    And the page exposes a path to investigate a selected entity

  @risk @explainability
  Scenario: Investigate a supplier risk detail
    Given a supplier has an elevated risk score with supporting evidence
    When the analyst opens the supplier detail view
    Then the view shows the current score, contributing factors, and confidence level
    And each contributing factor links to source evidence or derived feature lineage
    And the displayed timestamps make data freshness visible

  @graph
  Scenario: Explore graph neighborhood for a supplier
    Given a supplier is connected to facilities, products, regions, and events
    When the analyst opens the graph neighborhood
    Then the graph shows nodes and edges with clear entity types
    And the analyst can filter by relationship type and time window
    And selecting a node preserves context for the original supplier

  @explainability @graph
  Scenario: Trace a risk signal from UI to data lineage
    Given a risk score is visible in the supplier detail view
    When the analyst requests the explanation for that score
    Then the explanation lists source datasets, contract stage, model or graph run, and evidence identifiers
    And the explanation avoids exposing internal-only fields
    And missing optional evidence is labeled without blocking the rest of the explanation

  @resilience
  Scenario: Show controlled degraded state when upstream data is stale
    Given the latest upstream data is older than the freshness threshold
    When the analyst opens the portfolio overview
    Then the page indicates that data is stale
    And rankings remain visible only when the last valid snapshot is available
    And actions that require fresh data are disabled or clearly marked

  @smoke @export
  Scenario: Export an investigation summary
    Given the analyst has selected a supplier with risk evidence and graph context
    When the analyst exports the investigation summary
    Then the export includes supplier identity, risk score, evidence summary, graph context, generation time, graph version, source manifest, and report version
    And the export records warnings, assumptions, limitations, and fixture graph status
    And the export excludes raw source payloads, private runtime diagnostics, credentials, and hidden internal fields

  @smoke @simulation
  Scenario: Run forward stress testing from the Shock Simulator
    Given the analyst opens "#shock-simulator"
    When the analyst runs a fixed-seed forward stress test for "company:tsmc"
    Then the page shows expected loss, p50 loss, p90 loss, p95 loss, CVaR95, recovery timing, affected nodes, and top transmission paths
    And the run manifest includes run id, seed, graph version, source manifest, simulation version, timestamp, warnings, and evidence references
    And no dollar loss is displayed without licensed private exposure data

  @smoke @reverse-stress
  Scenario: Search for reverse stress shock sets
    Given the analyst opens "#reverse-stress-lab"
    When the analyst runs reverse stress search with a fixed threshold and seed
    Then the page shows ranked shock sets, threshold status, expected loss, CVaR95, plausibility cost, affected paths, baseline comparison, graph version, and source manifest
    And policy-related text is limited to resilience planning and compliance review

  @smoke @optimization
  Scenario: Optimize budget-constrained interventions
    Given the analyst opens "#intervention-optimizer"
    When the analyst sets a budget and runs the optimizer
    Then the page shows recommended actions, before and after expected loss, before and after CVaR95, cost, resilience ROI, assumptions, constraints, evidence refs, graph version, and source manifest
    And recommended actions remain within the budget and avoid illegal workaround advice

  @smoke @report
  Scenario: Generate the investigation report page export
    Given the analyst opens "#investigation-report"
    When the analyst generates a JSON investigation report for "company:tsmc"
    Then the page shows report id, graph version, source manifest, evidence summary, report version, and fixture graph warning
    And the report marks raw payloads and private diagnostics as excluded
