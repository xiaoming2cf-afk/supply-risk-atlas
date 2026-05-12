import type { GraphLink, GraphNode, GraphNodeKind } from "@supply-risk/shared-types";

export type GraphLayerCategory =
  | "dependency"
  | "supply"
  | "policy"
  | "event"
  | "substitution"
  | "trade"
  | "route"
  | "hazard"
  | "sanctions"
  | "simulation_trace";

export const graphLayerCategories: GraphLayerCategory[] = [
  "dependency",
  "supply",
  "policy",
  "event",
  "substitution",
  "trade",
  "route",
  "hazard",
  "sanctions",
  "simulation_trace",
];

export const defaultGraphLayerSet = new Set<GraphLayerCategory>(graphLayerCategories);

export function edgeLayerCategory(link: GraphLink): GraphLayerCategory {
  const text = `${link.edgeType ?? ""} ${link.edgeRole ?? ""} ${link.label ?? ""}`.toLowerCase();
  if (text.includes("simulation") || text.includes("trace") || text.includes("shock")) return "simulation_trace";
  if (text.includes("policy") || text.includes("governance") || text.includes("compliance")) return "policy";
  if (text.includes("event") || text.includes("incident") || text.includes("pressure")) return "event";
  if (text.includes("substitut") || text.includes("alternative")) return "substitution";
  if (text.includes("trade") || text.includes("custom") || text.includes("export") || text.includes("import")) return "trade";
  if (text.includes("hazard") || text.includes("earthquake") || text.includes("exposure")) return "hazard";
  if (text.includes("sanction") || text.includes("screening") || text.includes("restricted party")) return "sanctions";
  if (text.includes("route") || text.includes("lane") || text.includes("carrier") || text.includes("logistic")) return "route";
  if (text.includes("supply") || text.includes("supplier") || text.includes("flow") || text.includes("facility")) return "supply";
  return "dependency";
}

export function filterGraphLinks(
  links: GraphLink[],
  options: {
    enabledLayers: Set<GraphLayerCategory>;
    hideLowConfidence: boolean;
  },
) {
  return links.filter((link) => {
    if (!options.enabledLayers.has(edgeLayerCategory(link))) return false;
    if (options.hideLowConfidence && (link.confidence ?? 1) < 0.45) return false;
    return true;
  });
}

export function graphNodeMatchesSearch(node: GraphNode, query: string, kind: GraphNodeKind | "all") {
  const normalizedQuery = query.trim().toLowerCase();
  if (!normalizedQuery) return true;
  if (kind !== "all" && node.kind !== kind) return false;
  const metadataValues = Object.values(node.metadata ?? {}).map((value) => String(value).toLowerCase());
  const searchable = [
    node.id,
    node.label,
    node.kind,
    node.countryCode ?? "",
    node.entityType ?? "",
    node.displayName ?? "",
    node.geoId ?? "",
    node.provinceCode ?? "",
    node.sourceCountryCode ?? "",
    ...metadataValues,
  ];
  return searchable.some((value) => value.toLowerCase().includes(normalizedQuery));
}

export function findFirstGraphSearchMatch(nodes: GraphNode[], query: string, kind: GraphNodeKind | "all") {
  const normalizedQuery = query.trim();
  if (!normalizedQuery) return undefined;
  return nodes.find((node) => graphNodeMatchesSearch(node, normalizedQuery, kind));
}

export function graphNodeCountry(node: GraphNode) {
  return (node.countryCode ?? String(node.metadata?.country ?? "global")).toUpperCase();
}
