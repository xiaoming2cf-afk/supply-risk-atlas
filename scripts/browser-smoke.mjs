import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, rm, writeFile } from "node:fs/promises";
import net from "node:net";
import os from "node:os";
import path from "node:path";

const root = process.cwd();
const webUrl = process.env.SUPPLY_RISK_WEB_URL ?? "http://127.0.0.1:3000";
const expectedMode = process.env.SUPPLY_RISK_EXPECT_MODE;
const apiUrl = process.env.SUPPLY_RISK_API_URL ?? new URL("/api/v1", webUrl).toString();
const apiUrlLiteral = JSON.stringify(apiUrl.replace(/\/$/, ""));
const artifactDir = path.join(root, "artifacts", "browser-smoke");
const reportPath = path.join(artifactDir, "report.json");

const pages = [
  ["System Health Center", "#system-health-center"],
  ["Global Risk Cockpit", "#global-risk-cockpit"],
  ["Graph Explorer", "#graph-explorer"],
  ["Entity Risk 360", "#company-risk-360"],
  ["Prediction Center", "#prediction-center"],
  ["Path Analysis", "#path-analysis"],
  ["Country Lens", "#country-lens"],
  ["Shock Simulator", "#shock-simulator"],
  ["Causal Evidence Board", "#causal-evidence-board"],
];

const zhGlobalRiskTitle = "\u5168\u7403\u98ce\u9669\u9a7e\u9a76\u8231";
const zhGraphExplorerLabel = "\u56fe\u8c31\u63a2\u7d22\u5668";
const frGlobalRiskTitle = "Poste de pilotage des risques mondiaux";
const frGraphExplorerLabel = "Explorateur de graphe";

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

    await navigate(client, `${webUrl}#system-health-center`);
    const healthState = await waitFor(
      client,
      () => pageState(client),
      (state) =>
        state.title === "System Health Center" &&
        (
          state.text.includes("Source registry") ||
          state.text.includes("Data temporarily unavailable") ||
          state.text.includes("Public data unavailable")
        ),
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
    checks.push({
      page: "System Health Center public route",
      title: healthState.title,
      firstNavId: healthState.firstNavId,
      hasRegistryEvidence: healthHasRegistryEvidence,
      hasControlledDegradedState: healthHasControlledDegradedState,
      passed:
        healthState.title === "System Health Center" &&
        healthState.firstNavId === "system-health-center" &&
        (healthHasRegistryEvidence || healthHasControlledDegradedState),
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
          body: JSON.stringify({ region: 'China Taiwan Province semiconductor corridor', commodity: 'advanced semiconductor components', severity: 95, durationDays: 28, scope: 'regional' })
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
      for (const [, hash] of pages.filter(([, hash]) => hash !== "#shock-simulator")) {
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
          body: JSON.stringify({ region: 'China Taiwan Province semiconductor corridor', commodity: 'advanced semiconductor components', severity: 95, durationDays: 28, scope: 'regional' })
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
        state.text.includes("中国台湾省"),
    );
    checks.push({
      page: "Country Lens available countries and selected lens",
      availableCountryCount: countryLensApi.data?.availableCountries?.length ?? 0,
      selectedCountry: countryLensApi.data?.countryLens?.countryCode,
      passed:
        countryLensState.title === "Country Lens" &&
        countryLensState.text.includes("Available countries") &&
        countryLensState.text.includes("中国台湾省") &&
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
        state.bodyText.includes("中国台湾省") &&
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
        translatedGraphState.bodyText.includes("中国台湾省") &&
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
        translatedGraphState.bodyText.includes("中国台湾省") &&
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

  const report = { url: webUrl, checkedAt: new Date().toISOString(), checks };
  await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");

  const failures = checks.filter((check) => !check.passed);
  if (failures.length > 0) {
    console.error(JSON.stringify(report, null, 2));
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

async function navigate(client, url) {
  await client.send("Page.navigate", { url });
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
  process.exit(1);
});
