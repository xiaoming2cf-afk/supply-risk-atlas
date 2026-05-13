import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, rm, writeFile } from "node:fs/promises";
import net from "node:net";
import os from "node:os";
import path from "node:path";

const root = process.cwd();
const smokeMode = process.env.SUPPLY_RISK_SMOKE_MODE ?? cliOption("mode") ?? "proxy";
const webUrl =
  process.env.SUPPLY_RISK_WEB_URL ??
  (smokeMode === "deployed" ? "https://supply-risk-atlas-web.onrender.com" : "http://127.0.0.1:3000");
const expectedMode = process.env.SUPPLY_RISK_EXPECT_MODE;
const apiUrl =
  process.env.SUPPLY_RISK_API_URL ??
  process.env.NEXT_PUBLIC_SUPPLY_RISK_API_URL ??
  (smokeMode === "local" ? "http://127.0.0.1:8000/api/v1" : undefined) ??
  (smokeMode === "deployed" ? "https://supply-risk-atlas-api.onrender.com/api/v1" : undefined) ??
  new URL("/api/v1", webUrl).toString();
const apiBase = apiUrl.replace(/\/$/, "");
const apiUrlLiteral = JSON.stringify(apiUrl.replace(/\/$/, ""));
const artifactDir = path.join(root, "artifacts", "browser-smoke");
const reportPath = path.join(artifactDir, "report.json");
const deployedBestEffort = smokeMode === "deployed" || process.env.SUPPLY_RISK_SMOKE_BEST_EFFORT === "1";

const pages = [
  ["System Health Center", "#system-health-center"],
  ["Global Risk Cockpit", "#global-risk-cockpit"],
  ["Graph Explorer", "#graph-explorer"],
  ["Entity Risk 360", "#company-risk-360"],
  ["Prediction Center", "#prediction-center"],
  ["Path Analysis", "#path-analysis"],
  ["Country Lens", "#country-lens"],
  ["Shock Simulator", "#shock-simulator"],
  ["Reverse Stress Lab", "#reverse-stress-lab"],
  ["Intervention Optimizer", "#intervention-optimizer"],
  ["Investigation Report", "#investigation-report"],
  ["Causal Evidence Board", "#causal-evidence-board"],
];

const zhGlobalRiskTitle = "\u5168\u7403\u98ce\u9669\u9a7e\u9a76\u8231";
const zhGraphExplorerLabel = "\u56fe\u8c31\u63a2\u7d22\u5668";
const frGlobalRiskTitle = "Poste de pilotage des risques mondiaux";
const frGraphExplorerLabel = "Explorateur de graphe";

function cliOption(name) {
  const prefix = `--${name}=`;
  const match = process.argv.slice(2).find((item) => item.startsWith(prefix));
  return match ? match.slice(prefix.length) : undefined;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const waitForExit = (processHandle) =>
  new Promise((resolve) => {
    if (processHandle.exitCode !== null) {
      resolve();
      return;
    }
    const timer = setTimeout(resolve, 2000);
    processHandle.once("exit", () => {
      clearTimeout(timer);
      resolve();
    });
  });

async function main() {
  await assertWebServer();
  await mkdir(artifactDir, { recursive: true });

  const port = await freePort();
  const profileDir = path.join(artifactDir, `chrome-profile-${Date.now()}`);
  const chrome = spawn(findChrome(), [
    "--headless=new",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-first-run",
    "--no-default-browser-check",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    "about:blank",
  ], { stdio: "ignore" });

  const checks = [];
  let client;
  try {
    await waitForChrome(port);
    const pageWsUrl = await newPage(port);
    client = new CdpClient(pageWsUrl);
    await client.connect();
    await client.send("Page.enable");
    await client.send("Runtime.enable");

    const apiCapabilities = {
      systemHealth: await fetchApiJson("/dashboard/system-health-center"),
      graphSnapshot: await fetchApiJson("/graph/snapshot"),
      graphNeighborhood: await fetchApiJson("/graph/neighborhood?node_id=company:tsmc&depth=1"),
      entityRisk: await fetchApiJson("/risk/entities/company:tsmc"),
      riskPortfolio: await fetchApiJson("/risk/portfolio?node_type=company&limit=3"),
      forwardScenario: await fetchApiJson("/scenarios/forward", {
        method: "POST",
        body: JSON.stringify({
          scenario_type: "earthquake",
          targets: ["company:tsmc"],
          severity_distribution: { type: "fixed", params: { value: 0.72 } },
          duration_days_distribution: { type: "fixed", params: { value: 28 } },
          iterations: 80,
          seed: 42,
          as_of_time: "2026-05-01T00:00:00Z",
          assumptions: ["browser smoke fixture run"],
        }),
      }),
      reverseScenario: await fetchApiJson("/scenarios/reverse", {
        method: "POST",
        body: JSON.stringify({
          target_metric: "cvar95_loss",
          failure_threshold: 35,
          candidate_scope: {
            node_types: ["company", "equipment", "material", "chemical", "process_stage", "product_grade"],
            edge_types: [],
          },
          max_combination_size: 2,
          beam_width: 4,
          iterations_per_candidate: 30,
          seed: 42,
          as_of_time: "2026-05-01T00:00:00Z",
        }),
      }),
      interventionOptimization: await fetchApiJson("/optimization/interventions", {
        method: "POST",
        body: JSON.stringify({
          budget: 70,
          allowed_intervention_types: ["add_alternative_supplier", "increase_inventory_buffer", "add_policy_monitoring"],
          max_actions: 3,
          risk_aversion_beta: 0.7,
          compliance_constraints: { no_export_control_evasion: true, no_sanctions_circumvention: true },
          seed: 42,
          as_of_time: "2026-05-01T00:00:00Z",
        }),
      }),
      investigationReport: await fetchApiJson("/reports/investigation", {
        method: "POST",
        body: JSON.stringify({
          entity_id: "company:tsmc",
          include_entity_risk: true,
          format: "json",
        }),
      }),
    };
    const semiriskSystemHealthReady =
      isSuccessfulEnvelope(apiCapabilities.systemHealth) &&
      Boolean(apiCapabilities.systemHealth.body?.data?.semiconductorGraph);
    const semiriskRiskReady =
      isSuccessfulEnvelope(apiCapabilities.entityRisk) &&
      isSuccessfulEnvelope(apiCapabilities.riskPortfolio);
    const semiriskGraphReady =
      isSuccessfulEnvelope(apiCapabilities.graphSnapshot) &&
      isSuccessfulEnvelope(apiCapabilities.graphNeighborhood);
    const forwardScenarioReady = isSuccessfulEnvelope(apiCapabilities.forwardScenario);
    const reverseScenarioReady = isSuccessfulEnvelope(apiCapabilities.reverseScenario);
    const interventionOptimizationReady = isSuccessfulEnvelope(apiCapabilities.interventionOptimization);
    const investigationReportReady = isSuccessfulEnvelope(apiCapabilities.investigationReport);
    checks.push({
      page: "SemiRisk API capability",
      apiBase,
      systemHealthStatus: apiCapabilities.systemHealth.status,
      graphSnapshotStatus: apiCapabilities.graphSnapshot.status,
      graphNeighborhoodStatus: apiCapabilities.graphNeighborhood.status,
      entityRiskStatus: apiCapabilities.entityRisk.status,
      riskPortfolioStatus: apiCapabilities.riskPortfolio.status,
      forwardScenarioStatus: apiCapabilities.forwardScenario.status,
      reverseScenarioStatus: apiCapabilities.reverseScenario.status,
      interventionOptimizationStatus: apiCapabilities.interventionOptimization.status,
      investigationReportStatus: apiCapabilities.investigationReport.status,
      passed: expectedMode === "real" ? semiriskSystemHealthReady && semiriskGraphReady && semiriskRiskReady && forwardScenarioReady && reverseScenarioReady && interventionOptimizationReady && investigationReportReady : true,
    });

    for (const [page, hash] of pages) {
      await navigate(client, `${webUrl}${hash}`);
      const result = await waitFor(client, () => pageState(client), (state) => state.title === page);
      checks.push({
        page,
        hash,
        title: result.title,
        navCount: result.navCount,
        firstNavId: result.firstNavId,
        passed:
          result.title === page &&
          result.navCount === pages.length &&
          result.firstNavId === "system-health-center",
      });
    }

    await navigate(client, `${webUrl}#graph-explorer`);
    const graphV2Overview = await waitFor(
      client,
      () => graphV2State(client),
      (state) =>
        state.title === "Graph Explorer" &&
        state.hasV2Title &&
        state.hasV3ModeSelector &&
        state.hasLegend &&
        state.hasLayerControls &&
        state.hasFixtureWarning &&
        state.hasEvidenceContextSafety &&
        state.graphNodeCount >= 2 &&
        state.flowEdgeCount >= 1 &&
        state.graphNodeCount <= 20 &&
        state.flowEdgeCount <= 35,
    );
    checks.push({
      page: "Graph Explorer v2 overview caps",
      graphNodeCount: graphV2Overview.graphNodeCount,
      flowEdgeCount: graphV2Overview.flowEdgeCount,
      hasLegend: graphV2Overview.hasLegend,
      hasLayerControls: graphV2Overview.hasLayerControls,
      hasFixtureWarning: graphV2Overview.hasFixtureWarning,
      hasV3ModeSelector: graphV2Overview.hasV3ModeSelector,
      hasEvidenceContextSafety: graphV2Overview.hasEvidenceContextSafety,
      passed:
        graphV2Overview.title === "Graph Explorer" &&
        graphV2Overview.hasV2Title &&
        graphV2Overview.hasV3ModeSelector &&
        graphV2Overview.hasLegend &&
        graphV2Overview.hasLayerControls &&
        graphV2Overview.hasFixtureWarning &&
        graphV2Overview.hasEvidenceContextSafety &&
        graphV2Overview.graphNodeCount >= 2 &&
        graphV2Overview.flowEdgeCount >= 1 &&
        graphV2Overview.graphNodeCount <= 20 &&
        graphV2Overview.flowEdgeCount <= 35,
    });

    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      buttons.find((button) => button.textContent?.includes('Two-hop'))?.click();
    })()`);
    const graphV2Focus = await waitFor(
      client,
      () => graphV2State(client),
      (state) => state.text.includes("Focus view") && state.graphNodeCount >= 2 && state.graphNodeCount <= 25 && state.flowEdgeCount <= 40,
    );
    checks.push({
      page: "Graph Explorer v2 focus expansion caps",
      graphNodeCount: graphV2Focus.graphNodeCount,
      flowEdgeCount: graphV2Focus.flowEdgeCount,
      passed: graphV2Focus.graphNodeCount >= 2 && graphV2Focus.graphNodeCount <= 25 && graphV2Focus.flowEdgeCount <= 40,
    });

    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      buttons.find((button) => button.textContent?.trim().startsWith('Path'))?.click();
    })()`);
    const graphV2Path = await waitFor(
      client,
      () => graphV2State(client),
      (state) => state.text.includes("Path view") && state.text.includes("Transmission paths") && state.graphNodeCount >= 2 && state.flowEdgeCount >= 1,
    );
    checks.push({
      page: "Graph Explorer v2 path mode",
      graphNodeCount: graphV2Path.graphNodeCount,
      flowEdgeCount: graphV2Path.flowEdgeCount,
      passed:
        graphV2Path.text.includes("Path view") &&
        graphV2Path.text.includes("Transmission paths") &&
        graphV2Path.graphNodeCount >= 2 &&
        graphV2Path.flowEdgeCount >= 1,
    });

    await evaluate(client, `(() => {
      const layer = Array.from(document.querySelectorAll('.graph-layer-toggle')).find((item) => item.textContent?.includes('Trade'));
      layer?.querySelector('input')?.click();
    })()`);
    const graphV2LayerToggle = await waitFor(
      client,
      () => graphV2State(client),
      (state) => state.hasLayerControls && state.flowEdgeCount <= 40,
    );
    checks.push({
      page: "Graph Explorer v2 layer toggle",
      flowEdgeCount: graphV2LayerToggle.flowEdgeCount,
      passed: graphV2LayerToggle.hasLayerControls && graphV2LayerToggle.flowEdgeCount <= 40,
    });

    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      buttons.find((button) => button.textContent?.trim().startsWith('Timeline'))?.click();
    })()`);
    const graphV3Timeline = await waitFor(
      client,
      () => graphV2State(client),
      (state) => state.text.includes("Timeline mode") && state.text.includes("event nodes") && state.flowEdgeCount <= 40,
    );
    checks.push({
      page: "Graph Explorer v3 timeline mode",
      flowEdgeCount: graphV3Timeline.flowEdgeCount,
      passed: graphV3Timeline.text.includes("Timeline mode") && graphV3Timeline.flowEdgeCount <= 40,
    });

    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      buttons.find((button) => button.textContent?.trim().startsWith('Geo'))?.click();
    })()`);
    const graphV3Geo = await waitFor(
      client,
      () => graphV2State(client),
      (state) => state.text.includes("Geo mode") && state.graphNodeCount <= 20 && state.flowEdgeCount <= 35,
    );
    checks.push({
      page: "Graph Explorer v3 geo mode",
      graphNodeCount: graphV3Geo.graphNodeCount,
      flowEdgeCount: graphV3Geo.flowEdgeCount,
      passed: graphV3Geo.text.includes("Geo mode") && graphV3Geo.graphNodeCount <= 20 && graphV3Geo.flowEdgeCount <= 35,
    });

    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      buttons.find((button) => button.textContent?.trim().startsWith('Matrix'))?.click();
    })()`);
    const graphV3Matrix = await waitFor(
      client,
      () => graphV2State(client),
      (state) => state.text.includes("Matrix mode") && state.text.includes("dense node cloud"),
    );
    checks.push({
      page: "Graph Explorer v3 matrix mode",
      graphNodeCount: graphV3Matrix.graphNodeCount,
      passed: graphV3Matrix.text.includes("Matrix mode") && graphV3Matrix.text.includes("dense node cloud"),
    });

    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      buttons.find((button) => button.textContent?.trim().startsWith('Evidence'))?.click();
    })()`);
    const graphV3Evidence = await waitFor(
      client,
      () => graphV2State(client),
      (state) => state.text.includes("Evidence mode") && state.hasEvidenceContextSafety,
    );
    checks.push({
      page: "Graph Explorer v3 evidence-context safety",
      hasEvidenceContextSafety: graphV3Evidence.hasEvidenceContextSafety,
      passed: graphV3Evidence.text.includes("Evidence mode") && graphV3Evidence.hasEvidenceContextSafety,
    });

    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      buttons.find((button) => button.textContent?.trim().startsWith('Source Coverage'))?.click();
    })()`);
    const graphV3SourceCoverage = await waitFor(
      client,
      () => graphV2State(client),
      (state) => state.text.includes("Source Coverage mode") && state.text.includes("does not render the full graph"),
    );
    checks.push({
      page: "Graph Explorer v3 source coverage mode",
      passed:
        graphV3SourceCoverage.text.includes("Source Coverage mode") &&
        graphV3SourceCoverage.text.includes("does not render the full graph"),
    });

    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      buttons.find((button) => button.textContent?.trim().startsWith('Node Catalog'))?.click();
    })()`);
    const graphV3NodeCatalog = await waitFor(
      client,
      () => graphV2State(client),
      (state) => state.text.includes("Node Catalog mode") && state.text.includes("canonical catalog rows"),
    );
    checks.push({
      page: "Graph Explorer v3 node catalog mode",
      passed:
        graphV3NodeCatalog.text.includes("Node Catalog mode") &&
        graphV3NodeCatalog.text.includes("canonical catalog rows"),
    });

    await navigate(client, `${webUrl}#system-health-center`);
    const healthSemiriskTerms = [
      "SemiRisk-KG v0.1 fixture graph",
      "graphVersion",
      "sourceManifestId",
      "nodeCount",
      "edgeCount",
      "registryReady",
      "ontologyReady",
      "fixtureGraph",
      "fixture_graph:not_production_ready",
      "data_mode",
      "graph_mode",
      "storage_readiness",
      "connector_readiness",
      "deployment_version_readiness",
      "api_version",
      "web_build_version",
      "calibration_status",
      "not_production_ready",
    ];
    const healthState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "System Health Center" &&
        (semiriskSystemHealthReady
          ? healthSemiriskTerms.every((term) => state.text.toLowerCase().includes(term.toLowerCase()))
          : (
              state.text.includes("Source registry") ||
              state.text.includes("Data temporarily unavailable") ||
              state.text.includes("Public data unavailable")
            )),
    );
    const healthHasRegistryEvidence =
      healthState.text.includes("Source registry") &&
      /freshness/i.test(healthState.text) &&
      /manifest/i.test(healthState.text) &&
      (
        healthState.text.includes("Service status") ||
        healthState.text.includes("Risk API") ||
        healthState.text.includes("Public source ingest")
      );
    const healthHasControlledDegradedState =
      healthState.text.includes("Data temporarily unavailable") ||
      healthState.text.includes("Public data unavailable") ||
      healthState.text.includes("Partial public data") ||
        /unavailable|degraded/i.test(healthState.text);
    const healthTextLower = healthState.text.toLowerCase();
    const healthHasSemiriskEvidence = healthSemiriskTerms.every((term) => healthTextLower.includes(term.toLowerCase()));
    checks.push({
      page: "System Health Center public route",
      title: healthState.title,
      firstNavId: healthState.firstNavId,
      hasRegistryEvidence: healthHasRegistryEvidence,
      hasSemiriskEvidence: healthHasSemiriskEvidence,
      hasControlledDegradedState: healthHasControlledDegradedState,
      evidenceExcerpt: textExcerpt(healthState.text, healthSemiriskTerms),
      passed:
        healthState.title === "System Health Center" &&
        healthState.firstNavId === "system-health-center" &&
        (semiriskSystemHealthReady ? healthHasSemiriskEvidence : healthHasControlledDegradedState),
    });
    const chartTableTerms = [
      "Evidence-bound chart and table components",
      "Source freshness",
      "Graph quality",
      "SourceCatalog",
      "data_mode",
      "not_production_ready",
    ];
    checks.push({
      page: "chart/table component controlled states",
      present: chartTableTerms.filter((term) => healthTextLower.includes(term.toLowerCase())),
      passed: !semiriskSystemHealthReady || chartTableTerms.every((term) => healthTextLower.includes(term.toLowerCase())),
    });

    const pageVisualizationChecks = [
      {
        page: "Entity Risk 360 visualization integration",
        hash: "#company-risk-360",
        title: "Entity Risk 360",
        terms: ["Risk charts and evidence tables", "Risk component breakdown", "HHI concentration", "Evidence refs"],
      },
      {
        page: "Shock Simulator visualization integration",
        hash: "#shock-simulator",
        title: "Shock Simulator",
        terms: ["Forward analytics charts and tables", "Monte Carlo histogram", "Functionality curve", "ScenarioRun"],
      },
      {
        page: "Reverse Stress Lab visualization integration",
        hash: "#reverse-stress-lab",
        title: "Reverse Stress Lab",
        terms: ["Reverse stress charts and tables", "Top shock set path chart", "Ranked shock sets table"],
      },
      {
        page: "Intervention Optimizer visualization integration",
        hash: "#intervention-optimizer",
        title: "Intervention Optimizer",
        terms: ["Optimizer charts and action tables", "Optimizer before after", "OptimizerAction"],
      },
      {
        page: "Investigation Report visualization integration",
        hash: "#investigation-report",
        title: "Investigation Report",
        terms: ["Report metadata and evidence table", "Evidence summary table", "Evidence count"],
      },
      {
        page: "Evidence Board visualization integration",
        hash: "#causal-evidence-board",
        title: "Causal Evidence Board",
        terms: ["Evidence audit table", "Evidence refs", "Source freshness", "EVIDENCE_TO_GRAPH_PATH"],
      },
    ];
    for (const check of pageVisualizationChecks) {
      await navigate(client, `${webUrl}${check.hash}`);
      const state = await waitFor(
        client,
        () => pageState(client),
        (candidate) =>
          candidate.title === check.title &&
          (semiriskSystemHealthReady
            ? check.terms.every((term) => candidate.text.includes(term))
            : candidate.text.includes("Data temporarily unavailable") || candidate.text.includes("unavailable")),
      );
      checks.push({
        page: check.page,
        present: check.terms.filter((term) => state.text.includes(term)),
        passed:
          state.title === check.title &&
          (!semiriskSystemHealthReady || check.terms.every((term) => state.text.includes(term))),
      });
    }

    await navigate(client, `${webUrl}#company-risk-360`);
    const riskEvidenceTerms = [
      "company:tsmc",
      "likelihood_impact_vulnerability_framework",
      "semirisk_liv_framework_v0.1",
      "fixture_proxy_not_calibrated",
      "likelihood",
      "impact",
      "vulnerability_modifier",
      "source_concentration_hhi",
      "substitution_gap",
      "evidence_refs",
      "formula_refs",
      "semirisk_risk_score_likelihood_impact_v0.1",
      "graph_version",
      "source_manifest_id",
      "fixture_graph:not_production_ready",
    ];
    const riskState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Entity Risk 360" &&
        (semiriskRiskReady
          ? riskEvidenceTerms.every((term) => state.text.includes(term))
          : (
              state.text.includes("Entity Risk 360 unavailable") ||
              state.text.includes("Risk score unavailable")
            )),
    );
    const riskHasScoreEvidence = riskEvidenceTerms.every((term) => riskState.text.includes(term));
    const riskHasControlledDegradedState =
      riskState.text.includes("Entity Risk 360 unavailable") &&
      riskState.text.includes("failed_endpoint") &&
      riskState.text.includes("source_status");
    checks.push({
      page: "Entity Risk 360 Risk Score v0",
      title: riskState.title,
      hasScoreEvidence: riskHasScoreEvidence,
      hasControlledDegradedState: riskHasControlledDegradedState,
      evidenceExcerpt: textExcerpt(riskState.text, riskEvidenceTerms),
      passed:
        riskState.title === "Entity Risk 360" &&
        (semiriskRiskReady ? riskHasScoreEvidence : riskHasControlledDegradedState),
    });

    await navigate(client, `${webUrl}#shock-simulator`);
    const forwardControlTerms = [
      "Shock Simulator",
      "scenario_type",
      "company:tsmc",
      "severity_distribution",
      "duration_days_distribution",
      "iterations",
      "seed",
      "fixture_graph:not_production_ready",
    ];
    const shockInitialState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Shock Simulator" &&
        forwardControlTerms.every((term) => state.text.includes(term)),
    );
    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const runButton = buttons.find((button) => (button.textContent ?? '').includes('Run forward stress'));
      runButton?.click();
    })()`);
    const forwardResultTerms = [
      "expected_loss",
      "p50_loss",
      "p90_loss",
      "p95_loss",
      "cvar_95",
      "time_to_recover_days",
      "time_to_survive_days",
      "loss_mode",
      "resilience_integral_loss",
      "propagation_mode",
      "auto_semiconductor",
      "formula_refs",
      "calibration_status",
      "run_id",
      "seed",
      "graph_version",
      "source_manifest_id",
      "simulation_version",
      "semirisk_forward_mc_v0.1",
    ];
    const shockResultState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Shock Simulator" &&
        (forwardScenarioReady
          ? forwardResultTerms.every((term) => state.text.includes(term))
          : state.text.includes("Shock Simulator unavailable") && state.text.includes("failed_endpoint")),
    );
    checks.push({
      page: "Shock Simulator forward Monte Carlo v2",
      title: shockResultState.title,
      hasControls: forwardControlTerms.every((term) => shockInitialState.text.includes(term)),
      hasRunManifest: forwardResultTerms.every((term) => shockResultState.text.includes(term)),
      hasControlledDegradedState:
        shockResultState.text.includes("Shock Simulator unavailable") &&
        shockResultState.text.includes("failed_endpoint") &&
        shockResultState.text.includes("source_status"),
      evidenceExcerpt: textExcerpt(shockResultState.text, forwardResultTerms),
      passed:
        shockResultState.title === "Shock Simulator" &&
        forwardControlTerms.every((term) => shockInitialState.text.includes(term)) &&
        (forwardScenarioReady
          ? forwardResultTerms.every((term) => shockResultState.text.includes(term))
          : shockResultState.text.includes("Shock Simulator unavailable") && shockResultState.text.includes("failed_endpoint")),
    });

    await navigate(client, `${webUrl}#reverse-stress-lab`);
    const reverseControlTerms = [
      "Reverse Stress Lab",
      "target_metric",
      "failure_threshold",
      "max_combination_size",
      "beam_width",
      "iterations_per_candidate",
      "seed",
      "fixture_graph:not_production_ready",
    ];
    const reverseInitialState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Reverse Stress Lab" &&
        reverseControlTerms.every((term) => state.text.includes(term)),
    );
    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const runButton = buttons.find((button) => (button.textContent ?? '').includes('Run reverse stress'));
      runButton?.click();
    })()`);
    const reverseResultTerms = [
      "ranked_shock_sets",
      "threshold_met",
      "expected_loss",
      "cvar95",
      "plausibility_cost",
      "failure_threshold_normalized",
      "threshold_metric_basis",
      "loss_mode",
      "propagation_mode",
      "baseline_comparison",
      "run_id",
      "graph_version",
      "source_manifest_id",
      "semirisk_reverse_stress_v0.1",
    ];
    const reverseResultState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Reverse Stress Lab" &&
        (reverseScenarioReady
          ? reverseResultTerms.every((term) => state.text.includes(term))
          : state.text.includes("Reverse Stress Lab unavailable") && state.text.includes("failed_endpoint")),
    );
    checks.push({
      page: "Reverse Stress Lab v1",
      title: reverseResultState.title,
      hasControls: reverseControlTerms.every((term) => reverseInitialState.text.includes(term)),
      hasRankedShockSets: reverseResultTerms.every((term) => reverseResultState.text.includes(term)),
      hasControlledDegradedState:
        reverseResultState.text.includes("Reverse Stress Lab unavailable") &&
        reverseResultState.text.includes("failed_endpoint") &&
        reverseResultState.text.includes("source_status"),
      evidenceExcerpt: textExcerpt(reverseResultState.text, reverseResultTerms),
      passed:
        reverseResultState.title === "Reverse Stress Lab" &&
        reverseControlTerms.every((term) => reverseInitialState.text.includes(term)) &&
        (reverseScenarioReady
          ? reverseResultTerms.every((term) => reverseResultState.text.includes(term))
          : reverseResultState.text.includes("Reverse Stress Lab unavailable") && reverseResultState.text.includes("failed_endpoint")),
    });

    await navigate(client, `${webUrl}#intervention-optimizer`);
    const optimizerControlTerms = [
      "Intervention Optimizer",
      "budget",
      "max_actions",
      "risk_aversion_beta",
      "add_alternative_supplier",
      "fixture_graph:not_production_ready",
    ];
    const optimizerInitialState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Intervention Optimizer" &&
        optimizerControlTerms.every((term) => state.text.includes(term)),
    );
    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const runButton = buttons.find((button) => (button.textContent ?? '').includes('Run optimizer'));
      runButton?.click();
    })()`);
    const optimizerResultTerms = [
      "recommended_actions",
      "before_expected_loss",
      "after_expected_loss",
      "before_cvar95",
      "after_cvar95",
      "cost",
      "resilience_roi",
      "optimization_context_type",
      "scenario_count",
      "before_simulation_run_ids",
      "after_simulation_run_ids",
      "baseline_comparison",
      "run_id",
      "graph_version",
      "source_manifest_id",
      "semirisk_intervention_optimizer_v0.1",
    ];
    const optimizerResultState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Intervention Optimizer" &&
        (interventionOptimizationReady
          ? optimizerResultTerms.every((term) => state.text.includes(term))
          : state.text.includes("Intervention Optimizer unavailable") && state.text.includes("failed_endpoint")),
    );
    checks.push({
      page: "Intervention Optimizer v1",
      title: optimizerResultState.title,
      hasControls: optimizerControlTerms.every((term) => optimizerInitialState.text.includes(term)),
      hasRecommendedActions: optimizerResultTerms.every((term) => optimizerResultState.text.includes(term)),
      hasControlledDegradedState:
        optimizerResultState.text.includes("Intervention Optimizer unavailable") &&
        optimizerResultState.text.includes("failed_endpoint") &&
        optimizerResultState.text.includes("source_status"),
      evidenceExcerpt: textExcerpt(optimizerResultState.text, optimizerResultTerms),
      passed:
        optimizerResultState.title === "Intervention Optimizer" &&
        optimizerControlTerms.every((term) => optimizerInitialState.text.includes(term)) &&
        (interventionOptimizationReady
          ? optimizerResultTerms.every((term) => optimizerResultState.text.includes(term))
          : optimizerResultState.text.includes("Intervention Optimizer unavailable") && optimizerResultState.text.includes("failed_endpoint")),
    });

    await navigate(client, `${webUrl}#investigation-report`);
    const reportControlTerms = [
      "Investigation Report",
      "entity_id",
      "include_entity_risk",
      "Generate JSON report",
      "Export Markdown",
      "fixture_graph:not_production_ready",
    ];
    const reportInitialState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Investigation Report" &&
        reportControlTerms.every((term) => state.text.includes(term)),
    );
    await evaluate(client, `(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const runButton = buttons.find((button) => (button.textContent ?? '').includes('Generate JSON report'));
      runButton?.click();
    })()`);
    const reportResultTerms = [
      "report_id",
      "graph_version",
      "source_manifest_id",
      "report_version",
      "semirisk_investigation_report_v0.1",
      "raw_payload_excluded",
      "private_diagnostics_excluded",
      "evidence_summary",
      "risk_scoring_method",
      "formula_refs",
      "Model limitations",
      "fixture_graph:not_production_ready",
    ];
    const reportResultState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Investigation Report" &&
        (investigationReportReady
          ? reportResultTerms.every((term) => state.text.includes(term))
          : state.text.includes("Investigation Report unavailable") && state.text.includes("failed_endpoint")),
    );
    checks.push({
      page: "Investigation Report export v1",
      title: reportResultState.title,
      hasControls: reportControlTerms.every((term) => reportInitialState.text.includes(term)),
      hasReportExport: reportResultTerms.every((term) => reportResultState.text.includes(term)),
      hasControlledDegradedState:
        reportResultState.text.includes("Investigation Report unavailable") &&
        reportResultState.text.includes("failed_endpoint") &&
        reportResultState.text.includes("source_status"),
      evidenceExcerpt: textExcerpt(reportResultState.text, reportResultTerms),
      passed:
        reportResultState.title === "Investigation Report" &&
        reportControlTerms.every((term) => reportInitialState.text.includes(term)) &&
        (investigationReportReady
          ? reportResultTerms.every((term) => reportResultState.text.includes(term))
          : reportResultState.text.includes("Investigation Report unavailable") && reportResultState.text.includes("failed_endpoint")),
    });

    if (expectedMode) {
      const expectedModeText = { real: "Public data", mock: "Data unavailable", fallback: "Data unavailable" }[expectedMode];
      if (!expectedModeText) throw new Error(`Unsupported SUPPLY_RISK_EXPECT_MODE: ${expectedMode}`);
      await navigate(client, `${webUrl}#global-risk-cockpit`);
      const modeState = await pageState(client);
      const apiDiagnostic = await evaluate(client, `fetch(${apiUrlLiteral} + '/dashboard/global-risk-cockpit', { headers: { 'content-type': 'application/json' } })
        .then(async (response) => ({ ok: response.ok, status: response.status, bodyPrefix: (await response.text()).slice(0, 80) }))
        .catch((error) => ({ error: String(error) }))`);
      const shockDiagnostic = await evaluate(client, `fetch(${apiUrlLiteral} + '/dashboard/shock-simulator', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ region: '中国台湾 semiconductor corridor', commodity: 'advanced semiconductor components', severity: 95, durationDays: 28, scope: 'regional' })
        })
        .then(async (response) => ({ ok: response.ok, status: response.status, bodyPrefix: (await response.text()).slice(0, 80) }))
        .catch((error) => ({ error: String(error) }))`);
      checks.push({
        page: "runtime data mode",
        expectedMode,
        modeText: modeState.modeText,
        lineageText: modeState.lineageText,
        apiDiagnostic,
        shockDiagnostic,
        passed:
          modeState.modeText.includes(expectedModeText) &&
          modeState.lineageText.includes("Coverage:") &&
          !modeState.lineageText.includes("Request:") &&
          !modeState.lineageText.includes("Lineage:"),
      });
    }

    const degradedApiResult = await evaluate(client, `fetch(${apiUrlLiteral} + '/dashboard/unavailable-test', { headers: { 'content-type': 'application/json' } })
      .then(async (response) => ({ ok: response.ok, status: response.status, body: await response.json() }))
      .catch((error) => ({ error: String(error) }))`);
    checks.push({
      page: "degraded envelope preservation",
      status: degradedApiResult.status,
      sourceStatus: degradedApiResult.body?.source_status,
      requestId: degradedApiResult.body?.request_id,
      passed:
        degradedApiResult.status === 404 &&
        degradedApiResult.body?.status === "error" &&
        degradedApiResult.body?.request_id &&
        ["fresh", "stale", "partial", "unavailable"].includes(degradedApiResult.body?.source_status),
    });

    await navigate(client, `${webUrl}#global-risk-cockpit`);
    const lineageState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.lineageText.includes("Coverage:") &&
        state.lineageText.includes("Updated:") &&
        state.lineageText.includes("Source:") &&
        !state.lineageText.includes("Lineage:") &&
        !state.lineageText.includes("Request:") &&
        !state.lineageText.includes("api-unavailable://"),
    );
    checks.push({
      page: "public data status hides internal diagnostics",
      lineageText: lineageState.lineageText,
      passed:
        lineageState.lineageText.includes("Coverage:") &&
        lineageState.lineageText.includes("Updated:") &&
        lineageState.lineageText.includes("Source:") &&
        !lineageState.lineageText.includes("Lineage:") &&
        !lineageState.lineageText.includes("Request:") &&
        !lineageState.lineageText.includes("api-unavailable://"),
    });

    const deniedDemoStrings = [
      "Apex Mobility",
      "Orion Cells",
      "Kestrel Logic",
      "Northstar Devices",
      "Helio Polymers",
      "Customs filings + battery spot price panel",
      "EV platforms",
      "ADAS silicon",
      "MOCK FALLBACK DATA VISIBLE",
      "synthetic mock dashboard data",
      "Foundry wafer allocation",
      "Port closure causes",
      "g_2026_04_30",
      "tier-2 electronics",
      "2417000",
      "3981000",
      "4210000",
      "Raw feeds",
      "Public-source fallback dashboard seed",
      "public-source-fallback-dashboard",
      "client-fallback",
      "PUBLIC SOURCE FALLBACK DATA IS DISPLAYED",
      "\"mode\":\"fallback\"",
      "\"data_mode\":\"mock\"",
      "\"data_mode\":\"synthetic\"",
    ];
    const foundDemoStrings = [];
    for (const [page, hash] of pages) {
      await navigate(client, `${webUrl}${hash}`);
      const scanState = await waitFor(client, () => pageState(client), (state) => state.title === page);
      const found = deniedDemoStrings.filter((text) => scanState.text.includes(text));
      if (found.length > 0) {
        foundDemoStrings.push({ page, hash, found });
      }
    }
    checks.push({
      page: "no fictional demo data",
      denied: foundDemoStrings,
      passed: foundDemoStrings.length === 0,
    });

    if (expectedMode === "real") {
      const sourceRegistryDiagnostic = await evaluate(client, `fetch(${apiUrlLiteral} + '/sources', { headers: { 'content-type': 'application/json' } })
        .then((response) => response.json())
        .catch((error) => ({ error: String(error) }))`);
      checks.push({
        page: "source registry API",
        manifestRef: sourceRegistryDiagnostic.data?.manifestRef,
        sourceCount: sourceRegistryDiagnostic.data?.sourceCount,
        silverEntityCount: sourceRegistryDiagnostic.data?.silverEntityCount,
        passed:
          sourceRegistryDiagnostic.status === "success" &&
          sourceRegistryDiagnostic.mode === "real" &&
          sourceRegistryDiagnostic.data?.manifestRef?.startsWith("manifest_public_real_") &&
          sourceRegistryDiagnostic.data?.sourceCount >= 8 &&
          sourceRegistryDiagnostic.data?.sources?.some((source) => source.id === "usgs_earthquakes") &&
          sourceRegistryDiagnostic.data?.silverEntityCount >= 140,
      });

      const lineageDiagnostic = await evaluate(client, `fetch(${apiUrlLiteral} + '/lineage', { headers: { 'content-type': 'application/json' } })
        .then((response) => response.json())
        .catch((error) => ({ error: String(error) }))`);
      checks.push({
        page: "evidence lineage API",
        manifestRef: lineageDiagnostic.data?.manifestRef,
        rawRecordCount: lineageDiagnostic.data?.rawRecordCount,
        passed:
          lineageDiagnostic.status === "success" &&
          lineageDiagnostic.mode === "real" &&
          lineageDiagnostic.data?.manifestRef?.startsWith("manifest_public_real_") &&
          lineageDiagnostic.data?.rawRecordCount >= 8 &&
          lineageDiagnostic.data?.records?.some((record) => record.sourceId === "gdelt" && record.goldEdgeEventIds.length > 0),
      });

      const apiPayloadFindings = [];
      const postOnlyWorkflowPages = new Set([
        "#shock-simulator",
        "#reverse-stress-lab",
        "#intervention-optimizer",
        "#investigation-report",
      ]);
      for (const [, hash] of pages.filter(([, hash]) => !postOnlyWorkflowPages.has(hash))) {
        const pageId = hash.slice(1);
        const payloadText = await evaluate(client, `fetch(${apiUrlLiteral} + '/dashboard/${pageId}', { headers: { 'content-type': 'application/json' } })
          .then((response) => response.text())
          .catch((error) => String(error))`);
        const found = deniedDemoStrings.filter((text) => payloadText.includes(text));
        if (found.length > 0) {
          apiPayloadFindings.push({ endpoint: `/dashboard/${pageId}`, found });
        }
      }
      const shockPayloadText = await evaluate(client, `fetch(${apiUrlLiteral} + '/dashboard/shock-simulator', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ region: '中国台湾 semiconductor corridor', commodity: 'advanced semiconductor components', severity: 95, durationDays: 28, scope: 'regional' })
        })
        .then((response) => response.text())
        .catch((error) => String(error))`);
      const shockFound = deniedDemoStrings.filter((text) => shockPayloadText.includes(text));
      if (shockFound.length > 0) {
        apiPayloadFindings.push({ endpoint: "/dashboard/shock-simulator", found: shockFound });
      }
      checks.push({
        page: "no fictional demo API payload",
        denied: apiPayloadFindings,
        passed: apiPayloadFindings.length === 0,
      });
    }

    if (process.env.SUPPLY_RISK_FULL_SMOKE === "1") {
    await navigate(client, `${webUrl}#graph-explorer`);
    await evaluate(client, `(() => {
      const input = document.querySelector('input[type="search"]');
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
      setter.call(input, '0000320193');
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    })()`);
    const entitySearchState = await waitFor(
      client,
      () => evaluate(client, `(() => ({
        graphNodeCount: document.querySelectorAll('.risk-flow-node').length,
        flowNodeCount: document.querySelectorAll('.react-flow__node').length,
        flowEdgeCount: document.querySelectorAll('.react-flow__edge, .risk-flow-link-node').length,
        text: document.body.innerText,
        searchValue: document.querySelector('input[type="search"]')?.value ?? ''
      }))()`),
      (state) =>
        state.searchValue === "0000320193" &&
        state.graphNodeCount >= 2 &&
        state.flowNodeCount >= 2 &&
        state.flowEdgeCount >= 1 &&
        state.text.includes("Apple Inc."),
    );
    checks.push({
      page: "Graph Explorer entity search retains adjacency",
      graphNodeCount: entitySearchState.graphNodeCount,
      flowNodeCount: entitySearchState.flowNodeCount,
      flowEdgeCount: entitySearchState.flowEdgeCount,
      passed:
        entitySearchState.searchValue === "0000320193" &&
        entitySearchState.graphNodeCount >= 2 &&
        entitySearchState.flowNodeCount >= 2 &&
        entitySearchState.flowEdgeCount >= 1 &&
        entitySearchState.text.includes("Apple Inc."),
    });

    await evaluate(client, `(() => {
      const input = document.querySelector('input[type="search"]');
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
      setter.call(input, 'TX.VAL.TECH.MF.ZS');
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    })()`);
    const dataNodeSearchState = await waitFor(
      client,
      () => evaluate(client, `(() => ({
        graphNodeCount: document.querySelectorAll('.risk-flow-node').length,
        flowNodeCount: document.querySelectorAll('.react-flow__node').length,
        flowEdgeCount: document.querySelectorAll('.react-flow__edge, .risk-flow-link-node').length,
        text: document.body.innerText,
        searchValue: document.querySelector('input[type="search"]')?.value ?? ''
      }))()`),
      (state) =>
        state.searchValue === "TX.VAL.TECH.MF.ZS" &&
        state.graphNodeCount >= 2 &&
        state.flowNodeCount >= 2 &&
        state.flowEdgeCount >= 1 &&
        state.text.includes("High-technology exports percent of manufactured exports"),
    );
    checks.push({
      page: "Graph Explorer data node search retains adjacency",
      graphNodeCount: dataNodeSearchState.graphNodeCount,
      flowNodeCount: dataNodeSearchState.flowNodeCount,
      flowEdgeCount: dataNodeSearchState.flowEdgeCount,
      passed:
        dataNodeSearchState.searchValue === "TX.VAL.TECH.MF.ZS" &&
        dataNodeSearchState.graphNodeCount >= 2 &&
        dataNodeSearchState.flowNodeCount >= 2 &&
        dataNodeSearchState.flowEdgeCount >= 1 &&
        dataNodeSearchState.text.includes("High-technology exports percent of manufactured exports"),
    });

    await navigate(client, `${webUrl}#prediction-center`);
    const predictionCenterApi = await evaluate(client, `fetch(${apiUrlLiteral} + '/dashboard/prediction-center', { headers: { 'content-type': 'application/json' } })
      .then((response) => response.json())
      .catch((error) => ({ error: String(error) }))`);
    const predictionCenterState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Prediction Center" &&
        state.text.includes("Prediction workbench") &&
        state.text.includes("Score mechanism"),
    );
    checks.push({
      page: "Prediction Center mechanisms and evidence paths",
      predictionCount: predictionCenterApi.data?.predictions?.length ?? 0,
      saturatedScoreCount: predictionCenterApi.data?.saturatedScoreCount ?? 0,
      passed:
        predictionCenterState.title === "Prediction Center" &&
        predictionCenterState.text.includes("Prediction workbench") &&
        predictionCenterApi.status === "success" &&
        predictionCenterApi.data?.predictions?.length > 0 &&
        predictionCenterApi.data?.mechanisms?.length > 0 &&
        predictionCenterApi.data?.saturatedScoreCount < predictionCenterApi.data?.predictions?.length,
    });

    await navigate(client, `${webUrl}#path-analysis`);
    const pathAnalysisApi = await evaluate(client, `fetch(${apiUrlLiteral} + '/dashboard/path-analysis', { headers: { 'content-type': 'application/json' } })
      .then((response) => response.json())
      .catch((error) => ({ error: String(error) }))`);
    const pathAnalysisState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Path Analysis" &&
        state.text.includes("Critical nodes") &&
        state.text.includes("Transmission paths"),
    );
    checks.push({
      page: "Path Analysis critical nodes and transmission paths",
      criticalNodeCount: pathAnalysisApi.data?.criticalNodes?.length ?? 0,
      transmissionPathCount: pathAnalysisApi.data?.transmissionPaths?.length ?? 0,
      passed:
        pathAnalysisState.title === "Path Analysis" &&
        pathAnalysisState.text.includes("Critical nodes") &&
        pathAnalysisState.text.includes("Transmission paths") &&
        pathAnalysisApi.status === "success" &&
        pathAnalysisApi.data?.criticalNodes?.length > 0 &&
        pathAnalysisApi.data?.transmissionPaths?.length > 0,
    });

    await navigate(client, `${webUrl}#country-lens`);
    const countryLensApi = await evaluate(client, `fetch(${apiUrlLiteral} + '/dashboard/country-lens', { headers: { 'content-type': 'application/json' } })
      .then((response) => response.json())
      .catch((error) => ({ error: String(error) }))`);
    const countryLensState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "Country Lens" &&
        state.text.includes("Available countries") &&
        state.text.includes("中国台湾"),
    );
    checks.push({
      page: "Country Lens available countries and selected lens",
      availableCountryCount: countryLensApi.data?.availableCountries?.length ?? 0,
      selectedCountry: countryLensApi.data?.countryLens?.countryCode,
      passed:
        countryLensState.title === "Country Lens" &&
        countryLensState.text.includes("Available countries") &&
        countryLensState.text.includes("中国台湾") &&
        countryLensApi.status === "success" &&
        countryLensApi.data?.availableCountries?.length > 0 &&
        countryLensApi.data?.countryLens?.countryCode === "CN" &&
        !countryLensApi.data?.availableCountries?.some((country) => country.code === "TW"),
    });

    await navigate(client, `${webUrl}#global-risk-cockpit`);
    await evaluate(client, `document.querySelector('[data-page-id="graph-explorer"]')?.click()`);
    const navClick = await waitFor(client, () => pageState(client), (state) => state.title === "Graph Explorer");
    checks.push({ page: "nav click to Graph Explorer", title: navClick.title, passed: navClick.title === "Graph Explorer" });

    await navigate(client, `${webUrl}#global-risk-cockpit`);
    const languageBefore = await waitFor(client, () => pageLanguageState(client), (state) => state.title === "Global Risk Cockpit");
    await setPageLanguage(client, "zh");
    const zhState = await waitFor(
      client,
      () => pageLanguageState(client),
      (state) => state.language === "zh" && state.title === zhGlobalRiskTitle && state.navText.includes(zhGraphExplorerLabel),
    );
    await setPageLanguage(client, "fr");
    const frState = await waitFor(
      client,
      () => pageLanguageState(client),
      (state) => state.language === "fr" && state.title === frGlobalRiskTitle && state.navText.includes(frGraphExplorerLabel),
    );
    await navigate(client, `${webUrl}#graph-explorer`);
    const translatedGraphState = await waitFor(
      client,
      () => pageLanguageState(client),
      (state) =>
        state.language === "fr" &&
        state.title === frGraphExplorerLabel &&
        state.bodyText.includes("Advanced Micro Devices") &&
        state.bodyText.includes("中国台湾") &&
        state.bodyText.includes("Hon Hai Precision Industry"),
    );
    await navigate(client, `${webUrl}#causal-evidence-board`);
    const translatedEvidenceState = await waitFor(
      client,
      () => pageLanguageState(client),
      (state) =>
        state.language === "fr" &&
        (
          state.bodyText.includes("SEC EDGAR") ||
          state.bodyText.includes("GDELT") ||
          state.bodyText.includes("Public no-key real source manifest") ||
          state.bodyText.includes("OFAC Sanctions List Service")
        ),
    );
    await navigate(client, `${webUrl}#global-risk-cockpit`);
    await setPageLanguage(client, "en");
    const languageAfter = await waitFor(client, () => pageLanguageState(client), (state) => state.language === "en" && state.title === "Global Risk Cockpit");
    checks.push({
      page: "global page translator",
      beforeLanguage: languageBefore.language,
      zhTitle: zhState.title,
      frTitle: frState.title,
      afterLanguage: languageAfter.language,
      preservedEntities:
        translatedGraphState.bodyText.includes("Advanced Micro Devices") &&
        translatedGraphState.bodyText.includes("中国台湾") &&
        translatedGraphState.bodyText.includes("Hon Hai Precision Industry"),
      preservedSource:
        translatedEvidenceState.bodyText.includes("SEC EDGAR") ||
        translatedEvidenceState.bodyText.includes("GDELT") ||
        translatedEvidenceState.bodyText.includes("Public no-key real source manifest") ||
        translatedEvidenceState.bodyText.includes("OFAC Sanctions List Service"),
      passed:
        languageBefore.language === "en" &&
        zhState.title === zhGlobalRiskTitle &&
        frState.title === frGlobalRiskTitle &&
        languageAfter.language === "en" &&
        translatedGraphState.bodyText.includes("Advanced Micro Devices") &&
        translatedGraphState.bodyText.includes("中国台湾") &&
        translatedGraphState.bodyText.includes("Hon Hai Precision Industry") &&
        (
          translatedEvidenceState.bodyText.includes("SEC EDGAR") ||
          translatedEvidenceState.bodyText.includes("GDELT") ||
          translatedEvidenceState.bodyText.includes("Public no-key real source manifest") ||
          translatedEvidenceState.bodyText.includes("OFAC Sanctions List Service")
        ),
    });

    await navigate(client, `${webUrl}#shock-simulator`);
    const before = await waitFor(client, () => shockState(client), (state) => state.hasImpact && Number(state.severity) === 72);
    const rect = await evaluate(client, `(() => {
      const input = document.querySelector('input[type="range"]');
      const rect = input.getBoundingClientRect();
      const min = Number(input.min || 0);
      const max = Number(input.max || 100);
      const target = 95;
      return { x: rect.left + rect.width * ((target - min) / (max - min)), y: rect.top + rect.height / 2 };
    })()`);
    await client.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: rect.x, y: rect.y });
    await client.send("Input.dispatchMouseEvent", { type: "mousePressed", x: rect.x, y: rect.y, button: "left", clickCount: 1 });
    await client.send("Input.dispatchMouseEvent", { type: "mouseReleased", x: rect.x, y: rect.y, button: "left", clickCount: 1 });
    let after = await waitFor(
      client,
      () => shockState(client),
      (state) => Number(state.severity) >= 90 && state.impactScore !== before.impactScore,
      5000,
    ).catch(() => null);
    if (!after) {
      await evaluate(client, `(() => {
        const input = document.querySelector('input[type="range"]');
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        setter.call(input, '95');
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
      })()`);
      after = await waitFor(
        client,
        () => shockState(client),
        (state) => Number(state.severity) >= 90 && state.impactScore !== before.impactScore,
      );
    }
    checks.push({
      page: "Shock Simulator local state",
      beforeSeverity: Number(before.severity),
      afterSeverity: Number(after.severity),
      beforeImpact: before.impactScore,
      afterImpact: after.impactScore,
      hasOffset: after.hasOffset,
      hasTransmissionGraph: after.hasTransmissionGraph,
      layoutOverlapCount: after.layoutOverlapCount,
      passed:
        Number(after.severity) >= 90 &&
        after.impactScore !== before.impactScore &&
        after.hasOffset &&
        after.hasTransmissionGraph &&
        after.layoutOverlapCount === 0,
    });

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 390,
      height: 844,
      deviceScaleFactor: 2,
      mobile: true,
    });
    await navigate(client, `${webUrl}#graph-explorer`);
    const mobile = await waitFor(client, () => pageState(client), (state) => state.title === "Graph Explorer");
    checks.push({
      page: "mobile Graph Explorer",
      title: mobile.title,
      overflowSafe: mobile.overflowSafe,
      graphNodeCount: mobile.graphNodeCount,
      flowNodeCount: mobile.flowNodeCount,
      flowEdgeCount: mobile.flowEdgeCount,
      layoutOverlapCount: mobile.layoutOverlapCount,
      passed:
        mobile.title === "Graph Explorer" &&
        mobile.overflowSafe &&
        mobile.graphNodeCount >= 2 &&
        mobile.flowNodeCount >= 2 &&
        mobile.flowEdgeCount >= 1 &&
        mobile.layoutOverlapCount === 0,
    });
    }
  } finally {
    if (client) client.close();
    chrome.kill();
    await waitForExit(chrome);
    await rm(profileDir, { recursive: true, force: true }).catch(() => undefined);
  }

  const report = { url: webUrl, apiBase, smokeMode, bestEffort: deployedBestEffort, checkedAt: new Date().toISOString(), checks };
  await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");

  const failures = checks.filter((check) => !check.passed);
  if (failures.length > 0) {
    console.error(JSON.stringify(report, null, 2));
    if (deployedBestEffort) {
      console.warn(`Browser smoke had ${failures.length} failure(s) in deployed best-effort mode. Report: ${reportPath}`);
      return;
    }
    process.exit(1);
  }
  console.log(`Browser smoke passed: ${checks.length} checks. Report: ${reportPath}`);
}

async function assertWebServer() {
  const response = await fetch(webUrl);
  if (!response.ok) {
    throw new Error(`Web server is not ready at ${webUrl}: ${response.status}`);
  }
}

async function fetchApiJson(pathname, init = undefined) {
  const url = `${apiBase}${pathname}`;
  try {
    const response = await fetch(url, {
      headers: { "content-type": "application/json" },
      ...init,
    });
    const bodyText = await response.text();
    let body = null;
    try {
      body = bodyText ? JSON.parse(bodyText) : null;
    } catch {
      body = null;
    }
    return {
      ok: response.ok,
      status: response.status,
      body,
      bodyPrefix: bodyText.slice(0, 160),
      url,
    };
  } catch (error) {
    return {
      ok: false,
      status: null,
      body: null,
      error: String(error),
      url,
    };
  }
}

function isSuccessfulEnvelope(result) {
  return Boolean(result?.status === 200 && result?.body?.status === "success" && result?.body?.data);
}

function textExcerpt(text, terms) {
  const normalized = String(text ?? "").replace(/\s+/g, " ").trim();
  const indexes = terms
    .map((term) => normalized.indexOf(term))
    .filter((index) => index >= 0)
    .sort((left, right) => left - right);
  const start = Math.max(0, (indexes[0] ?? 0) - 120);
  return normalized.slice(start, start + 700);
}

async function navigate(client, url) {
  await client.send("Page.navigate", { url });
  const targetUrl = new URL(url);
  await waitFor(
    client,
    () => evaluate(client, "window.location.href"),
    (href) => {
      try {
        const current = new URL(String(href));
        return current.origin === targetUrl.origin && current.pathname === targetUrl.pathname;
      } catch {
        return false;
      }
    },
    30000,
  );
  const expectedHash = new URL(url).hash;
  if (expectedHash) {
    await evaluate(client, `(() => {
      const nextUrl = ${JSON.stringify(url)};
      const oldUrl = window.location.href;
      const next = new URL(nextUrl);
      if (window.location.href !== nextUrl) {
        window.history.pushState(null, '', next.pathname + next.search + next.hash);
      }
      if (window.location.hash !== ${JSON.stringify(expectedHash)}) {
        window.location.hash = ${JSON.stringify(expectedHash)};
      }
      window.dispatchEvent(new HashChangeEvent('hashchange', { oldURL: oldUrl, newURL: window.location.href }));
      const pageId = ${JSON.stringify(expectedHash.replace(/^#/, ""))};
      document.querySelector('[data-page-id="' + pageId + '"]')?.click();
    })()`);
    await sleep(100);
  }
  await waitFor(client, () => pageState(client), (state) => state.title.length > 0, 30000);
}

async function pageState(client) {
  return evaluate(client, `(() => {
    const root = document.documentElement;
    return {
      title: document.querySelector('h1')?.textContent?.trim() ?? '',
      navCount: document.querySelectorAll('.nav-button').length,
      firstNavId: document.querySelector('.nav-button')?.dataset?.pageId ?? '',
      modeText: Array.from(document.querySelectorAll('.mode-strip')).map((item) => item.textContent?.trim() ?? '').join(' | '),
      lineageText: document.querySelector('.data-lineage-banner')?.textContent?.trim() ?? '',
      text: document.body?.innerText ?? '',
      graphNodeCount: document.querySelectorAll('.risk-flow-node').length,
      flowNodeCount: document.querySelectorAll('.react-flow__node').length,
      flowEdgeCount: document.querySelectorAll('.react-flow__edge, .risk-flow-link-node').length,
      layoutOverlapCount: Math.max(0, ...Array.from(document.querySelectorAll('.risk-flow-render-metrics')).map((item) => Number(item.dataset.layoutOverlapCount ?? 0))),
      overflowSafe: root ? root.scrollWidth <= window.innerWidth + 1 : false
    };
  })()`);
}

async function graphV2State(client) {
  return evaluate(client, `(() => {
    const text = document.body?.innerText ?? '';
    return {
      title: document.querySelector('h1')?.textContent?.trim() ?? '',
      text,
      graphNodeCount: document.querySelectorAll('.risk-flow-node').length,
      flowNodeCount: document.querySelectorAll('.react-flow__node').length,
      flowEdgeCount: document.querySelectorAll('.react-flow__edge, .risk-flow-link-node').length,
      hasV2Title: text.includes('Graph Explorer v2'),
      hasV3ModeSelector: text.includes('View mode selector') && text.includes('Matrix') && text.includes('Evidence') && text.includes('Source Coverage') && text.includes('Node Catalog'),
      hasLegend: text.includes('Legend'),
      hasLayerControls: text.includes('Layer controls'),
      hasFixtureWarning: text.includes('fixture_graph:not_production_ready'),
      hasEvidenceContextSafety: text.includes('This is not a supply-chain dependency edge.'),
      layoutOverlapCount: Math.max(0, ...Array.from(document.querySelectorAll('.risk-flow-render-metrics')).map((item) => Number(item.dataset.layoutOverlapCount ?? 0))),
    };
  })()`);
}

async function shockState(client) {
  return evaluate(client, `(() => {
    const text = document.body?.innerText ?? '';
    const severity = document.querySelector('input[type="range"]')?.value ?? '';
    const resultValues = Array.from(document.querySelectorAll('.big-result strong')).map((item) => item.textContent?.trim() ?? '');
    const impactScore = resultValues[2] ?? resultValues[0] ?? '';
    const layoutOverlapCount = Math.max(0, ...Array.from(document.querySelectorAll('.risk-flow-render-metrics')).map((item) => Number(item.dataset.layoutOverlapCount ?? 0)));
    return {
      severity,
      impactScore,
      layoutOverlapCount,
      hasImpact: text.includes('Gross impact') && text.includes('Net impact'),
      hasOffset: text.includes('Mitigation offset') && text.includes('No dollar offset'),
      hasTransmissionGraph: text.includes('Dynamic transmission path') && document.querySelectorAll('.risk-flow-node').length >= 2
    };
  })()`);
}

async function pageLanguageState(client) {
  return evaluate(client, `(() => {
    return {
      language: document.querySelector('.page-language-select')?.value ?? '',
      title: document.querySelector('h1')?.textContent?.trim() ?? '',
      htmlLang: document.documentElement.lang,
      navText: Array.from(document.querySelectorAll('.nav-label')).map((item) => item.textContent?.trim() ?? '').join(' | '),
      panelText: Array.from(document.querySelectorAll('.panel-title')).map((item) => item.textContent?.trim() ?? '').join(' | '),
      bodyText: document.body?.innerText ?? ''
    };
  })()`);
}

async function setPageLanguage(client, language) {
  await evaluate(client, `(() => {
    const select = document.querySelector('.page-language-select');
    select.value = '${language}';
    select.dispatchEvent(new Event('change', { bubbles: true }));
  })()`);
}

async function evaluate(client, expression) {
  const result = await client.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    const exception = result.exceptionDetails.exception;
    throw new Error(
      exception?.description
        ?? exception?.value
        ?? result.exceptionDetails.text
        ?? "Runtime.evaluate failed",
    );
  }
  return result.result.value;
}

async function waitFor(client, read, predicate, timeout = 30000) {
  const startedAt = Date.now();
  let last;
  while (Date.now() - startedAt < timeout) {
    last = await read();
    if (predicate(last)) return last;
    await sleep(100);
  }
  throw new Error(`Timed out waiting for browser condition. Last state: ${JSON.stringify(last)}`);
}

async function newPage(port) {
  const response = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" });
  if (!response.ok) {
    throw new Error(`Unable to create Chrome target: ${response.status}`);
  }
  const target = await response.json();
  return target.webSocketDebuggerUrl;
}

async function waitForChrome(port) {
  const startedAt = Date.now();
  let lastError;
  while (Date.now() - startedAt < 10000) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (response.ok) return;
    } catch (error) {
      lastError = error;
    }
    await sleep(100);
  }
  throw new Error(`Chrome DevTools did not become ready: ${lastError?.message ?? "timeout"}`);
}

async function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      server.close(() => resolve(address.port));
    });
  });
}

function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const candidates = os.platform() === "win32"
    ? [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
      ]
    : [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
      ];
  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate;
  }
  throw new Error("Chrome or Edge was not found. Set CHROME_PATH to run browser smoke.");
}

class CdpClient {
  constructor(url) {
    this.url = url;
    this.id = 1;
    this.pending = new Map();
    this.socket = null;
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.socket = new WebSocket(this.url);
      this.socket.addEventListener("open", resolve, { once: true });
      this.socket.addEventListener("error", reject, { once: true });
      this.socket.addEventListener("message", (event) => {
        const message = JSON.parse(event.data);
        if (!message.id) return;
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(message.error.message));
        else pending.resolve(message.result ?? {});
      });
    });
  }

  send(method, params = {}) {
    const id = this.id++;
    const payload = JSON.stringify({ id, method, params });
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.socket.send(payload);
    });
  }

  close() {
    this.socket?.close();
  }
}

main().catch((error) => {
  console.error(error);
  if (deployedBestEffort) {
    console.warn("Browser smoke did not complete in deployed best-effort mode.");
    process.exit(0);
  }
  process.exit(1);
});
