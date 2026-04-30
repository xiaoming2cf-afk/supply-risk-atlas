import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, rm, writeFile } from "node:fs/promises";
import net from "node:net";
import os from "node:os";
import path from "node:path";

const root = process.cwd();
const webUrl = process.env.SUPPLY_RISK_WEB_URL ?? "http://127.0.0.1:3000";
const expectedMode = process.env.SUPPLY_RISK_EXPECT_MODE;
const apiUrl = process.env.SUPPLY_RISK_API_URL ?? "http://127.0.0.1:8000/api/v1";
const artifactDir = path.join(root, "artifacts", "browser-smoke");
const reportPath = path.join(artifactDir, "report.json");

const pages = [
  ["Global Risk Cockpit", "#global-risk-cockpit"],
  ["Graph Explorer", "#graph-explorer"],
  ["Company Risk 360", "#company-risk-360"],
  ["Path Explainer", "#path-explainer"],
  ["Shock Simulator", "#shock-simulator"],
  ["Causal Evidence Board", "#causal-evidence-board"],
  ["Graph Version Studio", "#graph-version-studio"],
  ["Translator", "#translator"],
  ["System Health Center", "#system-health-center"],
];

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
      checks.push({ page, hash, title: result.title, navCount: result.navCount, passed: result.title === page && result.navCount === pages.length });
    }

    if (expectedMode) {
      const expectedModeText = { real: "API linked", mock: "mock data", fallback: "API fallback" }[expectedMode];
      if (!expectedModeText) throw new Error(`Unsupported SUPPLY_RISK_EXPECT_MODE: ${expectedMode}`);
      await navigate(client, `${webUrl}#global-risk-cockpit`);
      const modeState = await pageState(client);
      const apiDiagnostic = await evaluate(client, `fetch('${apiUrl}/dashboard/global-risk-cockpit', { headers: { 'content-type': 'application/json' } })
        .then(async (response) => ({ ok: response.ok, status: response.status, bodyPrefix: (await response.text()).slice(0, 80) }))
        .catch((error) => ({ error: String(error) }))`);
      const shockDiagnostic = await evaluate(client, `fetch('${apiUrl}/dashboard/shock-simulator', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ region: 'Taiwan Strait', commodity: 'advanced semiconductor components', severity: 95, durationDays: 28, scope: 'regional' })
        })
        .then(async (response) => ({ ok: response.ok, status: response.status, bodyPrefix: (await response.text()).slice(0, 80) }))
        .catch((error) => ({ error: String(error) }))`);
      checks.push({
        page: "runtime data mode",
        expectedMode,
        modeText: modeState.modeText,
        apiDiagnostic,
        shockDiagnostic,
        passed: modeState.modeText.includes(expectedModeText),
      });
    }

    await navigate(client, `${webUrl}#global-risk-cockpit`);
    await evaluate(client, `Array.from(document.querySelectorAll(".nav-button")).find((button) => button.textContent.includes("Graph Explorer"))?.click()`);
    const navClick = await waitFor(client, () => pageState(client), (state) => state.title === "Graph Explorer");
    checks.push({ page: "nav click to Graph Explorer", title: navClick.title, passed: navClick.title === "Graph Explorer" });

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
      passed: Number(after.severity) >= 90 && after.impactScore !== before.impactScore,
    });

    await navigate(client, `${webUrl}#translator`);
    const translatorBefore = await waitFor(client, () => translatorState(client), (state) => state.title === "Translator" && state.hasOutput);
    await evaluate(client, `(() => {
      const selects = document.querySelectorAll('select');
      const target = selects[1];
      target.value = 'fr';
      target.dispatchEvent(new Event('change', { bubbles: true }));
    })()`);
    const translatorAfter = await waitFor(
      client,
      () => translatorState(client),
      (state) => state.output.includes("risque de chaîne d'approvisionnement") && state.targetLanguage === "fr",
    );
    checks.push({
      page: "Translator local state",
      beforeTarget: translatorBefore.targetLanguage,
      afterTarget: translatorAfter.targetLanguage,
      outputPrefix: translatorAfter.output.slice(0, 80),
      passed: translatorAfter.output.includes("risque de chaîne d'approvisionnement"),
    });

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 390,
      height: 844,
      deviceScaleFactor: 2,
      mobile: true,
    });
    await navigate(client, `${webUrl}#system-health-center`);
    const mobile = await waitFor(client, () => pageState(client), (state) => state.title === "System Health Center");
    checks.push({
      page: "mobile System Health Center",
      title: mobile.title,
      overflowSafe: mobile.overflowSafe,
      passed: mobile.title === "System Health Center" && mobile.overflowSafe,
    });
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
  await waitFor(client, () => pageState(client), (state) => state.title.length > 0);
}

async function pageState(client) {
  return evaluate(client, `(() => ({
    title: document.querySelector('h1')?.textContent?.trim() ?? '',
    navCount: document.querySelectorAll('.nav-button').length,
    modeText: Array.from(document.querySelectorAll('.mode-strip')).map((item) => item.textContent?.trim() ?? '').join(' | '),
    text: document.body.innerText,
    overflowSafe: document.documentElement.scrollWidth <= window.innerWidth + 1
  }))()`);
}

async function shockState(client) {
  return evaluate(client, `(() => {
    const text = document.body.innerText;
    const severity = document.querySelector('input[type="range"]')?.value ?? '';
    const impactScore = document.querySelector('.big-result strong')?.textContent?.trim() ?? '';
    return { severity, impactScore, hasImpact: text.includes('Impact score') };
  })()`);
}

async function translatorState(client) {
  return evaluate(client, `(() => {
    const selects = document.querySelectorAll('select');
    const output = document.querySelector('.translation-output')?.textContent?.trim() ?? '';
    return {
      title: document.querySelector('h1')?.textContent?.trim() ?? '',
      sourceLanguage: selects[0]?.value ?? '',
      targetLanguage: selects[1]?.value ?? '',
      output,
      hasOutput: output.length > 0
    };
  })()`);
}

async function evaluate(client, expression) {
  const result = await client.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text ?? "Runtime.evaluate failed");
  }
  return result.result.value;
}

async function waitFor(client, read, predicate, timeout = 10000) {
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
