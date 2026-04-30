import type {
  ApiEnvelope,
  CausalEvidenceBoardData,
  CompanyRisk360Data,
  GlobalRiskCockpitData,
  GraphExplorerData,
  GraphVersionStudioData,
  PathExplainerData,
  RiskLevel,
  ShockAffectedPath,
  ShockSimulationInput,
  ShockSimulationResult,
  SystemHealthData,
} from "@supply-risk/shared-types";

export interface SupplyRiskApiClientOptions {
  baseUrl?: string;
  useMockFallback?: boolean;
  fetcher?: typeof fetch;
}

export interface SupplyRiskApiClient {
  readonly mode: "mock" | "real";
  getGlobalRiskCockpit(): Promise<GlobalRiskCockpitData>;
  getGraphExplorer(): Promise<GraphExplorerData>;
  getCompanyRisk360(): Promise<CompanyRisk360Data>;
  getPathExplainer(): Promise<PathExplainerData>;
  runShockSimulation(input: ShockSimulationInput): Promise<ShockSimulationResult>;
  getCausalEvidenceBoard(): Promise<CausalEvidenceBoardData>;
  getGraphVersionStudio(): Promise<GraphVersionStudioData>;
  getSystemHealthCenter(): Promise<SystemHealthData>;
}

export interface SupplyRiskMockData {
  globalRiskCockpit: GlobalRiskCockpitData;
  graphExplorer: GraphExplorerData;
  companyRisk360: CompanyRisk360Data;
  pathExplainer: PathExplainerData;
  causalEvidenceBoard: CausalEvidenceBoardData;
  graphVersionStudio: GraphVersionStudioData;
  systemHealthCenter: SystemHealthData;
}

interface RequestJsonOptions extends Required<Pick<SupplyRiskApiClientOptions, "useMockFallback" | "fetcher">> {
  setEffectiveMode: (mode: "mock" | "real") => void;
}

const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

const riskLevelForScore = (score: number): RiskLevel => {
  if (score >= 88) return "critical";
  if (score >= 74) return "severe";
  if (score >= 58) return "elevated";
  if (score >= 40) return "guarded";
  return "low";
};

const mockData: SupplyRiskMockData = {
  globalRiskCockpit: {
    lastUpdated: "2026-04-30 08:18 CDT",
    operatingMode: "mock",
    metrics: [
      {
        id: "global-index",
        label: "Global risk index",
        value: 78,
        unit: "/100",
        delta: 6.4,
        trend: "up",
        level: "severe",
        detail: "Port congestion and rare earth exposure raised the composite index.",
      },
      {
        id: "watched-suppliers",
        label: "Suppliers watched",
        value: 12840,
        displayValue: "12.8k",
        delta: 2.1,
        trend: "up",
        level: "guarded",
        detail: "Expanded coverage across tier-2 electronics and chemicals.",
      },
      {
        id: "revenue-at-risk",
        label: "Revenue at risk",
        value: 34800000000,
        displayValue: "$34.8B",
        delta: 9.8,
        trend: "up",
        level: "severe",
        detail: "Near-term risk concentrated in semiconductors and battery inputs.",
      },
      {
        id: "model-confidence",
        label: "Model confidence",
        value: 91,
        unit: "%",
        delta: 1.2,
        trend: "up",
        level: "low",
        detail: "Evidence coverage improved after graph build 2026.04.30-candidate.",
      },
    ],
    hotspots: [
      {
        id: "taiwan-strait",
        label: "Taiwan Strait",
        region: "East Asia",
        level: "critical",
        score: 92,
        x: 73,
        y: 48,
        drivers: ["Semiconductor bottleneck", "Naval routing alerts", "Insurance spread widening"],
      },
      {
        id: "suez-red-sea",
        label: "Suez / Red Sea",
        region: "MENA",
        level: "severe",
        score: 81,
        x: 53,
        y: 51,
        drivers: ["Container reroutes", "Freight rate shock", "Lead-time variance"],
      },
      {
        id: "panama-canal",
        label: "Panama Canal",
        region: "Central America",
        level: "elevated",
        score: 64,
        x: 29,
        y: 57,
        drivers: ["Drought restrictions", "Slot scarcity"],
      },
      {
        id: "rhine-industrial",
        label: "Rhine Industrial Belt",
        region: "Europe",
        level: "guarded",
        score: 47,
        x: 49,
        y: 39,
        drivers: ["Water-level watch", "Chemical feedstock sensitivity"],
      },
    ],
    incidents: [
      {
        id: "inc-1029",
        title: "Foundry wafer allocation tightens after rolling power curbs",
        region: "East Asia",
        level: "critical",
        startedAt: "2026-04-30T06:10:00-05:00",
        affectedCompanies: 142,
        signalStrength: 0.94,
      },
      {
        id: "inc-1027",
        title: "Container dwell time exceeds 7-day threshold on Red Sea diversion lanes",
        region: "MENA",
        level: "severe",
        startedAt: "2026-04-30T04:40:00-05:00",
        affectedCompanies: 88,
        signalStrength: 0.86,
      },
      {
        id: "inc-1022",
        title: "Battery-grade graphite export checks add customs variance",
        region: "China",
        level: "elevated",
        startedAt: "2026-04-29T22:30:00-05:00",
        affectedCompanies: 64,
        signalStrength: 0.77,
      },
    ],
    corridors: [
      {
        id: "cor-1",
        source: "Shenzhen",
        target: "Los Angeles",
        commodity: "Consumer electronics",
        level: "severe",
        score: 82,
        volumeShare: 0.21,
      },
      {
        id: "cor-2",
        source: "Kaohsiung",
        target: "Rotterdam",
        commodity: "Advanced logic chips",
        level: "critical",
        score: 91,
        volumeShare: 0.34,
      },
      {
        id: "cor-3",
        source: "Jebel Ali",
        target: "Savannah",
        commodity: "Specialty chemicals",
        level: "elevated",
        score: 67,
        volumeShare: 0.14,
      },
    ],
  },
  graphExplorer: {
    selectedNodeId: "c-apex",
    filters: ["company", "supplier", "facility", "commodity", "route", "country"],
    nodes: [
      {
        id: "c-apex",
        label: "Apex Mobility",
        kind: "company",
        level: "severe",
        score: 79,
        x: 49,
        y: 47,
        metadata: { sector: "EV platforms", exposure: "$7.4B", tier: "target" },
      },
      {
        id: "s-orion",
        label: "Orion Cells",
        kind: "supplier",
        level: "critical",
        score: 91,
        x: 27,
        y: 26,
        metadata: { country: "Taiwan", dependency: "42%", tier: 1 },
      },
      {
        id: "f-kaohsiung",
        label: "Kaohsiung Fab 12",
        kind: "facility",
        level: "critical",
        score: 94,
        x: 18,
        y: 62,
        metadata: { utilization: "96%", substitute: "none" },
      },
      {
        id: "m-lithium",
        label: "Lithium carbonate",
        kind: "commodity",
        level: "elevated",
        score: 69,
        x: 74,
        y: 27,
        metadata: { inventory: "31 days", volatility: "high" },
      },
      {
        id: "r-red-sea",
        label: "Red Sea lane",
        kind: "route",
        level: "severe",
        score: 83,
        x: 78,
        y: 63,
        metadata: { delay: "11.6 days", freight: "+38%" },
      },
      {
        id: "cty-vn",
        label: "Vietnam",
        kind: "country",
        level: "guarded",
        score: 46,
        x: 44,
        y: 78,
        metadata: { customs: "stable", labor: "watch" },
      },
    ],
    links: [
      { id: "l1", source: "c-apex", target: "s-orion", label: "tier-1 dependency", weight: 0.8, level: "severe" },
      { id: "l2", source: "s-orion", target: "f-kaohsiung", label: "sole-source fab", weight: 0.9, level: "critical" },
      { id: "l3", source: "c-apex", target: "m-lithium", label: "input exposure", weight: 0.5, level: "elevated" },
      { id: "l4", source: "c-apex", target: "r-red-sea", label: "shipping lane", weight: 0.64, level: "severe" },
      { id: "l5", source: "c-apex", target: "cty-vn", label: "alternate assembly", weight: 0.38, level: "guarded" },
      { id: "l6", source: "r-red-sea", target: "m-lithium", label: "chemical shipments", weight: 0.44, level: "elevated" },
    ],
  },
  companyRisk360: {
    selectedCompanyId: "apex-mobility",
    companies: [
      {
        id: "apex-mobility",
        name: "Apex Mobility",
        ticker: "APXM",
        sector: "Electric vehicles",
        headquarters: "Detroit, US",
        riskScore: 79,
        confidence: 0.91,
        level: "severe",
        revenueAtRiskUsd: 7400000000,
        topDrivers: ["Battery cell sole-source exposure", "Advanced logic dependency", "Red Sea shipping delay"],
        mitigations: ["Qualify Vietnam battery pack line", "Forward-buy power modules", "Lock alternate Gulf routing"],
        suppliers: [
          {
            id: "sup-1",
            supplier: "Orion Cells",
            country: "Taiwan",
            category: "Battery cells",
            spendShare: 0.42,
            dependency: 0.76,
            level: "critical",
            leadTimeDays: 61,
          },
          {
            id: "sup-2",
            supplier: "Kestrel Logic",
            country: "South Korea",
            category: "ADAS silicon",
            spendShare: 0.18,
            dependency: 0.63,
            level: "severe",
            leadTimeDays: 44,
          },
          {
            id: "sup-3",
            supplier: "Nova Harness",
            country: "Mexico",
            category: "Wire harness",
            spendShare: 0.11,
            dependency: 0.38,
            level: "guarded",
            leadTimeDays: 21,
          },
        ],
      },
      {
        id: "northstar-devices",
        name: "Northstar Devices",
        ticker: "NSDV",
        sector: "Medical devices",
        headquarters: "Minneapolis, US",
        riskScore: 63,
        confidence: 0.84,
        level: "elevated",
        revenueAtRiskUsd: 2300000000,
        topDrivers: ["Sterile resin feedstock", "Single port import lane", "Regulatory supplier lock-in"],
        mitigations: ["Pre-clear alternate resin", "Add EU safety stock", "Negotiate expedited validation"],
        suppliers: [
          {
            id: "sup-4",
            supplier: "Helio Polymers",
            country: "Germany",
            category: "Medical resin",
            spendShare: 0.29,
            dependency: 0.58,
            level: "elevated",
            leadTimeDays: 37,
          },
        ],
      },
      {
        id: "terra-grid",
        name: "TerraGrid Storage",
        ticker: "TGRD",
        sector: "Grid batteries",
        headquarters: "Austin, US",
        riskScore: 87,
        confidence: 0.88,
        level: "severe",
        revenueAtRiskUsd: 9800000000,
        topDrivers: ["Graphite export checks", "Cell separator concentration", "Port labor watch"],
        mitigations: ["Dual-source separator film", "Shift graphite blend", "Reserve inland rail capacity"],
        suppliers: [
          {
            id: "sup-6",
            supplier: "Qingdao Graphite Works",
            country: "China",
            category: "Battery graphite",
            spendShare: 0.36,
            dependency: 0.82,
            level: "critical",
            leadTimeDays: 69,
          },
        ],
      },
    ],
  },
  pathExplainer: {
    selectedPathId: "path-apex-fab",
    paths: [
      {
        id: "path-apex-fab",
        title: "Apex Mobility score jump through Taiwan foundry dependency",
        targetCompany: "Apex Mobility",
        scoreMove: 6.8,
        confidence: 0.89,
        summary:
          "Most of the score move flows through a sole-source ADAS silicon path tied to a high-utilization Taiwan foundry.",
        steps: [
          {
            id: "step-1",
            label: "News signal: rolling power curbs",
            kind: "signal",
            level: "severe",
            contribution: 18,
            evidence: "Three independent feeds mention curbs near industrial zones.",
          },
          {
            id: "step-2",
            label: "Kaohsiung Fab 12",
            kind: "facility",
            level: "critical",
            contribution: 31,
            evidence: "Non-substitutable upstream facility with 96% utilization.",
          },
          {
            id: "step-3",
            label: "Orion Cells",
            kind: "supplier",
            level: "critical",
            contribution: 25,
            evidence: "Supplier sits on two high-dependency bills of material.",
          },
          {
            id: "step-4",
            label: "Apex Mobility",
            kind: "company",
            level: "severe",
            contribution: 26,
            evidence: "Inventory buffer is below recovery estimate.",
          },
        ],
      },
      {
        id: "path-red-sea-chemical",
        title: "Specialty chemical delay through Red Sea diversion",
        targetCompany: "Northstar Devices",
        scoreMove: 3.4,
        confidence: 0.82,
        summary: "A moderate score move is driven by route-level delay rather than supplier failure.",
        steps: [
          {
            id: "step-5",
            label: "Freight signal: Red Sea diversion",
            kind: "signal",
            level: "severe",
            contribution: 30,
            evidence: "AIS and carrier guidance agree on reroute duration.",
          },
          {
            id: "step-6",
            label: "Jebel Ali to Savannah",
            kind: "route",
            level: "elevated",
            contribution: 28,
            evidence: "Lane carries 14% of specialty chemical volume.",
          },
          {
            id: "step-7",
            label: "Helio Polymers",
            kind: "supplier",
            level: "elevated",
            contribution: 22,
            evidence: "Supplier has output but route constraints inflate variance.",
          },
          {
            id: "step-8",
            label: "Northstar Devices",
            kind: "company",
            level: "elevated",
            contribution: 20,
            evidence: "Regulatory validation slows substitution.",
          },
        ],
      },
    ],
  },
  causalEvidenceBoard: {
    activeClaimId: "ev-export-controls",
    evidence: [
      {
        id: "ev-export-controls",
        claim: "Graphite export checks increase EV battery cost volatility within 21 days.",
        source: "Customs filings + battery spot price panel",
        method: "diff-in-diff",
        confidence: 0.86,
        level: "severe",
        lastReviewed: "2026-04-30",
        disagreement: 0.18,
      },
      {
        id: "red-sea-latency",
        claim: "Red Sea diversion raises specialty chemical delivery variance by at least 8 days.",
        source: "AIS lane telemetry + carrier bulletins",
        method: "event-study",
        confidence: 0.91,
        level: "elevated",
        lastReviewed: "2026-04-29",
        disagreement: 0.09,
      },
      {
        id: "fab-power-curbs",
        claim: "Rolling power curbs reduce available advanced-node foundry starts.",
        source: "Local grid notices + foundry utilization inference",
        method: "graph-inference",
        confidence: 0.74,
        level: "critical",
        lastReviewed: "2026-04-30",
        disagreement: 0.31,
      },
      {
        id: "rhine-water-level",
        claim: "Rhine low-water alerts materially affect chemical feedstock availability.",
        source: "River gauge records + plant output reports",
        method: "expert",
        confidence: 0.62,
        level: "guarded",
        lastReviewed: "2026-04-28",
        disagreement: 0.27,
      },
    ],
  },
  graphVersionStudio: {
    baselineVersionId: "graph-2026-04-29",
    candidateVersionId: "graph-2026-04-30",
    versions: [
      {
        id: "graph-2026-04-30",
        label: "2026.04.30 candidate",
        createdAt: "2026-04-30 07:44 CDT",
        author: "graph-builder",
        status: "candidate",
        nodes: 4821901,
        edges: 18442250,
        schemaChanges: 3,
        riskScoreDelta: 2.6,
        validationPassRate: 0.982,
      },
      {
        id: "graph-2026-04-29",
        label: "2026.04.29 promoted",
        createdAt: "2026-04-29 08:02 CDT",
        author: "release-bot",
        status: "promoted",
        nodes: 4781122,
        edges: 18199701,
        schemaChanges: 0,
        riskScoreDelta: 0.4,
        validationPassRate: 0.991,
      },
      {
        id: "graph-2026-04-28",
        label: "2026.04.28 archive",
        createdAt: "2026-04-28 08:16 CDT",
        author: "release-bot",
        status: "archived",
        nodes: 4769022,
        edges: 18044219,
        schemaChanges: 1,
        riskScoreDelta: -0.7,
        validationPassRate: 0.988,
      },
    ],
    diffRows: [
      {
        id: "diff-1",
        area: "Supplier identity resolution",
        change: "Merged duplicate battery separator suppliers across JP/KR registries",
        severity: "elevated",
        count: 1842,
      },
      {
        id: "diff-2",
        area: "Facility geocoding",
        change: "Raised confidence threshold for Taiwan advanced-node facilities",
        severity: "severe",
        count: 216,
      },
      {
        id: "diff-3",
        area: "Route ontology",
        change: "Added diversion edge type for Suez / Cape rerouting",
        severity: "guarded",
        count: 93,
      },
    ],
  },
  systemHealthCenter: {
    services: [
      { id: "svc-api", service: "Risk API", owner: "platform", status: "operational", latencyMs: 72, freshnessMinutes: 4, errorRate: 0.001 },
      { id: "svc-graph", service: "Graph query", owner: "graph", status: "operational", latencyMs: 144, freshnessMinutes: 8, errorRate: 0.004 },
      { id: "svc-ingest", service: "Signal ingest", owner: "data", status: "degraded", latencyMs: 391, freshnessMinutes: 17, errorRate: 0.019 },
      { id: "svc-model", service: "Causal scorer", owner: "ml", status: "operational", latencyMs: 218, freshnessMinutes: 12, errorRate: 0.006 },
    ],
    stages: [
      { id: "stage-1", label: "Raw feeds", status: "complete", processed: 2417000, total: 2417000 },
      { id: "stage-2", label: "Entity resolution", status: "running", processed: 3981000, total: 4210000 },
      { id: "stage-3", label: "Graph materialization", status: "queued", processed: 0, total: 1 },
      { id: "stage-4", label: "Causal scoring", status: "queued", processed: 0, total: 1 },
    ],
    logs: [
      "08:18:41 ingest:data-contracts accepted 18 upstream schema changes",
      "08:17:55 resolver:entity-match recalibrated supplier aliases above 0.93 confidence",
      "08:15:20 graph:build queued candidate promotion checks",
      "08:12:02 scorer:causal completed 4,218 company score updates",
    ],
  },
};

const delay = (ms: number) => new Promise((resolve) => globalThis.setTimeout(resolve, ms));

const formatUsd = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
    notation: "compact",
  }).format(value);

async function requestJson<T>(
  baseUrl: string | undefined,
  endpoint: string,
  init: RequestInit | undefined,
  fallback: () => T,
  options: RequestJsonOptions,
): Promise<T> {
  if (!baseUrl) {
    options.setEffectiveMode("mock");
    await delay(80);
    return fallback();
  }

  try {
    const response = await options.fetcher(`${baseUrl.replace(/\/$/, "")}${endpoint}`, {
      headers: { "content-type": "application/json" },
      ...init,
    });
    if (!response.ok) throw new Error(`SupplyRiskAtlas API ${response.status} at ${endpoint}`);
    options.setEffectiveMode("real");
    return unwrapApiPayload<T>(await response.json());
  } catch (error) {
    if (!options.useMockFallback) throw error;
    options.setEffectiveMode("mock");
    await delay(120);
    return fallback();
  }
}

function unwrapApiPayload<T>(payload: unknown): T {
  if (payload && typeof payload === "object" && "status" in payload && "data" in payload) {
    const envelope = payload as ApiEnvelope<T>;
    if (envelope.status !== "success") {
      const message = envelope.errors?.[0]?.message ?? "SupplyRiskAtlas API returned an error envelope.";
      throw new Error(message);
    }
    return envelope.data;
  }
  return payload as T;
}

export const getMockSupplyRiskData = (): SupplyRiskMockData => clone(mockData);

export function calculateMockShockSimulation(input: ShockSimulationInput): ShockSimulationResult {
  const severityFactor = input.severity / 100;
  const durationFactor = Math.min(1.6, input.durationDays / 35);
  const scopeMultiplier = input.scope === "global" ? 1.35 : input.scope === "regional" ? 1.1 : 0.78;
  const commodityMultiplier = input.commodity.includes("semiconductor")
    ? 1.22
    : input.commodity.includes("battery")
      ? 1.16
      : input.commodity.includes("chemical")
        ? 1.08
        : 0.96;
  const regionMultiplier = input.region.includes("Taiwan") ? 1.2 : input.region.includes("Red Sea") ? 1.12 : 1;
  const impactScore = Math.min(
    99,
    Math.round(24 + severityFactor * 48 * scopeMultiplier + durationFactor * 12 * commodityMultiplier + regionMultiplier * 5),
  );
  const affectedCompanies = Math.round(22 + impactScore * scopeMultiplier * 2.7);
  const ebitdaAtRiskUsd = Math.round(impactScore * severityFactor * scopeMultiplier * commodityMultiplier * 90000000);
  const timeToRecoveryDays = Math.round(input.durationDays * (1.15 + severityFactor * 0.9) + scopeMultiplier * 9);
  const pathSeeds: Array<Omit<ShockAffectedPath, "impact" | "level">> = [
    { id: "shock-path-1", label: `${input.region} to North America logistics lane` },
    { id: "shock-path-2", label: `${input.commodity} tier-1 supplier dependency` },
    { id: "shock-path-3", label: "Inventory buffer exhaustion path" },
  ];

  return {
    input,
    impactScore,
    ebitdaAtRiskUsd,
    timeToRecoveryDays,
    affectedCompanies,
    affectedPaths: pathSeeds.map((path, index) => {
      const impact = Math.max(28, impactScore - index * 11);
      return { ...path, impact, level: riskLevelForScore(impact) };
    }),
    recommendations: [
      `Reserve ${input.scope === "global" ? "multi-region" : "alternate"} transport capacity for ${input.commodity}.`,
      `Raise safety stock by ${Math.max(7, Math.round(input.durationDays * 0.42))} days for severe path nodes.`,
      `Trigger executive review for exposures above ${formatUsd(ebitdaAtRiskUsd / Math.max(1, affectedCompanies))} per company.`,
    ],
  };
}

export function createSupplyRiskApiClient(options: SupplyRiskApiClientOptions = {}): SupplyRiskApiClient {
  const baseUrl = options.baseUrl?.trim();
  let effectiveMode: "mock" | "real" = baseUrl ? "real" : "mock";
  const setEffectiveMode = (mode: "mock" | "real") => {
    effectiveMode = mode;
  };
  const clientOptions = {
    useMockFallback: options.useMockFallback ?? true,
    fetcher: options.fetcher ?? ((input, init) => globalThis.fetch(input, init)),
    setEffectiveMode,
  };

  return {
    get mode() {
      return effectiveMode;
    },
    getGlobalRiskCockpit: () =>
      requestJson(
        baseUrl,
        "/dashboard/global-risk-cockpit",
        undefined,
        () => ({ ...clone(mockData.globalRiskCockpit), operatingMode: effectiveMode }),
        clientOptions,
      ),
    getGraphExplorer: () =>
      requestJson(baseUrl, "/dashboard/graph-explorer", undefined, () => clone(mockData.graphExplorer), clientOptions),
    getCompanyRisk360: () =>
      requestJson(baseUrl, "/dashboard/company-risk-360", undefined, () => clone(mockData.companyRisk360), clientOptions),
    getPathExplainer: () =>
      requestJson(baseUrl, "/dashboard/path-explainer", undefined, () => clone(mockData.pathExplainer), clientOptions),
    runShockSimulation: (input) =>
      requestJson(
        baseUrl,
        "/dashboard/shock-simulator",
        { method: "POST", body: JSON.stringify(input) },
        () => calculateMockShockSimulation(input),
        clientOptions,
      ),
    getCausalEvidenceBoard: () =>
      requestJson(baseUrl, "/dashboard/causal-evidence-board", undefined, () => clone(mockData.causalEvidenceBoard), clientOptions),
    getGraphVersionStudio: () =>
      requestJson(baseUrl, "/dashboard/graph-version-studio", undefined, () => clone(mockData.graphVersionStudio), clientOptions),
    getSystemHealthCenter: () =>
      requestJson(baseUrl, "/dashboard/system-health-center", undefined, () => clone(mockData.systemHealthCenter), clientOptions),
  };
}
