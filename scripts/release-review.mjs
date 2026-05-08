const apiUrl = normalizeBaseUrl(process.env.SUPPLY_RISK_API_URL ?? "http://127.0.0.1:8000/api/v1", "SUPPLY_RISK_API_URL");
const webUrl = normalizeBaseUrl(process.env.SUPPLY_RISK_WEB_URL ?? "http://localhost:3000", "SUPPLY_RISK_WEB_URL");
const requireWeb = process.env.SUPPLY_RISK_REVIEW_SKIP_WEB !== "1";
const minCountries = Number(process.env.SUPPLY_RISK_REVIEW_MIN_COUNTRIES ?? 150);
const minNodes = Number(process.env.SUPPLY_RISK_REVIEW_MIN_NODES ?? 3000);
const minLinks = Number(process.env.SUPPLY_RISK_REVIEW_MIN_LINKS ?? 6000);

const checks = [];

async function main() {
  const health = await fetchJson(`${apiUrl}/health`, "API health");
  const graph = await fetchJson(`${apiUrl}/dashboard/graph-explorer`, "Graph Explorer payload");
  const expansionNodeKinds = "raw_material,component,product_grade,supplier_tier,factory,warehouse,route_lane,carrier";
  const expansionEdgeTypes = "supplies_to,component_of,input_to,material_processed_into,manufactured_at,stored_at,ships_to,route_leg,handled_at,used_by,substitutes,qualified_alternative_to";
  const expandedGraph = await fetchJson(
    `${apiUrl}/dashboard/graph-explorer?node_kinds=${expansionNodeKinds}&edge_types=${expansionEdgeTypes}&path_direction=both`,
    "Supply-chain expansion payload",
  );
  const predictions = await fetchJson(`${apiUrl}/dashboard/prediction-center`, "Prediction Center payload");
  const scenario = await fetchJson(`${apiUrl}/dashboard/shock-simulator`, "Scenario shock payload", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      region: "China Taiwan Province semiconductor corridor",
      commodity: "advanced semiconductor components",
      severity: 86,
      durationDays: 28,
      scope: "regional",
    }),
  });
  const usgs = await fetchJson(`${apiUrl}/sources/usgs_earthquakes`, "USGS source payload");

  checkHealth(health);
  checkGraphExplorer(graph, expandedGraph);
  checkPredictionCenter(predictions);
  checkScenarioShock(scenario);
  checkUsgsSource(usgs);
  if (requireWeb) await checkWebShell();

  const failed = checks.filter((check) => !check.pass);
  for (const check of checks) {
    const marker = check.pass ? "PASS" : "FAIL";
    console.log(`${marker} ${check.name}${check.detail ? ` - ${check.detail}` : ""}`);
  }
  if (failed.length > 0) {
    console.error(`Release review failed: ${failed.length}/${checks.length} checks failed.`);
    process.exit(1);
  }
  console.log(`Release review passed: ${checks.length} checks.`);
}

function checkHealth(envelope) {
  const data = envelope.data ?? {};
  const metadata = envelope.metadata ?? {};
  addCheck("API envelope is successful", envelope.status === "success" && envelope.mode === "real", `mode=${envelope.mode}`);
  addCheck("API uses real data", data.data_mode === "real" && metadata.data_mode === "real", `metadata=${metadata.data_mode}`);
  addCheck("source count includes all public feeds", Number(metadata.source_count ?? 0) >= 8, `source_count=${metadata.source_count}`);
  addCheck(
    "USGS source is registered in health",
    (data.sources ?? []).some((source) => source.source_id === "usgs_earthquakes"),
    "source_id=usgs_earthquakes",
  );
}

function checkGraphExplorer(envelope, expandedEnvelope) {
  const data = envelope.data ?? {};
  const payloadText = JSON.stringify(data);
  const countries = data.availableCountries ?? data.countryLens?.countries ?? [];
  const graphStats = data.graphStats ?? {};
  const totalNodes = Number(graphStats.totalNodes ?? graphStats.fullNodeCount ?? data.nodes?.length ?? 0);
  const totalLinks = Number(graphStats.totalLinks ?? graphStats.fullEdgeCount ?? data.links?.length ?? 0);
  const paths = data.transmissionPaths ?? [];
  const countryLens = data.countryLens ?? {};
  const expanded = expandedEnvelope?.data ?? {};
  const expandedText = JSON.stringify(expanded);
  const requiredKinds = ["raw_material", "component", "product_grade", "supplier_tier", "factory", "warehouse", "route_lane", "carrier"];
  const requiredEdgeTypes = ["supplies_to", "component_of", "input_to", "material_processed_into", "manufactured_at", "stored_at", "ships_to", "route_leg", "handled_at", "used_by", "substitutes", "qualified_alternative_to"];

  addCheck("Graph Explorer country coverage is broad", countries.length >= minCountries, `countries=${countries.length}`);
  addCheck("Graph Explorer full graph has enough nodes", totalNodes >= minNodes, `nodes=${totalNodes}`);
  addCheck("Graph Explorer full graph has enough links", totalLinks >= minLinks, `links=${totalLinks}`);
  addCheck("CN is available for Country Lens", countries.some((country) => country.code === "CN"), "country=CN");
  addCheck("TW is not exposed as a country", !countries.some((country) => country.code === "TW"), "country=TW absent");
  addCheck("Taiwan is modeled as 中国台湾省", payloadText.includes("中国台湾省"), "province label present");
  addCheck("critical node ranking is populated", (data.criticalNodes ?? []).length >= 12, `critical=${data.criticalNodes?.length ?? 0}`);
  addCheck("transmission paths are populated", paths.length >= 8, `paths=${paths.length}`);
  addCheck("country aggregation edges are populated", (countryLens.countryEdges ?? []).length > 0, `countryEdges=${countryLens.countryEdges?.length ?? 0}`);
  addCheck("country top critical nodes are populated", (countryLens.topCriticalNodes ?? []).length > 0, `topCritical=${countryLens.topCriticalNodes?.length ?? 0}`);
  addCheck("country top paths are populated", (countryLens.topPaths ?? []).length > 0, `topPaths=${countryLens.topPaths?.length ?? 0}`);
  addCheck("country data coverage is populated", Object.keys(countryLens.dataCoverage ?? {}).length > 0, "dataCoverage");
  addCheck(
    "expanded supply-chain node families are exposed",
    requiredKinds.every((kind) => expandedText.includes(`\"kind\":\"${kind}\"`) || expandedText.includes(`\"entityType\":\"${kind}\"`)),
    requiredKinds.join(","),
  );
  addCheck(
    "expanded supply-chain edge families are exposed",
    requiredEdgeTypes.every((edgeType) => expandedText.includes(edgeType) || payloadText.includes(edgeType)),
    requiredEdgeTypes.join(","),
  );
  addCheck(
    "Graph Explorer supports path direction query",
    ["both", undefined].includes(expanded.query?.pathDirection) || expanded.transmissionSummary?.pathDirection === "both",
    `pathDirection=${expanded.query?.pathDirection ?? expanded.transmissionSummary?.pathDirection}`,
  );

  const linkIds = new Set((data.links ?? []).map((link) => link.id));
  const pathStructureOk = paths.every((path) => {
    const nodeSequence = path.nodeSequence ?? [];
    const edgeSequence = path.edgeSequence ?? [];
    const uniqueNodes = new Set(nodeSequence);
    return (
      nodeSequence.length === edgeSequence.length + 1 &&
      uniqueNodes.size === nodeSequence.length &&
      edgeSequence.every((edgeId) => linkIds.has(edgeId) || typeof edgeId === "string")
    );
  });
  addCheck("transmission paths have complete acyclic sequences", pathStructureOk, "nodes=edge+1");
  addCheck(
    "at least one path carries risk_transmits_to evidence",
    paths.some((path) => (path.steps ?? []).some((step) => step.edgeType === "risk_transmits_to" || String(step.evidence ?? "").includes("risk_transmits_to"))),
    "edgeType=risk_transmits_to",
  );
}

function checkPredictionCenter(envelope) {
  const data = envelope.data ?? {};
  const predictions = data.predictions ?? [];
  const saturated = Number(data.saturatedScoreCount ?? predictions.filter((prediction) => Number(prediction.risk_score ?? 0) >= 0.995).length);
  addCheck("Prediction Center is populated", predictions.length > 0, `predictions=${predictions.length}`);
  addCheck("prediction scores are not saturated", saturated === 0, `saturated=${saturated}`);
  addCheck(
    "predictions expose score components",
    predictions.some((prediction) => Object.keys(prediction.score_components ?? prediction.scoreComponents ?? {}).length > 0),
    "score_components",
  );
  addCheck(
    "predictions expose driver contributions",
    predictions.some((prediction) => (prediction.driver_contributions ?? prediction.driverContributions ?? []).length > 0),
    "driver_contributions",
  );
  addCheck(
    "predictions expose path evidence",
    predictions.some((prediction) => (prediction.path_details ?? prediction.pathDetails ?? prediction.top_paths ?? prediction.topPaths ?? []).length > 0),
    "path_details",
  );
  addCheck(
    "prediction mechanism is explicit and unlabeled",
    String(data.predictionForm ?? data.prediction_form ?? "").includes("public_evidence_graph") ||
      predictions.some((prediction) => String(prediction.prediction_form ?? "").includes("public_evidence_graph")),
    String(data.predictionForm ?? data.prediction_form ?? ""),
  );
}


function checkScenarioShock(envelope) {
  const data = envelope.data ?? {};
  const deltas = data.scenario_delta ?? data.scenarioDelta ?? [];
  const changedPaths = data.changedPathDetails ?? data.top_changed_paths ?? data.topChangedPaths ?? [];
  const diagnostics = data.diagnostics ?? {};
  const breakdown = data.offsetBreakdown ?? [];
  const requiredOffsetKeys = [
    "supplierDiversification",
    "routeRedundancy",
    "inventoryRecovery",
    "substitutionReadiness",
    "countryResilience",
    "evidenceCoverage",
  ];
  const overlay = data.scenarioGraphOverlay ?? {};
  const gross = Number(data.grossImpactScore ?? data.impactScore ?? 0);
  const net = Number(data.netImpactScore ?? data.impactScore ?? 0);
  const offsetPct = Number(data.offsetAmountPct ?? 0);
  addCheck("Scenario shock returns risk deltas", deltas.length > 0, `deltas=${deltas.length}`);
  addCheck("Scenario shock returns changed paths", changedPaths.length > 0, `paths=${changedPaths.length}`);
  addCheck("Scenario shock computes gross and net impact", gross >= net && gross > 0 && net > 0, `gross=${gross} net=${net}`);
  addCheck("Scenario shock offset cap is enforced", offsetPct >= 0 && offsetPct <= 0.45, `offset=${offsetPct}`);
  addCheck(
    "Scenario shock offset breakdown is complete",
    requiredOffsetKeys.every((key) => breakdown.some((item) => item.key === key && item.evidenceRef && item.dataSource && Number(item.confidence) > 0)),
    `keys=${breakdown.map((item) => item.key).join(",")}`,
  );
  addCheck(
    "Scenario shock uses deterministic public-evidence calculation",
    String(diagnostics.calculationMode ?? "").includes("deterministic_public_evidence_mitigation_offset"),
    String(diagnostics.calculationMode ?? ""),
  );
  addCheck(
    "Scenario shock avoids fictional monetary offset",
    Number(data.ebitdaAtRiskUsd ?? 0) === 0 && String(data.mitigationStandard?.monetaryAmountPolicy ?? diagnostics.monetaryOffsetMode ?? "").includes("No dollar offset"),
    String(data.mitigationStandard?.monetaryAmountPolicy ?? diagnostics.monetaryOffsetMode ?? ""),
  );
  addCheck("Scenario shock company impact is populated", (data.companyImpact ?? []).length > 0, `companies=${data.companyImpact?.length ?? 0}`);
  addCheck("Scenario shock country impact is populated", (data.countryImpact ?? []).length > 0, `countries=${data.countryImpact?.length ?? 0}`);
  addCheck(
    "Scenario shock dynamic path overlay is populated",
    (overlay.nodes ?? []).length > 0 && (overlay.links ?? []).length > 0 && (overlay.activePathEdgeIds ?? []).length > 0,
    `nodes=${overlay.nodes?.length ?? 0} links=${overlay.links?.length ?? 0}`,
  );
  addCheck(
    "Scenario shock changed paths have complete acyclic sequences",
    changedPaths.every((path) => {
      const nodeSequence = path.nodeSequence ?? [];
      const edgeSequence = path.edgeSequence ?? [];
      return nodeSequence.length === edgeSequence.length + 1 && new Set(nodeSequence).size === nodeSequence.length;
    }),
    "nodes=edge+1",
  );
}
function checkUsgsSource(envelope) {
  const sources = envelope.data?.sources ?? [];
  const source = sources.find((candidate) => candidate.id === "usgs_earthquakes" || candidate.source_id === "usgs_earthquakes");
  addCheck("USGS source detail is exposed", Boolean(source), "sources/usgs_earthquakes");
  addCheck("USGS source is fresh or partial", ["fresh", "partial"].includes(source?.status), `status=${source?.status}`);
}

async function checkWebShell() {
  const response = await fetch(`${webUrl}/#graph-explorer`);
  const text = await response.text();
  addCheck("web shell responds", response.ok, `status=${response.status}`);
  addCheck("web shell title is present", text.includes("SupplyRiskAtlas"), "title=SupplyRiskAtlas");
  addCheck("web bundle includes graph workbench", text.includes("__next") || text.includes("Graph Explorer"), "Next shell");
}

async function fetchJson(url, label, init = undefined) {
  const response = await fetch(url, { headers: { accept: "application/json", ...(init?.headers ?? {}) }, ...init });
  const text = await response.text();
  if (!response.ok) {
    throw new Error(`${label} failed: HTTP ${response.status} ${text.slice(0, 180)}`);
  }
  return JSON.parse(text);
}

function addCheck(name, pass, detail = "") {
  checks.push({ name, pass: Boolean(pass), detail });
}

function normalizeBaseUrl(value, envName) {
  let parsed;
  try {
    parsed = new URL(value);
  } catch {
    throw new Error(`${envName} must be an absolute http(s) URL.`);
  }
  if (!["http:", "https:"].includes(parsed.protocol)) {
    throw new Error(`${envName} must use http or https.`);
  }
  return parsed.toString().replace(/\/+$/, "");
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
