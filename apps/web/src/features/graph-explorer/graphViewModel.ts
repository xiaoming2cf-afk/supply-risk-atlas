import type {
  CountryRiskSummary,
  GraphExplorerData,
  GraphLink,
  GraphNode,
  GraphNodeKind,
  GraphTransmissionPath,
  RiskLevel,
  TransmissionPathStep,
} from "@supply-risk/shared-types";
import {
  filterGraphLinks,
  graphNodeCountry,
  graphNodeMatchesSearch,
  type GraphLayerCategory,
} from "./graphFilters";
import { graphScore, riskLevelRank } from "./graphLayout";

export type GraphViewMode = "overview" | "focus" | "path" | "timeline" | "geo" | "matrix" | "scenario" | "evidence";

export type LegacyGraphExplorerMode =
  | GraphViewMode
  | "supply-chain-flow"
  | "upstream-downstream"
  | "geo-aggregate"
  | "risk-propagation"
  | "event-timeline"
  | "scenario-overlay";

export type GraphFocusDirection = "incoming" | "outgoing" | "both";

export interface GraphVersionMetadata {
  graphVersion: string;
  sourceManifestId: string;
  asOfTime: string;
  warnings: string[];
  fixtureGraph: boolean;
}

export interface GraphViewModelInput {
  graph: GraphExplorerData;
  mode: GraphViewMode;
  selectedNodeId?: string;
  selectedEdgeId?: string | null;
  selectedPathId?: string;
  selectedPathStepIndex: number;
  selectedCountryCode?: string;
  searchQuery: string;
  nodeKind: GraphNodeKind | "all";
  enabledLayers: Set<GraphLayerCategory>;
  confidenceMin: number;
  countryFilter: string;
  evidenceOnly: boolean;
  hideLowConfidence: boolean;
  productFilter: string;
  sourceFilter: string;
  pinnedNodeIds: Set<string>;
  focusDepth: number;
  focusDirection: GraphFocusDirection;
}

export interface GraphViewModel {
  activePath?: GraphTransmissionPath;
  activePathEdgeIds: Set<string>;
  activePathNodeIds: Set<string>;
  activePathNodeIndex: Map<string, number>;
  emptyReason?: string;
  matchedNodeIds: Set<string>;
  renderLimits: { nodeLimit: number; edgeLimit: number };
  selectedCountry?: CountryRiskSummary;
  selectedEdge?: GraphLink;
  selectedNode?: GraphNode;
  selectedPathStep?: TransmissionPathStep;
  totalEligibleEdges: number;
  totalEligibleNodes: number;
  visibleLinks: GraphLink[];
  visibleNodes: GraphNode[];
}

const overviewNodeLimit = 20;
const overviewEdgeLimit = 35;
const focusNodeLimit = 25;
const focusEdgeLimit = 40;
const pathNodeLimit = 35;
const pathEdgeLimit = 40;

export function normalizeGraphViewMode(mode: LegacyGraphExplorerMode): GraphViewMode {
  if (mode === "supply-chain-flow") return "overview";
  if (mode === "upstream-downstream") return "focus";
  if (mode === "risk-propagation") return "path";
  if (mode === "event-timeline") return "timeline";
  if (mode === "geo-aggregate") return "geo";
  if (mode === "scenario-overlay") return "scenario";
  return mode;
}

export function graphViewModeUsesPath(mode: GraphViewMode) {
  return mode === "path" || mode === "timeline";
}

export function graphModeLabel(mode: GraphViewMode) {
  return {
    overview: "Overview",
    focus: "Focus",
    path: "Path",
    timeline: "Timeline",
    geo: "Geo",
    matrix: "Matrix",
    scenario: "Scenario overlay",
    evidence: "Evidence",
  }[mode];
}

export function buildGraphViewModel(input: GraphViewModelInput): GraphViewModel {
  const selectedCountry = selectedCountryForInput(input.graph, input.selectedCountryCode);
  const activePath =
    input.graph.transmissionPaths?.find((path) => path.id === input.selectedPathId) ??
    input.graph.transmissionPaths?.[0];
  const selectedPathStep =
    activePath?.steps[Math.min(input.selectedPathStepIndex, Math.max(0, activePath.steps.length - 1))];
  const activePathNodeIds = new Set(activePath?.nodeSequence ?? []);
  const activePathEdgeIds = new Set(activePath?.edgeSequence ?? []);
  const activePathNodeIndex = new Map((activePath?.nodeSequence ?? []).map((nodeId, index) => [nodeId, index]));
  const matchedNodeIds = new Set(
    input.searchQuery.trim()
      ? input.graph.nodes
          .filter((node) => graphNodeMatchesSearch(node, input.searchQuery, input.nodeKind))
          .map((node) => node.id)
      : [],
  );
  const useSearchFocus = matchedNodeIds.size > 0 && (input.mode === "overview" || input.mode === "focus");
  const searchContext = buildSearchContextGraph(input.graph, matchedNodeIds);
  const baseNodes = input.graph.nodes.filter((node) =>
    graphNodePassesAdvancedFilters(node, input.sourceFilter, input.countryFilter, input.productFilter, input.evidenceOnly),
  );
  const workingNodes = searchContext.nodes.length ? [...baseNodes, ...searchContext.nodes] : baseNodes;
  const baseFilteredLinks = filterGraphLinks(input.graph.links, {
    enabledLayers: input.enabledLayers,
    hideLowConfidence: input.hideLowConfidence,
  });
  const advancedFilteredLinks = baseFilteredLinks.filter((link) =>
    graphLinkPassesAdvancedFilters(link, input.sourceFilter, input.countryFilter, input.confidenceMin, input.evidenceOnly),
  );
  const filteredLinks = searchContext.links.length ? [...advancedFilteredLinks, ...searchContext.links] : advancedFilteredLinks;
  const nodeMap = new Map(workingNodes.map((node) => [node.id, node]));
  const rawLinkMap = new Map([...input.graph.links, ...searchContext.links].map((link) => [link.id, link]));

  if (input.mode === "overview" && matchedNodeIds.size === 0) {
    const overview = buildOverviewGraph({ ...input.graph, nodes: baseNodes, links: advancedFilteredLinks });
    const selectedNode =
      overview.nodes.find((node) => node.id === input.selectedNodeId) ??
      nodeMap.get(input.selectedNodeId ?? "") ??
      overview.nodes[0] ??
      input.graph.nodes[0];
    return {
      activePath,
      activePathEdgeIds: new Set(),
      activePathNodeIds: new Set(),
      activePathNodeIndex: new Map(),
      matchedNodeIds,
      renderLimits: { nodeLimit: overviewNodeLimit, edgeLimit: overviewEdgeLimit },
      selectedCountry,
      selectedEdge: undefined,
      selectedNode,
      selectedPathStep: undefined,
      totalEligibleEdges: overview.links.length,
      totalEligibleNodes: overview.nodes.length,
      visibleLinks: overview.links.slice(0, overviewEdgeLimit),
      visibleNodes: overview.nodes.slice(0, overviewNodeLimit),
    };
  }

  if (input.mode === "geo" && matchedNodeIds.size === 0) {
    const geo = buildGeoGraph({ ...input.graph, nodes: baseNodes, links: advancedFilteredLinks }, selectedCountry?.code);
    if (geo.nodes.length >= 2 && geo.links.length >= 1) {
      return {
        activePath,
        activePathEdgeIds: new Set(),
        activePathNodeIds: new Set(),
        activePathNodeIndex: new Map(),
        matchedNodeIds,
        renderLimits: { nodeLimit: overviewNodeLimit, edgeLimit: overviewEdgeLimit },
        selectedCountry,
        selectedEdge: geo.links.find((link) => link.id === input.selectedEdgeId),
        selectedNode: geo.nodes.find((node) => node.id === input.selectedNodeId) ?? geo.nodes[0],
        selectedPathStep: undefined,
        totalEligibleEdges: geo.links.length,
        totalEligibleNodes: geo.nodes.length,
        visibleLinks: geo.links.slice(0, overviewEdgeLimit),
        visibleNodes: geo.nodes.slice(0, overviewNodeLimit),
      };
    }
  }

  const visibleIds = new Set<string>();
  const addNode = (nodeId: string | undefined) => {
    if (nodeId && nodeMap.has(nodeId)) visibleIds.add(nodeId);
  };
  const addLinkContext = (link: GraphLink) => {
    addNode(link.source);
    addNode(link.target);
  };
  const addNeighborContext = (nodeId: string | undefined, direction: GraphFocusDirection, depth: number) => {
    if (!nodeId) return;
    const frontier = new Set([nodeId]);
    const visited = new Set<string>();
    for (let hop = 0; hop <= Math.max(0, depth); hop += 1) {
      const next = new Set<string>();
      for (const currentId of frontier) {
        if (visited.has(currentId)) continue;
        visited.add(currentId);
        addNode(currentId);
        for (const link of filteredLinks) {
          const followsIncoming = direction !== "outgoing" && link.target === currentId;
          const followsOutgoing = direction !== "incoming" && link.source === currentId;
          if (!followsIncoming && !followsOutgoing) continue;
          addLinkContext(link);
          next.add(followsIncoming ? link.source : link.target);
        }
      }
      frontier.clear();
      next.forEach((nodeId) => frontier.add(nodeId));
    }
  };
  const addPathContext = (path: GraphTransmissionPath | undefined, timelineStepIndex?: number) => {
    if (!path) return;
    const nodeLimit = timelineStepIndex === undefined ? path.nodeSequence.length : Math.min(path.nodeSequence.length, timelineStepIndex + 1);
    const edgeLimit = timelineStepIndex === undefined ? path.edgeSequence.length : Math.min(path.edgeSequence.length, timelineStepIndex);
    path.nodeSequence.slice(0, nodeLimit).forEach(addNode);
    path.edgeSequence.slice(0, edgeLimit).forEach((edgeId) => {
      const link = rawLinkMap.get(edgeId);
      if (link) addLinkContext(link);
    });
  };
  const selectedOrDefaultNodeId =
    input.selectedNodeId ??
    input.graph.selectedNodeId ??
    input.graph.criticalNodes?.[0]?.id ??
    input.graph.nodes[0]?.id;

  if (useSearchFocus) {
    matchedNodeIds.forEach((nodeId) => {
      addNode(nodeId);
      addNeighborContext(nodeId, "both", 1);
    });
  } else if (input.mode === "path") {
    addPathContext(activePath);
  } else if (input.mode === "timeline") {
    addPathContext(activePath, input.selectedPathStepIndex + 1);
  } else if (input.mode === "scenario") {
    input.pinnedNodeIds.forEach(addNode);
    addNeighborContext(selectedOrDefaultNodeId, "both", 1);
  } else if (input.mode === "matrix") {
    for (const node of criticalGraphNodes({ ...input.graph, nodes: baseNodes }).slice(0, overviewNodeLimit)) addNode(node.id);
  } else if (input.mode === "evidence") {
    filteredLinks
      .filter((link) => Boolean(link.sourceId || link.metadata?.source || link.metadata?.source_label))
      .slice(0, focusEdgeLimit)
      .forEach(addLinkContext);
  } else if (input.mode === "geo") {
    addCountryNodeContext(input.graph, filteredLinks, selectedCountry?.code, addNode, addLinkContext);
  } else {
    addNeighborContext(selectedOrDefaultNodeId, input.focusDirection, Math.max(1, input.focusDepth));
  }

  input.pinnedNodeIds.forEach((nodeId) => {
    addNode(nodeId);
    addNeighborContext(nodeId, "both", 1);
  });
  addNode(input.selectedNodeId);
  if (graphViewModeUsesPath(input.mode) && selectedPathStep?.nodeId) addNode(selectedPathStep.nodeId);
  if (visibleIds.size === 0) {
    for (const node of criticalGraphNodes(input.graph).slice(0, overviewNodeLimit)) addNode(node.id);
  }

  const { nodeLimit, edgeLimit } = renderLimitsForMode(input.mode);
  const orderedNodes = workingNodes
    .filter((node) => visibleIds.has(node.id) && (input.nodeKind === "all" || node.kind === input.nodeKind || matchedNodeIds.has(node.id)))
    .sort((a, b) => compareVisibleNodes(a, b, {
      activePathNodeIds,
      matchedNodeIds,
      pinnedNodeIds: input.pinnedNodeIds,
      selectedNodeId: input.selectedNodeId,
      selectedPathStepNodeId: selectedPathStep?.nodeId,
    }));
  const visibleNodes = orderedNodes.slice(0, nodeLimit);
  const visibleNodeIds = new Set(visibleNodes.map((node) => node.id));
  const orderedLinks = filteredLinks
    .filter((link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target))
    .sort((a, b) => compareVisibleLinks(a, b, {
      activePathEdgeIds,
      selectedEdgeId: input.selectedEdgeId,
      selectedNodeId: input.selectedNodeId,
      selectedPathStepEdgeId: selectedPathStep?.edgeId ?? undefined,
    }));
  const visibleLinks = orderedLinks.slice(0, edgeLimit);
  const selectedNode =
    nodeMap.get(input.selectedNodeId ?? "") ??
    visibleNodes.find((node) => matchedNodeIds.has(node.id)) ??
    visibleNodes[0] ??
    input.graph.nodes[0];

  return {
    activePath,
    activePathEdgeIds: graphViewModeUsesPath(input.mode) ? activePathEdgeIds : new Set(),
    activePathNodeIds: graphViewModeUsesPath(input.mode) ? activePathNodeIds : new Set(),
    activePathNodeIndex: graphViewModeUsesPath(input.mode) ? activePathNodeIndex : new Map(),
    emptyReason: input.mode === "scenario" ? "No scenario run overlay is selected." : undefined,
    matchedNodeIds,
    renderLimits: { nodeLimit, edgeLimit },
    selectedCountry,
    selectedEdge: input.selectedEdgeId ? rawLinkMap.get(input.selectedEdgeId) : undefined,
    selectedNode,
    selectedPathStep: graphViewModeUsesPath(input.mode) ? selectedPathStep : undefined,
    totalEligibleEdges: orderedLinks.length,
    totalEligibleNodes: orderedNodes.length,
    visibleLinks,
    visibleNodes,
  };
}

function buildSearchContextGraph(graph: GraphExplorerData, matchedNodeIds: Set<string>) {
  if (matchedNodeIds.size === 0) return { nodes: [] as GraphNode[], links: [] as GraphLink[] };
  const directLinkNodeIds = new Set<string>();
  for (const link of graph.links) {
    if (matchedNodeIds.has(link.source)) directLinkNodeIds.add(link.source);
    if (matchedNodeIds.has(link.target)) directLinkNodeIds.add(link.target);
  }
  const nodes: GraphNode[] = [];
  const links: GraphLink[] = [];
  const nodeMap = new Map(graph.nodes.map((node) => [node.id, node]));
  for (const nodeId of [...matchedNodeIds].slice(0, 3)) {
    if (directLinkNodeIds.has(nodeId)) continue;
    const node = nodeMap.get(nodeId);
    if (!node) continue;
    const sourceLabel = String(node.metadata.source ?? node.metadata.source_id ?? "public evidence source");
    const countryCode = node.countryCode ?? String(node.metadata.country ?? "global");
    const contextId = `search-context:${node.id}`;
    const confidence = Number(node.metadata.confidence ?? 0.5);
    nodes.push({
      id: contextId,
      label: `${sourceLabel} evidence context`,
      kind: "data",
      level: node.level,
      score: graphScore(node.score),
      x: node.x,
      y: node.y,
      metadata: {
        derived_context: true,
        not_supply_chain_dependency: true,
        source: "search_result_metadata",
        source_label: sourceLabel,
        country: countryCode,
      },
      countryCode,
      entityType: "search_context",
      riskScore: node.riskScore ?? node.score,
      centralityScore: 0,
      criticalityScore: 0,
    });
    links.push({
      id: `search-context-link:${node.id}`,
      source: contextId,
      target: node.id,
      label: "evidence-context link",
      weight: 0.25,
      level: node.level,
      edgeType: "evidence_context",
      riskScore: graphScore(node.riskScore ?? node.score),
      confidence: Number.isFinite(confidence) ? confidence : 0.5,
      sourceId: sourceLabel,
      transmissionWeight: 0.25,
      sourceCountry: countryCode,
      targetCountry: countryCode,
      edgeRole: "evidence_context",
      metadata: {
        derived_context: true,
        not_supply_chain_dependency: true,
        source: "search_result_metadata",
        source_label: sourceLabel,
      },
    });
  }
  return { nodes, links };
}

export function criticalGraphNodes(graph: GraphExplorerData): GraphNode[] {
  if (graph.criticalNodes?.length) {
    const byId = new Map(graph.nodes.map((node) => [node.id, node]));
    return graph.criticalNodes.map((node) => byId.get(node.id)).filter((node): node is GraphNode => Boolean(node));
  }
  return [...graph.nodes].sort(
    (a, b) =>
      graphScore(b.criticalityScore ?? b.score) - graphScore(a.criticalityScore ?? a.score) ||
      riskLevelRank(b.level) - riskLevelRank(a.level) ||
      a.label.localeCompare(b.label),
  );
}

function renderLimitsForMode(mode: GraphViewMode) {
  if (mode === "overview" || mode === "geo" || mode === "matrix") return { nodeLimit: overviewNodeLimit, edgeLimit: overviewEdgeLimit };
  if (mode === "focus" || mode === "scenario") return { nodeLimit: focusNodeLimit, edgeLimit: focusEdgeLimit };
  if (mode === "evidence") return { nodeLimit: focusNodeLimit, edgeLimit: focusEdgeLimit };
  return { nodeLimit: pathNodeLimit, edgeLimit: pathEdgeLimit };
}

function graphNodePassesAdvancedFilters(
  node: GraphNode,
  sourceFilter: string,
  countryFilter: string,
  productFilter: string,
  evidenceOnly: boolean,
) {
  if (sourceFilter !== "all" && !nodeSourceTokens(node).includes(sourceFilter)) return false;
  if (countryFilter !== "all" && graphNodeCountry(node) !== countryFilter.toUpperCase()) return false;
  if (productFilter !== "all") {
    const productTokens = [
      node.kind,
      node.entityType ?? "",
      String(node.metadata.product_grade ?? ""),
      String(node.metadata.product_category ?? ""),
      String(node.metadata.commodity_code ?? ""),
      String(node.metadata.category ?? ""),
    ].map((value) => value.toLowerCase());
    if (!productTokens.includes(productFilter.toLowerCase())) return false;
  }
  if (evidenceOnly && nodeEvidenceTokens(node).length === 0) return false;
  return true;
}

function graphLinkPassesAdvancedFilters(
  link: GraphLink,
  sourceFilter: string,
  countryFilter: string,
  confidenceMin: number,
  evidenceOnly: boolean,
) {
  if ((link.confidence ?? 1) < confidenceMin) return false;
  if (sourceFilter !== "all" && !linkSourceTokens(link).includes(sourceFilter)) return false;
  if (countryFilter !== "all") {
    const country = countryFilter.toUpperCase();
    if (link.sourceCountry !== country && link.targetCountry !== country) return false;
  }
  if (evidenceOnly && !link.sourceId && !link.metadata?.source && !link.metadata?.source_label) return false;
  return true;
}

function nodeSourceTokens(node: GraphNode) {
  return [
    String(node.metadata.source ?? ""),
    String(node.metadata.source_id ?? ""),
    String(node.metadata.sourceId ?? ""),
    String(node.metadata.dataset ?? ""),
  ].filter(Boolean);
}

function linkSourceTokens(link: GraphLink) {
  return [
    link.sourceId ?? "",
    String(link.metadata?.source ?? ""),
    String(link.metadata?.source_id ?? ""),
    String(link.metadata?.source_label ?? ""),
  ].filter(Boolean);
}

function nodeEvidenceTokens(node: GraphNode) {
  return [
    ...(node.riskDrivers ?? []),
    String(node.metadata.source ?? ""),
    String(node.metadata.source_id ?? ""),
    String(node.metadata.evidence_ref ?? ""),
  ].filter(Boolean);
}

function selectedCountryForInput(graph: GraphExplorerData, selectedCountryCode?: string) {
  const countries = graph.availableCountries ?? graph.countryLens?.countries ?? [];
  return (
    countries.find((country) => country.code === selectedCountryCode) ??
    countries.find((country) => country.code === graph.countryLens?.selectedCountryCode) ??
    countries[0]
  );
}

function buildOverviewGraph(graph: GraphExplorerData) {
  const geo = buildGeoGraph(graph, undefined);
  if (geo.nodes.length >= 2 && geo.links.length >= 1) {
    return geo;
  }
  const critical = criticalGraphNodes(graph).slice(0, overviewNodeLimit);
  const criticalIds = new Set(critical.map((node) => node.id));
  const links = [...graph.links]
    .filter((link) => criticalIds.has(link.source) && criticalIds.has(link.target))
    .sort((a, b) => (b.transmissionWeight ?? b.weight) - (a.transmissionWeight ?? a.weight));
  if (links.length > 0) return { nodes: critical, links };
  const seededLinks = [...graph.links]
    .sort((a, b) => (b.transmissionWeight ?? b.weight) - (a.transmissionWeight ?? a.weight))
    .slice(0, overviewEdgeLimit);
  const nodeIds = new Set<string>();
  seededLinks.forEach((link) => {
    nodeIds.add(link.source);
    nodeIds.add(link.target);
  });
  return {
    nodes: graph.nodes.filter((node) => nodeIds.has(node.id)).slice(0, overviewNodeLimit),
    links: seededLinks,
  };
}

function buildGeoGraph(graph: GraphExplorerData, selectedCountryCode?: string) {
  const countries = [...(graph.availableCountries ?? graph.countryLens?.countries ?? [])].sort((a, b) => b.riskScore - a.riskScore);
  const selectedCode = selectedCountryCode?.toUpperCase();
  const countryNodes = countries.slice(0, overviewNodeLimit).map(countryToGraphNode);
  const visibleCountryCodes = new Set(countryNodes.map((node) => node.countryCode ?? ""));
  const countryEdges = (graph.countryLens?.countryEdges ?? [])
    .filter((edge) => {
      if (!visibleCountryCodes.has(edge.sourceCountry) || !visibleCountryCodes.has(edge.targetCountry)) return false;
      if (!selectedCode) return true;
      return edge.sourceCountry === selectedCode || edge.targetCountry === selectedCode;
    })
    .sort((a, b) => b.riskScore - a.riskScore)
    .map((edge) => ({
      id: `country-edge:${edge.id}`,
      source: countryNodeId(edge.sourceCountry),
      target: countryNodeId(edge.targetCountry),
      label: edge.topEdgeTypes[0]?.edgeType ?? "cross-border",
      weight: edge.transmissionWeight,
      level: scoreToRiskLevel(edge.riskScore),
      edgeType: "trade",
      riskScore: edge.riskScore,
      confidence: 0.72,
      transmissionWeight: edge.transmissionWeight,
      sourceCountry: edge.sourceCountry,
      targetCountry: edge.targetCountry,
      edgeRole: "transmission",
    } satisfies GraphLink));
  return { nodes: countryNodes, links: countryEdges };
}

function addCountryNodeContext(
  graph: GraphExplorerData,
  links: GraphLink[],
  selectedCountryCode: string | undefined,
  addNode: (nodeId: string | undefined) => void,
  addLinkContext: (link: GraphLink) => void,
) {
  const countryCode = selectedCountryCode?.toUpperCase();
  if (!countryCode) return;
  for (const node of graph.nodes) {
    if (graphNodeCountry(node) === countryCode) addNode(node.id);
  }
  for (const link of links) {
    if (link.sourceCountry === countryCode || link.targetCountry === countryCode) addLinkContext(link);
  }
  for (const path of graph.transmissionPaths ?? []) {
    if (!path.countrySequence.includes(countryCode)) continue;
    path.nodeSequence.forEach(addNode);
  }
}

function countryToGraphNode(country: CountryRiskSummary, index: number): GraphNode {
  const score = graphScore(country.riskScore);
  return {
    id: countryNodeId(country.code),
    label: country.label || country.countryName || country.code,
    kind: "country",
    level: scoreToRiskLevel(score),
    score,
    x: 15 + (index % 5) * 16,
    y: 15 + Math.floor(index / 5) * 16,
    metadata: {
      cluster: "country",
      country_code: country.code,
      entities: country.entityCount,
      edges: country.edgeCount,
      inbound_risk: country.inboundRisk,
      outbound_risk: country.outboundRisk,
    },
    countryCode: country.code,
    entityType: "country_cluster",
    riskScore: score,
    centralityScore: country.centralityScore,
    criticalityScore: score,
  };
}

function countryNodeId(countryCode: string) {
  return `country:${countryCode}`;
}

function scoreToRiskLevel(score: number): RiskLevel {
  const normalized = graphScore(score);
  if (normalized >= 85) return "critical";
  if (normalized >= 68) return "severe";
  if (normalized >= 42) return "elevated";
  if (normalized >= 18) return "guarded";
  return "low";
}

function compareVisibleNodes(
  a: GraphNode,
  b: GraphNode,
  options: {
    activePathNodeIds: Set<string>;
    matchedNodeIds: Set<string>;
    pinnedNodeIds: Set<string>;
    selectedNodeId?: string;
    selectedPathStepNodeId?: string;
  },
) {
  const scoreA = nodePriority(a, options);
  const scoreB = nodePriority(b, options);
  return scoreB - scoreA || graphScore(b.criticalityScore ?? b.score) - graphScore(a.criticalityScore ?? a.score) || a.label.localeCompare(b.label);
}

function nodePriority(
  node: GraphNode,
  options: {
    activePathNodeIds: Set<string>;
    matchedNodeIds: Set<string>;
    pinnedNodeIds: Set<string>;
    selectedNodeId?: string;
    selectedPathStepNodeId?: string;
  },
) {
  return (
    (node.id === options.selectedNodeId ? 1000 : 0) +
    (node.id === options.selectedPathStepNodeId ? 900 : 0) +
    (options.matchedNodeIds.has(node.id) ? 800 : 0) +
    (options.pinnedNodeIds.has(node.id) ? 700 : 0) +
    (options.activePathNodeIds.has(node.id) ? 600 : 0) +
    graphScore(node.criticalityScore ?? node.score)
  );
}

function compareVisibleLinks(
  a: GraphLink,
  b: GraphLink,
  options: {
    activePathEdgeIds: Set<string>;
    selectedEdgeId?: string | null;
    selectedNodeId?: string;
    selectedPathStepEdgeId?: string;
  },
) {
  const scoreA = linkPriority(a, options);
  const scoreB = linkPriority(b, options);
  return scoreB - scoreA || a.id.localeCompare(b.id);
}

function linkPriority(
  link: GraphLink,
  options: {
    activePathEdgeIds: Set<string>;
    selectedEdgeId?: string | null;
    selectedNodeId?: string;
    selectedPathStepEdgeId?: string;
  },
) {
  return (
    (link.id === options.selectedEdgeId ? 1000 : 0) +
    (link.id === options.selectedPathStepEdgeId ? 900 : 0) +
    (options.activePathEdgeIds.has(link.id) ? 800 : 0) +
    (link.source === options.selectedNodeId || link.target === options.selectedNodeId ? 300 : 0) +
    (link.transmissionWeight ?? link.weight) * 100
  );
}
