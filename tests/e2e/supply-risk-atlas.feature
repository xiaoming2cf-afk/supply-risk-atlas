Feature: SupplyRiskAtlas analyst workflows
  Supply-risk analysts need explainable, traceable risk views across suppliers,
  graph relationships, and evidence so they can prioritize interventions.

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
    Then the export includes supplier identity, risk score, evidence summary, graph context, and generation time
    And the export records the data freshness state
    And the export excludes private runtime diagnostics
