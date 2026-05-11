import type { RiskLevel, TrendDirection } from "./common";

export type DashboardPageId =
  | "system-health-center"
  | "global-risk-cockpit"
  | "graph-explorer"
  | "company-risk-360"
  | "prediction-center"
  | "path-analysis"
  | "country-lens"
  | "path-explainer"
  | "shock-simulator"
  | "reverse-stress-lab"
  | "intervention-optimizer"
  | "investigation-report"
  | "causal-evidence-board"
  | "graph-version-studio";

export interface DashboardPage {
  id: DashboardPageId;
  label: string;
  shortLabel: string;
  description: string;
}

export const dashboardPages: DashboardPage[] = [
  {
    id: "system-health-center",
    label: "System Health Center",
    shortLabel: "Health",
    description: "Data pipeline, source registry, freshness, API, and graph service health",
  },
  {
    id: "global-risk-cockpit",
    label: "Global Risk Cockpit",
    shortLabel: "Cockpit",
    description: "Live exposure map, risk pressure, and incident queue",
  },
  {
    id: "graph-explorer",
    label: "Graph Explorer",
    shortLabel: "Graph",
    description: "Supplier, facility, commodity, route, and country network",
  },
  {
    id: "company-risk-360",
    label: "Entity Risk 360",
    shortLabel: "Risk 360",
    description: "Fixture-labeled entity risk score, components, evidence refs, and graph context",
  },
  {
    id: "prediction-center",
    label: "Prediction Center",
    shortLabel: "Predict",
    description: "Ensemble risk forecasts, mechanism labels, confidence bands, and evidence paths",
  },
  {
    id: "path-analysis",
    label: "Path Analysis",
    shortLabel: "Paths",
    description: "Top-K transmission paths with hop-by-hop evidence",
  },
  {
    id: "country-lens",
    label: "Country Lens",
    shortLabel: "Country",
    description: "Country risk, critical nodes, data coverage, and cross-border flow",
  },
  {
    id: "shock-simulator",
    label: "Shock Simulator",
    shortLabel: "Simulator",
    description: "Stress test regions, commodities, severity, and recovery",
  },
  {
    id: "reverse-stress-lab",
    label: "Reverse Stress Lab",
    shortLabel: "Reverse",
    description: "Find plausible shock sets that can breach a normalized failure threshold",
  },
  {
    id: "intervention-optimizer",
    label: "Intervention Optimizer",
    shortLabel: "Optimize",
    description: "Budget-constrained fixture graph resilience action selection",
  },
  {
    id: "investigation-report",
    label: "Investigation Report",
    shortLabel: "Report",
    description: "Auditable JSON and Markdown report export with evidence and version metadata",
  },
  {
    id: "causal-evidence-board",
    label: "Causal Evidence Board",
    shortLabel: "Evidence",
    description: "Evidence quality, causal claims, and disagreement tracking",
  },
  {
    id: "graph-version-studio",
    label: "Graph Version Studio",
    shortLabel: "Versions",
    description: "Compare graph builds, schema drift, and promotion readiness",
  },
];

export interface RiskMetric {
  id: string;
  label: string;
  value: number;
  unit?: string;
  displayValue?: string;
  delta: number;
  trend: TrendDirection;
  level: RiskLevel;
  detail: string;
}

export interface Hotspot {
  id: string;
  label: string;
  region: string;
  level: RiskLevel;
  score: number;
  x: number;
  y: number;
  drivers: string[];
}

export interface Incident {
  id: string;
  title: string;
  region: string;
  level: RiskLevel;
  startedAt: string;
  affectedCompanies: number;
  signalStrength: number;
}

export interface CorridorRisk {
  id: string;
  source: string;
  target: string;
  commodity: string;
  level: RiskLevel;
  score: number;
  volumeShare: number;
}

export interface GlobalRiskCockpitData {
  lastUpdated: string;
  operatingMode: "real";
  metrics: RiskMetric[];
  hotspots: Hotspot[];
  incidents: Incident[];
  corridors: CorridorRisk[];
}

export interface EvidenceItem {
  id: string;
  claim: string;
  source: string;
  method: "event-study" | "diff-in-diff" | "expert" | "graph-inference" | "news-signal";
  confidence: number;
  level: RiskLevel;
  lastReviewed: string;
  disagreement: number;
}

export interface CausalEvidenceBoardData {
  evidence: EvidenceItem[];
  activeClaimId: string;
}
