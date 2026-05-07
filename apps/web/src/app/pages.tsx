import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import type { CSSProperties } from "react";
import type { ElkNode } from "elkjs";
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  type Edge as FlowEdge,
  type Node as FlowNode,
  type NodeProps
} from "@xyflow/react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  Factory,
  GitBranch,
  Layers3,
  Play,
  Search,
  ShieldAlert,
  SlidersHorizontal,
  TerminalSquare
} from "lucide-react";
import type { SupplyRiskApiClient, SupplyRiskDashboardData } from "@supply-risk/api-client";
import type {
  ApiResult,
  CountryLensData,
  CountryRiskSummary,
  CriticalGraphNode,
  DashboardPageId,
  EvidenceItem,
  ExplainedPath,
  GraphLink,
  GraphTransmissionPath,
  GraphNode,
  GraphNodeKind,
  GraphVersion,
  Prediction,
  RiskLevel,
  ShockSimulationInput,
  ShockSimulationResult
} from "@supply-risk/shared-types";
import { formatCompactNumber, formatPercent, formatUsdCompact, riskClassByLevel } from "@supply-risk/design-system";
import { Button, Field, IconButton, MetricTile, Panel, ProgressBar, RiskPill, ScoreDial, StatusPill } from "./components";
import { useI18n } from "./i18n";

export interface PageRenderProps {
  data: SupplyRiskDashboardData;
  apiClient: SupplyRiskApiClient;
}

export function renderPage(pageId: DashboardPageId, props: PageRenderProps) {
  switch (pageId) {
    case "global-risk-cockpit":
      return <GlobalRiskCockpit data={props.data} />;
    case "graph-explorer":
      return <GraphExplorer data={props.data} initialMode="risk-centrality" />;
    case "company-risk-360":
      return <CompanyRisk360 data={props.data} />;
    case "prediction-center":
      return <PredictionCenter data={props.data} />;
    case "path-analysis":
      return <GraphExplorer data={props.data} initialMode="path-analysis" />;
    case "country-lens":
      return <GraphExplorer data={props.data} initialMode="country-lens" />;
    case "path-explainer":
      return <PathExplainer data={props.data} />;
    case "shock-simulator":
      return <ShockSimulator apiClient={props.apiClient} />;
    case "causal-evidence-board":
      return <CausalEvidenceBoard data={props.data} />;
    case "graph-version-studio":
      return <GraphVersionStudio data={props.data} />;
    case "system-health-center":
      return <SystemHealthCenter data={props.data} />;
    default:
      return (
        <div className="empty-state">
          <p>Page not configured.</p>
        </div>
      );
  }
}

function isAcceptedRealApiResult<T>(result: ApiResult<T>): result is ApiResult<T> & { data: T } {
  return (
    result.envelope.status === "success" &&
    result.data !== null &&
    !["fallback", "unavailable", "unauthorized", "error"].includes(result.sourceStatus)
  );
}

function GlobalRiskCockpit({ data }: { data: SupplyRiskDashboardData }) {
  const { t } = useI18n();
  const cockpit = data.globalRiskCockpit;

  return (
    <div className="page-grid">
      <div className="metrics-grid">
        {cockpit.metrics.map((metric) => (
          <MetricTile key={metric.id} metric={metric} />
        ))}
      </div>

      <div className="page-grid cockpit-layout">
        <Panel
          title="Global exposure canvas"
          subtitle={`Last refreshed ${cockpit.lastUpdated}; hotspots are positioned by route and supplier concentration.`}
          action={<IconButton icon={Search} label="Search exposure graph" />}
        >
          <div className="map-canvas" role="img" aria-label={t("Global supply risk hotspot map")}>
            {cockpit.hotspots.map((hotspot) => (
              <div key={hotspot.id}>
                <span
                  className={`hotspot ${riskClassByLevel[hotspot.level]}`}
                  style={{ left: `${hotspot.x}%`, top: `${hotspot.y}%` }}
                />
                <article
                  className="hotspot-card"
                  style={{
                    left: `${Math.min(hotspot.x + 1, 76)}%`,
                    top: `${Math.max(hotspot.y - 5, 6)}%`
                  }}
                >
                  <div className="row-top">
                    <strong>{hotspot.label}</strong>
                    <RiskPill level={hotspot.level} />
                  </div>
                  <span>{hotspot.drivers.slice(0, 2).join(" / ")}</span>
                </article>
              </div>
            ))}
          </div>
        </Panel>

        <div className="page-grid">
          <Panel title="Incident queue" subtitle="Ranked by signal strength and graph reach.">
            <ul className="incident-list">
              {cockpit.incidents.map((incident) => (
                <li className="data-row" key={incident.id}>
                  <div className="row-top">
                    <div>
                      <span className="row-title">{incident.title}</span>
                      <span className="row-subtitle">{incident.region}</span>
                    </div>
                    <RiskPill level={incident.level} />
                  </div>
                  <ProgressBar value={incident.signalStrength * 100} level={incident.level} />
                  <div className="row-meta">
                    <span>{t(`${incident.affectedCompanies} companies`)}</span>
                    <span>{t(`${formatPercent(incident.signalStrength)} signal strength`)}</span>
                  </div>
                </li>
              ))}
            </ul>
          </Panel>

          <Panel title="Corridor stress" subtitle="Trade lanes carrying disproportionate revenue exposure.">
            <ul className="corridor-list">
              {cockpit.corridors.map((corridor) => (
                <li className="data-row" key={corridor.id}>
                  <div className="row-top">
                    <div>
                      <span className="row-title">
                        {corridor.source} {t("to")} {corridor.target}
                      </span>
                      <span className="row-subtitle">{corridor.commodity}</span>
                    </div>
                    <RiskPill level={corridor.level} />
                  </div>
                  <ProgressBar value={corridor.score} level={corridor.level} />
                  <div className="row-meta">
                    <span>{t(`${corridor.score}/100 risk`)}</span>
                    <span>{t(`${formatPercent(corridor.volumeShare)} volume share`)}</span>
                  </div>
                </li>
              ))}
            </ul>
          </Panel>
        </div>
      </div>
    </div>
  );
}

type GraphExplorerMode = "risk-centrality" | "path-analysis" | "country-lens";

const graphModeOptions: Array<{ id: GraphExplorerMode; label: string }> = [
  { id: "risk-centrality", label: "Risk + Centrality" },
  { id: "path-analysis", label: "Path Analysis" },
  { id: "country-lens", label: "Country Lens" },
];

function GraphExplorer({
  data,
  initialMode = "risk-centrality"
}: {
  data: SupplyRiskDashboardData;
  initialMode?: GraphExplorerMode;
}) {
  const { t } = useI18n();
  const graph = data.graphExplorer;
  const [mode, setMode] = useState<GraphExplorerMode>(initialMode);
  const [kind, setKind] = useState<GraphNodeKind | "all">("all");
  const [query, setQuery] = useState("");
  const [selectedNodeId, setSelectedNodeId] = useState(graph.selectedNodeId);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [selectedPathId, setSelectedPathId] = useState(graph.transmissionPaths?.[0]?.id ?? data.pathExplainer.selectedPathId);
  const [selectedPathStepIndex, setSelectedPathStepIndex] = useState(0);
  const [selectedCountryCode, setSelectedCountryCode] = useState(
    graph.countryLens?.selectedCountryCode ?? graph.availableCountries?.[0]?.code ?? "CN",
  );
  const normalizedQuery = query.trim().toLowerCase();
  const graphStats = graph.graphStats;
  const nodeMap = useMemo(() => new Map(graph.nodes.map((node) => [node.id, node])), [graph.nodes]);
  const linkMap = useMemo(() => new Map(graph.links.map((link) => [link.id, link])), [graph.links]);
  const criticalNodes = useMemo<CriticalGraphNode[]>(
    () =>
      graph.criticalNodes?.length
        ? graph.criticalNodes
        : [...graph.nodes]
            .sort((a, b) => b.score - a.score)
            .slice(0, 12)
            .map((node) => ({
              id: node.id,
              label: node.label,
              kind: node.kind,
              level: node.level,
              score: node.score,
              countryCode: node.countryCode,
              entityType: node.entityType,
              riskScore: node.riskScore ?? node.score,
              centralityScore: node.centralityScore ?? 0,
              criticalityScore: node.criticalityScore ?? node.score,
              criticalityRank: node.criticalityRank,
              drivers: node.riskDrivers ?? [],
            })),
    [graph.criticalNodes, graph.nodes]
  );
  const transmissionPaths = graph.transmissionPaths ?? [];
  const activePath = transmissionPaths.find((path) => path.id === selectedPathId) ?? transmissionPaths[0];
  const activePathEdgeIds = useMemo(() => new Set(activePath?.edgeSequence ?? []), [activePath]);
  const activePathNodeIds = useMemo(() => new Set(activePath?.nodeSequence ?? []), [activePath]);
  const activePathNodeIndex = useMemo(
    () => new Map((activePath?.nodeSequence ?? []).map((nodeId, index) => [nodeId, index])),
    [activePath],
  );
  const selectedPathStep =
    mode === "path-analysis" && activePath ? activePath.steps[Math.min(selectedPathStepIndex, activePath.steps.length - 1)] : undefined;
  const selectedPathStepEdgeId =
    mode === "path-analysis" && activePath && selectedPathStepIndex > 0
      ? activePath.edgeSequence[selectedPathStepIndex - 1]
      : undefined;
  const countryLens = graph.countryLens;
  const availableCountries = graph.availableCountries ?? countryLens?.countries ?? [];
  const selectedCountry =
    availableCountries.find((country) => country.code === selectedCountryCode) ??
    availableCountries.find((country) => country.code === countryLens?.selectedCountryCode) ??
    availableCountries[0];

  useEffect(() => {
    setMode(initialMode);
  }, [initialMode]);

  useEffect(() => {
    if (activePath && selectedPathId !== activePath.id) {
      setSelectedPathId(activePath.id);
    }
  }, [activePath, selectedPathId]);

  useEffect(() => {
    setSelectedPathStepIndex(0);
  }, [selectedPathId]);

  useEffect(() => {
    if (activePath && selectedPathStepIndex >= activePath.steps.length) {
      setSelectedPathStepIndex(Math.max(0, activePath.steps.length - 1));
    }
  }, [activePath, selectedPathStepIndex]);

  useEffect(() => {
    if (selectedCountry && selectedCountry.code !== selectedCountryCode) {
      setSelectedCountryCode(selectedCountry.code);
    }
  }, [selectedCountry, selectedCountryCode]);

  const visibleNodeIds = useMemo(() => {
    const ids = new Set<string>();
    const addNode = (nodeId: string | undefined) => {
      if (nodeId && nodeMap.has(nodeId)) ids.add(nodeId);
    };
    const addLinkContext = (link: GraphLink) => {
      addNode(link.source);
      addNode(link.target);
    };
    const addPathContext = (path: GraphTransmissionPath | undefined) => {
      path?.nodeSequence.forEach(addNode);
    };
    const addFirstNeighborContext = (nodeId: string | undefined) => {
      if (!nodeId) return;
      addNode(nodeId);
      for (const link of graph.links) {
        if (link.source === nodeId || link.target === nodeId) addLinkContext(link);
      }
    };
    const nodeMatchesSearch = (node: GraphNode) => {
      if (!normalizedQuery) return true;
      const metadataValues = Object.values(node.metadata).map((value) => String(value).toLowerCase());
      return [node.id, node.label, node.kind, node.countryCode ?? "", node.entityType ?? "", ...metadataValues].some((value) =>
        value.toLowerCase().includes(normalizedQuery),
      );
    };

    if (mode === "path-analysis") {
      addPathContext(activePath);
      for (const edgeId of activePath?.edgeSequence ?? []) {
        const link = linkMap.get(edgeId);
        if (link) addLinkContext(link);
      }
      for (const path of transmissionPaths.slice(0, 4)) {
        addPathContext(path);
      }
    } else if (mode === "country-lens" && selectedCountryCode) {
      for (const node of graph.nodes) {
        if ((node.countryCode ?? String(node.metadata.country ?? "")).toUpperCase() === selectedCountryCode) {
          addNode(node.id);
        }
      }
      for (const link of graph.links) {
        if (link.sourceCountry === selectedCountryCode || link.targetCountry === selectedCountryCode) {
          addLinkContext(link);
        }
      }
      for (const path of transmissionPaths) {
        if (path.countrySequence.includes(selectedCountryCode)) addPathContext(path);
      }
    } else {
      for (const node of criticalNodes.slice(0, 18)) {
        addNode(node.id);
      }
      addFirstNeighborContext(selectedNodeId);
    }

    if (normalizedQuery) {
      const matchedIds = graph.nodes
        .filter((node) => (kind === "all" || node.kind === kind) && nodeMatchesSearch(node))
        .map((node) => node.id);
      for (const nodeId of matchedIds) {
        addNode(nodeId);
        for (const link of graph.links) {
          if (link.source === nodeId || link.target === nodeId) addLinkContext(link);
        }
        for (const path of transmissionPaths) {
          if (path.nodeSequence.includes(nodeId)) addPathContext(path);
        }
      }
    } else if (kind !== "all") {
      for (const node of graph.nodes) {
        if (node.kind === kind) addNode(node.id);
      }
    }

    addFirstNeighborContext(selectedNodeId);
    if (selectedPathStep?.nodeId) addFirstNeighborContext(selectedPathStep.nodeId);

    if (ids.size === 0) {
      for (const node of graph.nodes.slice(0, 40)) addNode(node.id);
    }
    return ids;
  }, [
    activePath,
    criticalNodes,
    graph.links,
    graph.nodes,
    kind,
    linkMap,
    mode,
    nodeMap,
    normalizedQuery,
    selectedCountryCode,
    selectedNodeId,
    selectedPathStep,
    transmissionPaths,
  ]);

  const visibleNodes = useMemo(
    () =>
      graph.nodes
        .filter((node) => visibleNodeIds.has(node.id))
        .sort((a, b) => {
          if (activePathNodeIds.has(a.id) !== activePathNodeIds.has(b.id)) return activePathNodeIds.has(a.id) ? -1 : 1;
          return (b.criticalityScore ?? b.score) - (a.criticalityScore ?? a.score);
        }),
    [activePathNodeIds, graph.nodes, visibleNodeIds]
  );
  const visibleLinks = useMemo(
    () => graph.links.filter((link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target)),
    [graph.links, visibleNodeIds]
  );
  const selectedNode =
    nodeMap.get(selectedNodeId) ??
    visibleNodes.find((node) => node.id === graph.selectedNodeId) ??
    visibleNodes[0] ??
    graph.nodes[0];
  const selectedEdge = selectedEdgeId ? linkMap.get(selectedEdgeId) : undefined;

  return (
    <div className="graph-workbench">
      <Panel title="Graph scope" subtitle="Mode, filters, and ranked critical entities." className="graph-side-panel">
        <div className="graph-mode-toolbar" aria-label={t("Graph analysis mode")}>
          {graphModeOptions.map((option) => (
            <button
              className={`mode-tab ${mode === option.id ? "is-active" : ""}`}
              key={option.id}
              onClick={() => {
                setMode(option.id);
                setSelectedEdgeId(null);
              }}
              type="button"
            >
              {t(option.label)}
            </button>
          ))}
        </div>
        <div className="segmented" aria-label={t("Graph node type")}>
          {(["all", ...graph.filters] as Array<GraphNodeKind | "all">).map((filter) => (
            <button
              className={`segment ${kind === filter ? "is-active" : ""}`}
              key={filter}
              onClick={() => setKind(filter)}
              type="button"
            >
              {t(filter)}
            </button>
          ))}
        </div>
        <label className="form-control graph-search-control">
          <span>{t("Entity search")}</span>
          <input
            aria-label={t("Entity search")}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={t("Search name, source, country, or external id")}
            type="search"
            value={query}
          />
        </label>
        <div className="inspector-grid graph-stat-grid">
          <Field label="Visible nodes" value={visibleNodes.length} />
          <Field label="Visible links" value={visibleLinks.length} />
          <Field label="Total nodes" value={formatCompactNumber(graphStats?.totalNodes ?? graph.nodes.length)} />
          <Field label="Total links" value={formatCompactNumber(graphStats?.totalLinks ?? graph.links.length)} />
          <Field label="Critical nodes" value={criticalNodes.length} />
          <Field label="Transmission paths" value={transmissionPaths.length} />
        </div>

        <GraphCriticalNodeList
          nodes={criticalNodes}
          selectedNodeId={selectedNode.id}
          onSelect={(nodeId) => {
            setSelectedNodeId(nodeId);
            setSelectedEdgeId(null);
            setMode("risk-centrality");
          }}
        />

        {mode === "path-analysis" ? (
          <GraphPathList
            paths={transmissionPaths}
            selectedPathId={activePath?.id}
            onSelect={(pathId) => {
              setSelectedPathId(pathId);
              setSelectedEdgeId(null);
            }}
          />
        ) : null}

        {mode === "country-lens" ? (
          <GraphCountryList
            countries={availableCountries}
            selectedCountryCode={selectedCountry?.code}
            onSelect={(countryCode) => {
              setSelectedCountryCode(countryCode);
              setSelectedEdgeId(null);
            }}
          />
        ) : null}
      </Panel>

      <Panel
        title="Entity network"
        subtitle="Click nodes, edges, paths, and countries to inspect risk transmission."
        className="graph-main-panel"
      >
        <div className="graph-canvas">
          <GraphNetwork
            activePathEdgeIds={activePathEdgeIds}
            activePathNodeIds={activePathNodeIds}
            links={visibleLinks}
            mode={mode}
            nodes={visibleNodes}
            onSelectEdge={(edgeId) => {
              setSelectedEdgeId(edgeId);
            }}
            onSelectNode={(nodeId) => {
              setSelectedNodeId(nodeId);
              setSelectedEdgeId(null);
            }}
            selectedCountryCode={mode === "country-lens" ? selectedCountry?.code : undefined}
            selectedEdgeId={selectedEdgeId}
            selectedNodeId={selectedNode.id}
            selectedPathStepEdgeId={selectedPathStepEdgeId}
            selectedPathStepNodeId={selectedPathStep?.nodeId}
            activePathNodeIndex={activePathNodeIndex}
          />
          {visibleNodes.length === 0 ? <div className="empty-state">{t("No entities match the current filters.")}</div> : null}
        </div>
      </Panel>

      <Panel title="Inspector" subtitle="Selection-specific evidence, flow, and country context." className="graph-inspector-panel">
        <GraphInspector
          activePath={mode === "path-analysis" ? activePath : undefined}
          countryLens={countryLens}
          edge={selectedEdge}
          node={selectedEdge ? undefined : selectedNode}
          onSelectPathStep={(index, nodeId) => {
            setSelectedPathStepIndex(index);
            if (nodeId) {
              setSelectedNodeId(nodeId);
              setSelectedEdgeId(null);
            }
          }}
          selectedCountry={mode === "country-lens" ? selectedCountry : undefined}
          selectedPathStepIndex={selectedPathStepIndex}
        />
      </Panel>
    </div>
  );
}

function GraphCriticalNodeList({
  nodes,
  onSelect,
  selectedNodeId
}: {
  nodes: CriticalGraphNode[];
  onSelect: (nodeId: string) => void;
  selectedNodeId: string;
}) {
  const { t } = useI18n();
  return (
    <div className="graph-list-section">
      <div className="section-kicker">{t("Critical nodes")}</div>
      <ul className="critical-node-list">
        {nodes.slice(0, 10).map((node) => (
          <li key={node.id}>
            <button
              className={`graph-list-button ${node.id === selectedNodeId ? "is-active" : ""}`}
              onClick={() => onSelect(node.id)}
              type="button"
            >
              <span>
                <strong>{node.criticalityRank ? `#${node.criticalityRank} ` : ""}{node.label}</strong>
                <small>{node.kind} / {node.countryCode ?? "global"}</small>
              </span>
              <b>{graphScore(node.criticalityScore ?? node.score)}</b>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function GraphPathList({
  onSelect,
  paths,
  selectedPathId
}: {
  onSelect: (pathId: string) => void;
  paths: GraphTransmissionPath[];
  selectedPathId?: string;
}) {
  const { t } = useI18n();
  return (
    <div className="graph-list-section">
      <div className="section-kicker">{t("Transmission paths")}</div>
      <ul className="path-list">
        {paths.slice(0, 8).map((path) => (
          <li key={path.id}>
            <button
              className={`graph-list-button path ${path.id === selectedPathId ? "is-active" : ""}`}
              onClick={() => onSelect(path.id)}
              type="button"
            >
              <span>
                <strong>{path.sourceLabel} -&gt; {path.targetLabel}</strong>
                <small>{path.edgeSequence.length} hops / {path.countrySequence.join(" -> ")}</small>
              </span>
              <b>{Math.round(path.transmissionScore * 100)}</b>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function GraphCountryList({
  countries,
  onSelect,
  selectedCountryCode
}: {
  countries: CountryRiskSummary[];
  onSelect: (countryCode: string) => void;
  selectedCountryCode?: string;
}) {
  const { t } = useI18n();
  return (
    <div className="graph-list-section">
      <div className="section-kicker">{t("Available countries")}</div>
      <ul className="country-list">
        {countries.slice(0, 12).map((country) => (
          <li key={country.code}>
            <button
              className={`graph-list-button country ${country.code === selectedCountryCode ? "is-active" : ""}`}
              onClick={() => onSelect(country.code)}
              type="button"
            >
              <span>
                <strong>{country.label}</strong>
                <small>{country.entityCount} nodes / {country.edgeCount} edges</small>
              </span>
              <b>{graphScore(country.riskScore)}</b>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function GraphInspector({
  activePath,
  countryLens,
  edge,
  node,
  onSelectPathStep,
  selectedCountry,
  selectedPathStepIndex
}: {
  activePath?: GraphTransmissionPath;
  countryLens?: CountryLensData;
  edge?: GraphLink;
  node?: GraphNode;
  onSelectPathStep?: (index: number, nodeId: string) => void;
  selectedCountry?: CountryRiskSummary;
  selectedPathStepIndex?: number;
}) {
  if (edge) {
    return <EdgeInspector edge={edge} />;
  }
  if (selectedCountry && countryLens) {
    return <CountryInspector country={selectedCountry} countryLens={countryLens} />;
  }
  if (activePath) {
    return <PathInspector onSelectStep={onSelectPathStep} path={activePath} selectedStepIndex={selectedPathStepIndex ?? 0} />;
  }
  if (node) {
    return <NodeInspector node={node} />;
  }
  return <div className="empty-state">Select an object to inspect.</div>;
}

function NodeInspector({ node }: { node: GraphNode }) {
  return (
    <div className="inspector-stack">
      <div className="inspector-grid">
        <Field label="Name" value={node.label} />
        <Field label="Risk level" value={<RiskPill level={node.level} />} />
        <Field label="Risk score" value={`${graphScore(node.riskScore ?? node.score)}/100`} />
        <Field label="Centrality" value={`${graphScore(node.centralityScore ?? 0)}/100`} />
        <Field label="Criticality" value={`${graphScore(node.criticalityScore ?? node.score)}/100`} />
        <Field label="Rank" value={node.criticalityRank ? `#${node.criticalityRank}` : "n/a"} />
        <Field label="In / out degree" value={`${node.inDegree ?? 0} / ${node.outDegree ?? 0}`} />
        <Field label="Country" value={node.countryCode ?? String(node.metadata.country ?? "global")} />
      </div>
      {node.riskDrivers?.length ? (
        <ul className="evidence-list compact">
          {node.riskDrivers.slice(0, 4).map((driver) => (
            <li key={driver}>{driver}</li>
          ))}
        </ul>
      ) : null}
      <div className="inspector-grid">
        {Object.entries(node.metadata).slice(0, 8).map(([label, value]) => (
          <Field key={label} label={label} value={String(value)} />
        ))}
      </div>
    </div>
  );
}

function EdgeInspector({ edge }: { edge: GraphLink }) {
  return (
    <div className="inspector-stack edge-inspector">
      <div className="inspector-grid">
        <Field label="Edge type" value={edge.edgeType ?? edge.label} />
        <Field label="Role" value={edge.edgeRole ?? "context"} />
        <Field label="Risk score" value={`${edge.riskScore ?? Math.round(edge.weight * 100)}/100`} />
        <Field label="Weight" value={formatPercent(edge.transmissionWeight ?? edge.weight)} />
        <Field label="Confidence" value={formatPercent(edge.confidence ?? 0)} />
        <Field label="Lag days" value={edge.lagDays ?? 0} />
        <Field label="Source country" value={edge.sourceCountry ?? "global"} />
        <Field label="Target country" value={edge.targetCountry ?? "global"} />
      </div>
      <p className="inspector-note">
        {edge.source} -&gt; {edge.target} / {edge.sourceId ?? "public source"}
      </p>
    </div>
  );
}

function PathInspector({
  onSelectStep,
  path,
  selectedStepIndex
}: {
  onSelectStep?: (index: number, nodeId: string) => void;
  path: GraphTransmissionPath;
  selectedStepIndex: number;
}) {
  const boundedStepIndex = Math.min(selectedStepIndex, Math.max(0, path.steps.length - 1));
  return (
    <div className="inspector-stack path-inspector">
      <div className="inspector-grid">
        <Field label="Path risk" value={`${Math.round(path.pathRisk * 100)}/100`} />
        <Field label="Transmission" value={`${Math.round(path.transmissionScore * 100)}/100`} />
        <Field label="Confidence" value={formatPercent(path.pathConfidence)} />
        <Field label="Hops" value={path.edgeSequence.length} />
        <Field label="Countries" value={path.countrySequence.join(" -> ")} />
        <Field label="Bottleneck" value={path.bottleneckEdgeId} />
      </div>
      {path.steps.length > 1 ? (
        <div className="path-scrubber">
          <button
            aria-label="Previous path step"
            disabled={boundedStepIndex === 0}
            onClick={() => {
              const nextIndex = Math.max(0, boundedStepIndex - 1);
              const nextStep = path.steps[nextIndex];
              if (nextStep) onSelectStep?.(nextIndex, nextStep.nodeId);
            }}
            type="button"
          >
            Prev
          </button>
          <input
            aria-label="Selected path step"
            max={path.steps.length - 1}
            min={0}
            onChange={(event) => {
              const nextIndex = Number(event.target.value);
              const nextStep = path.steps[nextIndex];
              if (nextStep) onSelectStep?.(nextIndex, nextStep.nodeId);
            }}
            step={1}
            type="range"
            value={boundedStepIndex}
          />
          <button
            aria-label="Next path step"
            disabled={boundedStepIndex === path.steps.length - 1}
            onClick={() => {
              const nextIndex = Math.min(path.steps.length - 1, boundedStepIndex + 1);
              const nextStep = path.steps[nextIndex];
              if (nextStep) onSelectStep?.(nextIndex, nextStep.nodeId);
            }}
            type="button"
          >
            Next
          </button>
        </div>
      ) : null}
      <div className="transmission-step-list">
        {path.steps.map((step, index) => (
          <button
            className={`transmission-step ${index === boundedStepIndex ? "is-active" : ""}`}
            key={step.id}
            onClick={() => onSelectStep?.(index, step.nodeId)}
            type="button"
          >
            <span>{index + 1}</span>
            <div>
              <strong>{step.label}</strong>
              <small>{step.edgeType ?? "source"} / {step.countryCode ?? "global"} / {step.evidence}</small>
            </div>
            <b>{step.contribution}</b>
          </button>
        ))}
      </div>
    </div>
  );
}

function CountryInspector({
  country,
  countryLens
}: {
  country: CountryRiskSummary;
  countryLens: CountryLensData;
}) {
  const selectedNodes = countryLens.topCriticalNodes.length ? countryLens.topCriticalNodes : countryLens.criticalNodes;
  const selectedPaths = countryLens.topPaths.length ? countryLens.topPaths : countryLens.transmissionPaths;
  return (
    <div className="inspector-stack country-inspector">
      <div className="inspector-grid">
        <Field label="Country" value={country.label} />
        <Field label="Risk score" value={`${graphScore(country.riskScore)}/100`} />
        <Field label="Centrality" value={`${graphScore(country.centralityScore)}/100`} />
        <Field label="Nodes" value={country.entityCount} />
        <Field label="Inbound risk" value={country.inboundRisk.toFixed(1)} />
        <Field label="Outbound risk" value={country.outboundRisk.toFixed(1)} />
      </div>
      <div className="country-lens-grid">
        <div>
          <div className="section-kicker">Top companies / facilities</div>
          <ul className="evidence-list compact">
            {selectedNodes.slice(0, 5).map((node) => (
              <li key={node.id}>{node.label} / {graphScore(node.criticalityScore ?? node.score)}</li>
            ))}
          </ul>
        </div>
        <div>
          <div className="section-kicker">High-risk paths</div>
          <ul className="evidence-list compact">
            {selectedPaths.slice(0, 4).map((path) => (
              <li key={path.id}>{path.sourceLabel} -&gt; {path.targetLabel}</li>
            ))}
          </ul>
        </div>
      </div>
      {country.subdivisions?.length ? (
        <div>
          <div className="section-kicker">Province / region detail</div>
          <ul className="evidence-list compact">
            {country.subdivisions.slice(0, 6).map((subdivision) => (
              <li key={subdivision.geoId}>
                {subdivision.label}: {subdivision.entityCount} nodes / {graphScore(subdivision.riskScore)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      <div>
        <div className="section-kicker">Data coverage</div>
        <ul className="evidence-list compact">
          {countryLens.dataCoverage
            .filter((coverage) => coverage.countryCode === country.code)
            .slice(0, 5)
            .map((coverage) => (
              <li key={`${coverage.countryCode}-${coverage.sourceId}`}>
                {coverage.sourceId}: {coverage.nodeCount} nodes
              </li>
            ))}
        </ul>
      </div>
    </div>
  );
}

type RiskFlowNodeData = {
  graphNode: GraphNode;
  selected: boolean;
  dimmed: boolean;
  inActivePath: boolean;
  isFirstNeighbor: boolean;
  selectedPathStep: boolean;
};

type RiskFlowNode = FlowNode<RiskFlowNodeData, "risk">;
type RiskFlowEdge = FlowEdge<{ level: RiskLevel; label: string; role?: string; activePath: boolean }>;

const graphKindRankHint: Record<GraphNodeKind, number> = {
  country: 0,
  route: 1,
  data: 1,
  supplier: 2,
  facility: 2,
  commodity: 2,
  company: 3,
};

type GraphPosition = { x: number; y: number };

const graphColorByLevel: Record<RiskLevel, string> = {
  low: "#52d7d0",
  guarded: "#9fb2a9",
  elevated: "#f2b84b",
  severe: "#ff7a4d",
  critical: "#ff4d6d"
};

const graphNodeTypes = { risk: RiskFlowNodeCard };

type GraphHoverTooltip = {
  x: number;
  y: number;
  title: string;
  meta: string;
  detail: string;
};

function GraphNetwork({
  activePathEdgeIds,
  activePathNodeIds,
  links,
  mode,
  nodes,
  onSelectEdge,
  onSelectNode,
  selectedCountryCode,
  selectedEdgeId,
  selectedNodeId,
  selectedPathStepEdgeId,
  selectedPathStepNodeId,
  activePathNodeIndex
}: {
  activePathEdgeIds: Set<string>;
  activePathNodeIds: Set<string>;
  links: GraphLink[];
  mode: GraphExplorerMode;
  nodes: GraphNode[];
  onSelectEdge: (edgeId: string) => void;
  onSelectNode: (nodeId: string) => void;
  selectedCountryCode?: string;
  selectedEdgeId: string | null;
  selectedNodeId: string;
  selectedPathStepEdgeId?: string;
  selectedPathStepNodeId?: string;
  activePathNodeIndex: Map<string, number>;
}) {
  const [tooltip, setTooltip] = useState<GraphHoverTooltip | null>(null);
  const firstNeighborNodeIds = useMemo(() => {
    const neighborIds = new Set<string>();
    for (const link of links) {
      if (link.source === selectedNodeId) neighborIds.add(link.target);
      if (link.target === selectedNodeId) neighborIds.add(link.source);
      if (selectedEdgeId && link.id === selectedEdgeId) {
        neighborIds.add(link.source);
        neighborIds.add(link.target);
      }
      if (selectedPathStepNodeId && (link.source === selectedPathStepNodeId || link.target === selectedPathStepNodeId)) {
        neighborIds.add(link.source);
        neighborIds.add(link.target);
      }
    }
    return neighborIds;
  }, [links, selectedEdgeId, selectedNodeId, selectedPathStepNodeId]);
  const topologyPositions = useTopologyPositions(nodes, links, activePathNodeIndex);
  const flowNodes = useMemo<RiskFlowNode[]>(
    () =>
      layoutGraphNodes(nodes, links, {
        activePathNodeIds,
        activePathNodeIndex,
        firstNeighborNodeIds,
        layoutPositions: topologyPositions,
        mode,
        selectedCountryCode,
        selectedNodeId,
        selectedPathStepNodeId,
      }),
    [activePathNodeIds, activePathNodeIndex, firstNeighborNodeIds, links, mode, nodes, selectedCountryCode, selectedNodeId, selectedPathStepNodeId, topologyPositions]
  );
  const flowEdges = useMemo<RiskFlowEdge[]>(
    () =>
      layoutGraphEdges(links, new Set(nodes.map((node) => node.id)), {
        activePathEdgeIds,
        firstNeighborNodeIds,
        mode,
        selectedCountryCode,
        selectedEdgeId,
        selectedNodeId,
        selectedPathStepEdgeId,
        selectedPathStepNodeId,
      }),
    [activePathEdgeIds, firstNeighborNodeIds, links, mode, nodes, selectedCountryCode, selectedEdgeId, selectedNodeId, selectedPathStepEdgeId, selectedPathStepNodeId]
  );

  return (
    <>
      <ReactFlow
        className="risk-flow"
        colorMode="dark"
        defaultEdgeOptions={{ type: "smoothstep" }}
        edges={flowEdges}
        fitView
        fitViewOptions={{ padding: 0.2, maxZoom: 1.08 }}
        maxZoom={1.65}
        minZoom={0.22}
        nodeTypes={graphNodeTypes}
        nodes={flowNodes}
        nodesDraggable={false}
        onEdgeClick={(_, edge) => onSelectEdge(edge.id)}
        onEdgeMouseEnter={(event, edge) => {
          const link = links.find((candidate) => candidate.id === edge.id);
          setTooltip({
            x: event.clientX,
            y: event.clientY,
            title: edge.label ? String(edge.label) : link?.label ?? edge.id,
            meta: `${link?.edgeRole ?? link?.edgeType ?? "edge"} / ${formatPercent(link?.transmissionWeight ?? link?.weight ?? 0)}`,
            detail: `${link?.sourceCountry ?? "global"} -> ${link?.targetCountry ?? "global"}`,
          });
        }}
        onEdgeMouseLeave={() => setTooltip(null)}
        onEdgeMouseMove={(event) => setTooltip((current) => (current ? { ...current, x: event.clientX, y: event.clientY } : current))}
        onNodeClick={(_, node) => onSelectNode(node.id)}
        onNodeMouseEnter={(event, node) => {
          const data = node.data as RiskFlowNodeData;
          setTooltip({
            x: event.clientX,
            y: event.clientY,
            title: data.graphNode.label,
            meta: `${data.graphNode.kind} / ${data.graphNode.countryCode ?? String(data.graphNode.metadata.country ?? "global")}`,
            detail: `Risk ${graphScore(data.graphNode.riskScore ?? data.graphNode.score)} / centrality ${graphScore(data.graphNode.centralityScore ?? 0)}`,
          });
        }}
        onNodeMouseLeave={() => setTooltip(null)}
        onNodeMouseMove={(event) => setTooltip((current) => (current ? { ...current, x: event.clientX, y: event.clientY } : current))}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="rgba(238,247,242,0.08)" gap={32} size={1} />
        <MiniMap
          className="risk-flow-minimap"
          nodeColor={(node) => graphColorByLevel[(node.data as RiskFlowNodeData).graphNode.level]}
          pannable
          zoomable
        />
        <Controls className="risk-flow-controls" fitViewOptions={{ padding: 0.2 }} />
      </ReactFlow>
      {tooltip ? (
        <div className="risk-flow-tooltip" style={{ left: tooltip.x + 14, top: tooltip.y + 14 }}>
          <strong>{tooltip.title}</strong>
          <span>{tooltip.meta}</span>
          <small>{tooltip.detail}</small>
        </div>
      ) : null}
    </>
  );
}

function useTopologyPositions(
  nodes: GraphNode[],
  links: GraphLink[],
  activePathNodeIndex: Map<string, number>,
): Map<string, GraphPosition> {
  const fallbackPositions = useMemo(
    () => computeRankedTopologyLayout(nodes, links, activePathNodeIndex),
    [nodes, links, activePathNodeIndex]
  );
  const [positions, setPositions] = useState<Map<string, GraphPosition>>(fallbackPositions);

  useEffect(() => {
    let cancelled = false;
    setPositions(fallbackPositions);
    if (nodes.length < 2) return;

    computeElkTopologyLayout(nodes, links, activePathNodeIndex, fallbackPositions)
      .then((layoutPositions) => {
        if (!cancelled) setPositions(layoutPositions);
      })
      .catch(() => {
        if (!cancelled) setPositions(fallbackPositions);
      });

    return () => {
      cancelled = true;
    };
  }, [activePathNodeIndex, fallbackPositions, links, nodes]);

  return positions.size ? positions : fallbackPositions;
}

function RiskFlowNodeCard({ data }: NodeProps<RiskFlowNode>) {
  const node = data.graphNode;
  return (
    <div
      className={`risk-flow-node ${riskClassByLevel[node.level]} ${data.selected ? "is-selected" : ""} ${data.dimmed ? "is-dimmed" : ""} ${data.inActivePath ? "is-path-node" : ""} ${data.isFirstNeighbor ? "is-neighbor" : ""} ${data.selectedPathStep ? "is-step-node" : ""}`}
      style={
        {
          "--node-scale": `${1 + Math.min(0.2, graphScore(node.centralityScore ?? 0) / 500)}`,
          "--critical-ring": `${Math.max(1, Math.min(4, graphScore(node.criticalityScore ?? node.score) / 26))}px`,
        } as CSSProperties
      }
    >
      <Handle className="risk-flow-handle" position={Position.Left} type="target" />
      <Handle className="risk-flow-handle" position={Position.Right} type="source" />
      <div className="risk-flow-node-topline">
        <span>{node.kind}</span>
        <strong>{graphScore(node.criticalityScore ?? node.score)}</strong>
      </div>
      <p>{node.label}</p>
      <small>
        R{graphScore(node.riskScore ?? node.score)} / C{graphScore(node.centralityScore ?? 0)} / {node.countryCode ?? String(node.metadata.country ?? "global")}
      </small>
    </div>
  );
}

function layoutGraphNodes(
  nodes: GraphNode[],
  links: GraphLink[],
  options: {
    activePathNodeIds: Set<string>;
    activePathNodeIndex: Map<string, number>;
    firstNeighborNodeIds: Set<string>;
    layoutPositions?: Map<string, GraphPosition>;
    mode: GraphExplorerMode;
    selectedCountryCode?: string;
    selectedNodeId: string;
    selectedPathStepNodeId?: string;
  },
): RiskFlowNode[] {
  const positions = new Map(options.layoutPositions ?? computeRankedTopologyLayout(nodes, links, options.activePathNodeIndex));
  for (const node of nodes) {
    if (!positions.has(node.id)) positions.set(node.id, { x: 0, y: 0 });
  }
  return nodes.map((node) => {
    const inActivePath = options.activePathNodeIds.has(node.id);
    const isSelected = node.id === options.selectedNodeId;
    const isFirstNeighbor = options.firstNeighborNodeIds.has(node.id);
    const selectedPathStep = node.id === options.selectedPathStepNodeId;
    const countryMatches = options.selectedCountryCode
      ? (node.countryCode ?? String(node.metadata.country ?? "")).toUpperCase() === options.selectedCountryCode
      : true;
    const isFocused =
      isSelected ||
      isFirstNeighbor ||
      selectedPathStep ||
      (options.mode === "path-analysis" && inActivePath) ||
      (options.mode === "country-lens" && countryMatches);
    const dimmed =
      (options.mode === "path-analysis" && options.activePathNodeIds.size > 0 && !isFocused) ||
      (options.mode === "country-lens" && !isFocused) ||
      (options.mode === "risk-centrality" && !isFocused);
    return {
      id: node.id,
      type: "risk",
      position: positions.get(node.id) ?? { x: 0, y: 0 },
      data: { graphNode: node, selected: isSelected, dimmed, inActivePath, isFirstNeighbor, selectedPathStep },
      selected: isSelected,
    };
  });
}

function computeRankedTopologyLayout(
  nodes: GraphNode[],
  links: GraphLink[],
  activePathNodeIndex: Map<string, number>,
): Map<string, GraphPosition> {
  const visibleIds = new Set(nodes.map((node) => node.id));
  const sortedNodes = [...nodes].sort(compareGraphNodesForLayout(activePathNodeIndex));
  const sortedLinks = [...links]
    .filter((link) => visibleIds.has(link.source) && visibleIds.has(link.target))
    .sort((a, b) => a.source.localeCompare(b.source) || a.target.localeCompare(b.target) || a.id.localeCompare(b.id));
  const outgoing = new Map<string, GraphLink[]>();
  const indegree = new Map<string, number>();
  const rankById = new Map<string, number>();
  for (const node of sortedNodes) {
    outgoing.set(node.id, []);
    indegree.set(node.id, 0);
    rankById.set(node.id, graphKindRankHint[node.kind]);
  }
  for (const link of sortedLinks) {
    outgoing.get(link.source)?.push(link);
    indegree.set(link.target, (indegree.get(link.target) ?? 0) + 1);
  }

  const queue = sortedNodes.filter((node) => (indegree.get(node.id) ?? 0) === 0);
  for (let index = 0; index < queue.length; index += 1) {
    const node = queue[index];
    for (const link of outgoing.get(node.id) ?? []) {
      rankById.set(link.target, Math.max(rankById.get(link.target) ?? 0, (rankById.get(node.id) ?? 0) + 1));
      indegree.set(link.target, Math.max(0, (indegree.get(link.target) ?? 0) - 1));
      if (indegree.get(link.target) === 0) {
        const target = sortedNodes.find((candidate) => candidate.id === link.target);
        if (target) queue.push(target);
      }
    }
  }

  // Clean replacement point for a future ELK adapter: keep the input/output pure and deterministic.
  for (const link of sortedLinks) {
    const sourceRank = rankById.get(link.source) ?? 0;
    const targetRank = rankById.get(link.target) ?? 0;
    if (targetRank <= sourceRank) rankById.set(link.target, sourceRank + 1);
  }

  const compressedRanks = new Map<number, number>();
  [...new Set([...rankById.values()].sort((a, b) => a - b))].forEach((rank, index) => compressedRanks.set(rank, index));
  const rankGroups = new Map<number, GraphNode[]>();
  for (const node of nodes) {
    const rank = compressedRanks.get(rankById.get(node.id) ?? 0) ?? 0;
    rankGroups.set(rank, [...(rankGroups.get(rank) ?? []), node]);
  }

  const maxRank = Math.max(0, ...rankGroups.keys());
  const positions = new Map<string, GraphPosition>();
  const rankGap = 310;
  const rowGap = 120;
  for (const [rank, rankNodes] of [...rankGroups.entries()].sort((a, b) => a[0] - b[0])) {
    const ordered = [...rankNodes].sort(compareGraphNodesForLayout(activePathNodeIndex));
    const count = ordered.length;
    ordered.forEach((node, index) => {
      const centerOffset = index - (count - 1) / 2;
      const denseRankOffset = count > 8 ? ((index % 2) - 0.5) * 46 : 0;
      positions.set(node.id, {
        x: (rank - maxRank / 2) * rankGap + denseRankOffset,
        y: centerOffset * rowGap,
      });
    });
  }
  return positions;
}

async function computeElkTopologyLayout(
  nodes: GraphNode[],
  links: GraphLink[],
  activePathNodeIndex: Map<string, number>,
  fallbackPositions: Map<string, GraphPosition>,
): Promise<Map<string, GraphPosition>> {
  const { default: ELK } = await import("elkjs/lib/elk.bundled.js");
  const visibleIds = new Set(nodes.map((node) => node.id));
  const sortedNodes = [...nodes].sort(compareGraphNodesForLayout(activePathNodeIndex));
  const sortedLinks = [...links]
    .filter((link) => visibleIds.has(link.source) && visibleIds.has(link.target) && link.source !== link.target)
    .sort((a, b) => a.source.localeCompare(b.source) || a.target.localeCompare(b.target) || a.id.localeCompare(b.id));
  const nodeWidth = 220;
  const nodeHeight = 92;
  const graph: ElkNode = {
    id: "risk-topology",
    layoutOptions: {
      "elk.algorithm": "layered",
      "elk.direction": "RIGHT",
      "elk.edgeRouting": "ORTHOGONAL",
      "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES",
      "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",
      "elk.layered.nodePlacement.strategy": "NETWORK_SIMPLEX",
      "elk.layered.spacing.edgeNodeBetweenLayers": "52",
      "elk.layered.spacing.nodeNodeBetweenLayers": "112",
      "elk.spacing.nodeNode": "42",
    },
    children: sortedNodes.map((node, index) => ({
      id: node.id,
      width: nodeWidth,
      height: nodeHeight,
      layoutOptions: {
        "elk.priority": String((4 - graphKindRankHint[node.kind]) * 100 + sortedNodes.length - index),
      },
    })),
    edges: sortedLinks.map((link) => ({
      id: link.id,
      sources: [link.source],
      targets: [link.target],
      layoutOptions: {
        "elk.priority": String(Math.round((link.transmissionWeight ?? link.weight ?? 0.2) * 100)),
      },
    })),
  };
  const elk = new ELK();
  const layouted = await elk.layout(graph);
  const rawPositions = new Map<string, GraphPosition>();
  for (const child of layouted.children ?? []) {
    rawPositions.set(child.id, {
      x: (child.x ?? fallbackPositions.get(child.id)?.x ?? 0) + nodeWidth / 2,
      y: (child.y ?? fallbackPositions.get(child.id)?.y ?? 0) + nodeHeight / 2,
    });
  }
  if (rawPositions.size < Math.max(1, Math.floor(nodes.length * 0.75))) return fallbackPositions;

  const xs = [...rawPositions.values()].map((position) => position.x);
  const ys = [...rawPositions.values()].map((position) => position.y);
  const centerX = (Math.min(...xs) + Math.max(...xs)) / 2;
  const centerY = (Math.min(...ys) + Math.max(...ys)) / 2;
  const positions = new Map<string, GraphPosition>();
  for (const node of nodes) {
    const raw = rawPositions.get(node.id) ?? fallbackPositions.get(node.id) ?? { x: 0, y: 0 };
    positions.set(node.id, { x: raw.x - centerX, y: raw.y - centerY });
  }
  return positions;
}

function compareGraphNodesForLayout(activePathNodeIndex: Map<string, number>) {
  return (a: GraphNode, b: GraphNode) => {
    const aPathIndex = activePathNodeIndex.get(a.id);
    const bPathIndex = activePathNodeIndex.get(b.id);
    if (aPathIndex !== undefined || bPathIndex !== undefined) {
      return (aPathIndex ?? Number.POSITIVE_INFINITY) - (bPathIndex ?? Number.POSITIVE_INFINITY);
    }
    return (
      riskLevelRank(b.level) - riskLevelRank(a.level) ||
      graphScore(b.criticalityScore ?? b.score) - graphScore(a.criticalityScore ?? a.score) ||
      graphKindRankHint[a.kind] - graphKindRankHint[b.kind] ||
      a.label.localeCompare(b.label) ||
      a.id.localeCompare(b.id)
    );
  };
}

function layoutGraphEdges(
  links: GraphLink[],
  visibleNodeIds: Set<string>,
  options: {
    activePathEdgeIds: Set<string>;
    firstNeighborNodeIds: Set<string>;
    mode: GraphExplorerMode;
    selectedCountryCode?: string;
    selectedEdgeId: string | null;
    selectedNodeId: string;
    selectedPathStepEdgeId?: string;
    selectedPathStepNodeId?: string;
  },
): RiskFlowEdge[] {
  return links
    .filter((link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target))
    .map((link) => {
      const color = graphColorByLevel[link.level];
      const isSelectedAdjacency = link.source === options.selectedNodeId || link.target === options.selectedNodeId;
      const isActivePath = options.activePathEdgeIds.has(link.id);
      const isSelectedEdge = link.id === options.selectedEdgeId;
      const isSelectedPathStep = link.id === options.selectedPathStepEdgeId;
      const isFirstNeighbor =
        options.firstNeighborNodeIds.has(link.source) ||
        options.firstNeighborNodeIds.has(link.target) ||
        link.source === options.selectedPathStepNodeId ||
        link.target === options.selectedPathStepNodeId;
      const countryFocused =
        options.selectedCountryCode &&
        (link.sourceCountry === options.selectedCountryCode || link.targetCountry === options.selectedCountryCode);
      const isFocused =
        isActivePath ||
        isSelectedEdge ||
        isSelectedPathStep ||
        isSelectedAdjacency ||
        isFirstNeighbor ||
        (options.mode === "country-lens" && Boolean(countryFocused));
      const baseWidth = link.transmissionWeight ?? link.weight;
      return {
        id: link.id,
        source: link.source,
        target: link.target,
        type: "smoothstep",
        animated: isSelectedPathStep || isActivePath,
        label: isSelectedPathStep || isActivePath || isSelectedEdge || link.level === "critical" ? link.label : undefined,
        data: { level: link.level, label: link.label, role: link.edgeRole, activePath: isActivePath },
        markerEnd: { type: MarkerType.ArrowClosed, color },
        style: {
          stroke: color,
          strokeOpacity: isFocused ? (isSelectedPathStep || isSelectedEdge ? 0.98 : 0.78) : 0.16,
          strokeWidth: isSelectedPathStep || isActivePath || isSelectedEdge ? 4.8 : Math.max(1.1, Math.min(4.4, baseWidth * 4.8)),
        },
      };
    });
}

function riskLevelRank(level: RiskLevel) {
  return { low: 0, guarded: 1, elevated: 2, severe: 3, critical: 4 }[level];
}

function graphScore(value: number | undefined, fallback = 0) {
  const score = value ?? fallback;
  if (!Number.isFinite(score)) return 0;
  return Math.round(score <= 1 ? score * 100 : score);
}

function predictionRiskLevelToUi(level?: Prediction["risk_level"], score?: number): RiskLevel {
  if (level === "critical") return "critical";
  if (level === "high") return "severe";
  if (level === "medium") return "elevated";
  if (level === "low") return "low";
  const numericScore = score ?? 0;
  if (numericScore >= 0.88) return "critical";
  if (numericScore >= 0.65) return "severe";
  if (numericScore >= 0.35) return "elevated";
  return "low";
}

function NetworkSvg({ links, nodes }: { links: GraphLink[]; nodes: GraphNode[] }) {
  const nodeById = new Map(nodes.map((node) => [node.id, node]));

  return (
    <svg className="svg-network" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
      {links.map((link) => {
        const source = nodeById.get(link.source);
        const target = nodeById.get(link.target);
        if (!source || !target) return null;

        return (
          <line
            key={link.id}
            x1={source.x}
            y1={source.y}
            x2={target.x}
            y2={target.y}
            stroke="rgba(196,255,77,0.32)"
            strokeDasharray={link.level === "critical" || link.level === "severe" ? "0" : "2 2"}
            strokeLinecap="round"
            strokeWidth={0.45 + link.weight}
            vectorEffect="non-scaling-stroke"
          />
        );
      })}
    </svg>
  );
}

function CompanyRisk360({ data }: { data: SupplyRiskDashboardData }) {
  const { t } = useI18n();
  const companyData = data.companyRisk360;
  const [selectedCompanyId, setSelectedCompanyId] = useState(companyData.selectedCompanyId);
  const selectedCompany =
    companyData.companies.find((company) => company.id === selectedCompanyId) ?? companyData.companies[0];

  return (
    <div className="page-grid split-layout">
      <Panel title="Company watchlist" subtitle="Board-level exposure by target company.">
        <div className="company-list">
          {companyData.companies.map((company) => (
            <button
              className={`version-card ${selectedCompany.id === company.id ? "is-selected" : ""}`}
              key={company.id}
              onClick={() => setSelectedCompanyId(company.id)}
              type="button"
            >
              <div className="row-top">
                <div>
                  <span className="row-title">{company.name}</span>
                  <span className="row-subtitle">
                    {company.ticker} / {company.sector}
                  </span>
                </div>
                <RiskPill level={company.level} />
              </div>
              <ProgressBar value={company.riskScore} level={company.level} />
            </button>
          ))}
        </div>
      </Panel>

      <div className="page-grid">
        <Panel
          title={`${selectedCompany.name} ${t("risk posture")}`}
          subtitle={`${selectedCompany.headquarters}; ${t("confidence")} ${formatPercent(selectedCompany.confidence)}.`}
          translateTitle={false}
          translateSubtitle={false}
          action={<Button icon={ShieldAlert}>Create watch</Button>}
        >
          <div className="driver-grid">
            <ScoreDial score={selectedCompany.riskScore} level={selectedCompany.level} label="Risk score" />
            <div className="inspector-grid">
              <Field label="Revenue at risk" value={formatUsdCompact(selectedCompany.revenueAtRiskUsd)} />
              <Field label="Supplier count" value={selectedCompany.suppliers.length} />
              <Field label="Top dependency" value={selectedCompany.suppliers[0]?.supplier ?? "None"} />
              <Field label="Confidence" value={formatPercent(selectedCompany.confidence)} />
            </div>
          </div>
        </Panel>

        <Panel title="Drivers and mitigations" subtitle="Highest contribution factors and current response plan.">
          <div className="driver-grid">
            <ul className="timeline-list">
              {selectedCompany.topDrivers.map((driver) => (
                <li className="data-row" key={driver}>
                  <span className="row-title">{driver}</span>
                </li>
              ))}
            </ul>
            <ul className="recommendation-list">
              {selectedCompany.mitigations.map((mitigation) => (
                <li className="data-row" key={mitigation}>
                  <span className="row-title">{mitigation}</span>
                </li>
              ))}
            </ul>
          </div>
        </Panel>

        <Panel title="Supplier exposure table" subtitle="Spend share, dependency, and lead time by supplier.">
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t("Supplier")}</th>
                  <th>{t("Country")}</th>
                  <th>{t("Category")}</th>
                  <th>{t("Spend")}</th>
                  <th>{t("Dependency")}</th>
                  <th>{t("Lead time")}</th>
                  <th>{t("Level")}</th>
                </tr>
              </thead>
              <tbody>
                {selectedCompany.suppliers.map((supplier) => (
                  <tr key={supplier.id}>
                    <td>{supplier.supplier}</td>
                    <td>{supplier.country}</td>
                    <td>{supplier.category}</td>
                    <td>{formatPercent(supplier.spendShare)}</td>
                    <td>{formatPercent(supplier.dependency)}</td>
                    <td>{t(`${supplier.leadTimeDays} days`)}</td>
                    <td>
                      <RiskPill level={supplier.level} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function PredictionCenter({ data }: { data: SupplyRiskDashboardData }) {
  const { t } = useI18n();
  const center = data.predictionCenter;
  const predictions = center.predictions;
  const [selectedPredictionId, setSelectedPredictionId] = useState(
    center.topPredictions[0]?.prediction_id ?? predictions[0]?.prediction_id ?? "",
  );
  const selectedPrediction =
    predictions.find((prediction) => prediction.prediction_id === selectedPredictionId) ??
    center.topPredictions[0] ??
    predictions[0];
  const selectedLevel = predictionRiskLevelToUi(selectedPrediction?.risk_level);

  if (!selectedPrediction) {
    return <div className="empty-state">{t("No predictions are available from the current graph.")}</div>;
  }

  return (
    <div className="prediction-center-layout">
      <Panel title="Forecast queue" subtitle="Public-evidence graph ensemble, sorted by risk and confidence." className="prediction-queue-panel">
        <div className="inspector-grid prediction-summary-grid">
          <Field label="Model" value={center.modelVersion} />
          <Field label="Form" value={center.predictionForm} />
          <Field label="High confidence" value={center.highConfidenceCount} />
          <Field label="Saturated scores" value={center.saturatedScoreCount} />
        </div>
        <ul className="prediction-list">
          {center.topPredictions.slice(0, 14).map((prediction) => (
            <li key={prediction.prediction_id}>
              <button
                className={`prediction-row ${prediction.prediction_id === selectedPrediction.prediction_id ? "is-active" : ""}`}
                onClick={() => setSelectedPredictionId(prediction.prediction_id)}
                type="button"
              >
                <span>
                  <strong>{prediction.target_id}</strong>
                  <small>{prediction.mechanism ?? "public_evidence_graph"} / {prediction.horizon}d</small>
                </span>
                <b>{Math.round(prediction.risk_score * 100)}</b>
              </button>
            </li>
          ))}
        </ul>
      </Panel>

      <div className="page-grid">
        <Panel
          title="Prediction workbench"
          subtitle="Mechanism labels, confidence bands, and driver attribution from the active graph."
          action={<RiskPill level={selectedLevel} />}
        >
          <div className="prediction-workbench">
            <ScoreDial score={Math.round(selectedPrediction.risk_score * 100)} level={selectedLevel} label="Risk score" />
            <div className="inspector-grid">
              <Field label="Target" value={selectedPrediction.target_id} />
              <Field label="Mechanism" value={selectedPrediction.mechanism ?? "public_evidence_graph"} />
              <Field label="Horizon" value={`${selectedPrediction.horizon} days`} />
              <Field
                label="Confidence band"
                value={`${Math.round(selectedPrediction.confidence_low * 100)}-${Math.round(selectedPrediction.confidence_high * 100)}`}
              />
              <Field label="Path count" value={selectedPrediction.path_details?.length ?? selectedPrediction.top_paths.length} />
              <Field label="Evidence refs" value={selectedPrediction.evidence_refs?.length ?? 0} />
            </div>
          </div>
        </Panel>

        <Panel title="Score mechanism" subtitle="Weighted components explain why the forecast moved.">
          <div className="component-stack">
            {Object.entries(selectedPrediction.score_components ?? {}).map(([component, value]) => (
              <div className="component-row" key={component}>
                <div>
                  <strong>{component.replaceAll("_", " ")}</strong>
                  <small>{Math.round((value ?? 0) * 100)}/100</small>
                </div>
                <ProgressBar value={Math.round((value ?? 0) * 100)} level={selectedLevel} />
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Driver attribution" subtitle="Contribution-ranked features and paths.">
          <ul className="evidence-list compact">
            {(selectedPrediction.driver_contributions ?? []).slice(0, 8).map((driver) => (
              <li key={`${driver.driver}-${driver.pathId ?? "component"}`}>
                {driver.driver.replaceAll("_", " ")}: {Math.round(driver.contribution * 100)} contribution
                {driver.pathId ? ` / ${driver.pathId}` : ""}
              </li>
            ))}
          </ul>
        </Panel>

        <Panel title="Evidence paths" subtitle="Top transmission paths used by this prediction.">
          <div className="prediction-path-grid">
            {(selectedPrediction.path_details ?? []).slice(0, 4).map((path) => (
              <article className="prediction-path-card" key={path.pathId}>
                <div className="row-top">
                  <span className="row-title">{path.nodeLabels.join(" -> ")}</span>
                  <b>{Math.round(path.transmissionScore * 100)}</b>
                </div>
                <small>{path.edgeTypes.join(" -> ")}</small>
                <div className="lineage-chips">
                  {path.evidenceRefs.slice(0, 3).map((ref) => (
                    <span key={ref}>{ref}</span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </Panel>

        <Panel title="Mechanism mix" subtitle="Which public-evidence mechanisms are active.">
          <div className="mechanism-grid">
            {center.mechanisms.map((mechanism) => (
              <article className="mechanism-card" key={mechanism.mechanism}>
                <strong>{mechanism.mechanism.replaceAll("_", " ")}</strong>
                <span>{mechanism.count} forecasts</span>
                <ProgressBar value={Math.round(mechanism.maxRisk * 100)} level={predictionRiskLevelToUi(undefined, mechanism.maxRisk)} />
              </article>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}

function PathExplainer({ data }: { data: SupplyRiskDashboardData }) {
  const { t } = useI18n();
  const pathData = data.pathExplainer;
  const [selectedPathId, setSelectedPathId] = useState(pathData.selectedPathId);
  const selectedPath = pathData.paths.find((path) => path.id === selectedPathId) ?? pathData.paths[0];

  return (
    <div className="page-grid">
      <Panel
        title="Explained path selector"
        subtitle="Trace the concrete graph route behind a risk score movement."
        action={<Button icon={GitBranch}>Pin explanation</Button>}
      >
        <div className="segmented" aria-label={t("Explained path")}>
          {pathData.paths.map((path) => (
            <button
              className={`segment ${selectedPath.id === path.id ? "is-active" : ""}`}
              key={path.id}
              onClick={() => setSelectedPathId(path.id)}
              type="button"
            >
              {path.targetCompany}
            </button>
          ))}
        </div>
      </Panel>

      <Panel
        title={selectedPath.title}
        subtitle={`${selectedPath.scoreMove.toFixed(1)} point score move; ${formatPercent(selectedPath.confidence)} explanation confidence.`}
        translateTitle={false}
      >
        <p className="panel-subtitle" style={{ marginBottom: 16 }}>
          {selectedPath.summary}
        </p>
        <PathStrip path={selectedPath} />
      </Panel>
    </div>
  );
}

function PathStrip({ path }: { path: ExplainedPath }) {
  const { t } = useI18n();
  return (
    <div className="path-strip">
      {path.steps.map((step) => (
        <article className="path-step" key={step.id}>
          <div className="row-top">
            <RiskPill level={step.level} />
            <span className="method-pill">{t(step.kind)}</span>
          </div>
          <p className="contribution">+{step.contribution}%</p>
          <span className="row-title">{step.label}</span>
          <span className="row-subtitle">{step.evidence}</span>
        </article>
      ))}
    </div>
  );
}

function ShockSimulator({ apiClient }: { apiClient: SupplyRiskApiClient }) {
  const { t } = useI18n();
  const [input, setInput] = useState<ShockSimulationInput>({
    region: "Taiwan Strait",
    commodity: "advanced semiconductor components",
    severity: 72,
    durationDays: 28,
    scope: "regional"
  });
  const [result, setResult] = useState<ShockSimulationResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [simulationWarning, setSimulationWarning] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    setIsRunning(true);
    apiClient
      .runShockSimulation(input)
      .then((nextResult) => {
        if (!isActive) return;
        if (isAcceptedRealApiResult(nextResult)) {
          setResult(nextResult.data);
          setSimulationWarning(null);
          return;
        }
        setResult(null);
        setSimulationWarning("Simulation requires a real API envelope before results are rendered.");
      })
      .catch((error: unknown) => {
        if (!isActive) return;
        setResult(null);
        setSimulationWarning(error instanceof Error ? error.message : "Simulation API request failed.");
      })
      .finally(() => {
        if (isActive) setIsRunning(false);
      });

    return () => {
      isActive = false;
    };
  }, [apiClient, input]);

  const setNumber = (key: "severity" | "durationDays") => (event: ChangeEvent<HTMLInputElement>) => {
    setInput((current) => ({ ...current, [key]: Number(event.target.value) }));
  };

  return (
    <div className="page-grid split-layout">
      <Panel
        title="Shock controls"
        subtitle="Change the scenario and the impact model recalculates against the active graph."
        action={<Button icon={Play} variant="primary">{isRunning ? "Running" : "Run"}</Button>}
      >
        <div className="form-grid">
          <label className="form-control">
            <span>{t("Region")}</span>
            <select value={input.region} onChange={(event) => setInput((current) => ({ ...current, region: event.target.value }))}>
              <option value="Taiwan Strait">Taiwan Strait</option>
              <option value="Red Sea / Suez">Red Sea / Suez</option>
              <option value="Panama Canal">Panama Canal</option>
              <option value="Rhine Industrial Belt">Rhine Industrial Belt</option>
            </select>
          </label>
          <label className="form-control">
            <span>{t("Commodity")}</span>
            <select
              value={input.commodity}
              onChange={(event) => setInput((current) => ({ ...current, commodity: event.target.value }))}
            >
              <option value="advanced semiconductor components">advanced semiconductor components</option>
              <option value="battery graphite">battery graphite</option>
              <option value="specialty chemical feedstock">specialty chemical feedstock</option>
              <option value="consumer electronics assemblies">consumer electronics assemblies</option>
            </select>
          </label>
          <label className="form-control">
            <span>{t("Severity")}: {input.severity}</span>
            <input min="10" max="100" onChange={setNumber("severity")} type="range" value={input.severity} />
          </label>
          <label className="form-control">
            <span>{t("Duration")}: {t(`${input.durationDays} days`)}</span>
            <input min="3" max="90" onChange={setNumber("durationDays")} type="range" value={input.durationDays} />
          </label>
          <label className="form-control">
            <span>{t("Scope")}</span>
            <select value={input.scope} onChange={(event) => setInput((current) => ({ ...current, scope: event.target.value as ShockSimulationInput["scope"] }))}>
              <option value="facility">{t("Facility")}</option>
              <option value="regional">{t("Regional")}</option>
              <option value="global">{t("Global")}</option>
            </select>
          </label>
        </div>
      </Panel>

      <div className="page-grid">
        <Panel title="Projected impact" subtitle="Rendered only from an accepted real API envelope.">
          {result ? (
            <div className="three-column page-grid">
              <div className={`big-result ${riskClassByLevel[result.affectedPaths[0]?.level ?? "guarded"]}`}>
                <span>{t("Impact score")}</span>
                <strong>{result.impactScore}</strong>
              </div>
              <div className="big-result tone-elevated">
                <span>{t("EBITDA at risk")}</span>
                <strong>{formatUsdCompact(result.ebitdaAtRiskUsd)}</strong>
              </div>
              <div className="big-result tone-guarded">
                <span>{t("Recovery time")}</span>
                <strong>{t(`${result.timeToRecoveryDays}d`)}</strong>
              </div>
            </div>
          ) : (
            <div className="empty-state">{t(simulationWarning ?? "Awaiting simulation result.")}</div>
          )}
        </Panel>

        {result ? (
          <>
            <Panel title="Affected paths" subtitle={`${result.affectedCompanies} companies touched by this scenario.`}>
              <ul className="timeline-list">
                {result.affectedPaths.map((path) => (
                  <li className="data-row" key={path.id}>
                    <div className="row-top">
                      <span className="row-title">{path.label}</span>
                      <RiskPill level={path.level} />
                    </div>
                    <ProgressBar value={path.impact} level={path.level} />
                  </li>
                ))}
              </ul>
            </Panel>

            <Panel title="Mitigation queue" subtitle="Operational actions ranked by speed-to-impact.">
              <ul className="recommendation-list">
                {result.recommendations.map((recommendation) => (
                  <li className="data-row" key={recommendation}>
                    <span className="row-title">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </Panel>
          </>
        ) : null}
      </div>
    </div>
  );
}

function CausalEvidenceBoard({ data }: { data: SupplyRiskDashboardData }) {
  const { t } = useI18n();
  const board = data.causalEvidenceBoard;
  const [activeClaimId, setActiveClaimId] = useState(board.activeClaimId);
  const activeClaim = board.evidence.find((claim) => claim.id === activeClaimId) ?? board.evidence[0];

  return (
    <div className="page-grid split-layout">
      <Panel title="Evidence register" subtitle="Causal claims are scored for confidence and disagreement.">
        <div className="evidence-list">
          {board.evidence.map((item) => (
            <EvidenceButton
              item={item}
              isActive={item.id === activeClaim.id}
              key={item.id}
              onSelect={() => setActiveClaimId(item.id)}
            />
          ))}
        </div>
      </Panel>

      <div className="page-grid">
        <Panel
          title="Causal claim focus"
          subtitle={activeClaim.source}
          translateSubtitle={false}
          action={<span className="method-pill">{activeClaim.method}</span>}
        >
          <div className="driver-grid">
            <div>
              <p className="row-title">{activeClaim.claim}</p>
              <div className="inspector-grid" style={{ marginTop: 16 }}>
                <Field label="Confidence" value={formatPercent(activeClaim.confidence)} />
                <Field label="Disagreement" value={formatPercent(activeClaim.disagreement)} />
                <Field label="Reviewed" value={activeClaim.lastReviewed} />
                <Field label="Level" value={<RiskPill level={activeClaim.level} />} />
              </div>
            </div>
            <div className="causal-canvas" role="img" aria-label={t("Causal evidence mini graph")}>
              <NetworkSvg
                nodes={[
                  { id: "shock", label: t("Shock"), kind: "route", level: activeClaim.level, score: 80, x: 18, y: 48, metadata: {} },
                  { id: "mechanism", label: t("Mechanism"), kind: "facility", level: "elevated", score: 66, x: 50, y: 28, metadata: {} },
                  { id: "outcome", label: t("Outcome"), kind: "company", level: activeClaim.level, score: 78, x: 78, y: 62, metadata: {} }
                ]}
                links={[
                  { id: "a", source: "shock", target: "mechanism", label: t("causes"), weight: 0.76, level: activeClaim.level },
                  { id: "b", source: "mechanism", target: "outcome", label: t("shifts"), weight: 0.62, level: "elevated" }
                ]}
              />
            </div>
          </div>
        </Panel>

        <Panel title="Evidence quality" subtitle="Confidence and disagreement are tracked separately.">
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t("Claim")}</th>
                  <th>{t("Method")}</th>
                  <th>{t("Confidence")}</th>
                  <th>{t("Disagreement")}</th>
                  <th>{t("Level")}</th>
                </tr>
              </thead>
              <tbody>
                {board.evidence.map((item) => (
                  <tr key={item.id}>
                    <td>{item.claim}</td>
                    <td>{item.method}</td>
                    <td>{formatPercent(item.confidence)}</td>
                    <td>{formatPercent(item.disagreement)}</td>
                    <td>
                      <RiskPill level={item.level} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function EvidenceButton({ item, isActive, onSelect }: { item: EvidenceItem; isActive: boolean; onSelect: () => void }) {
  const { t } = useI18n();
  return (
    <button className={`evidence-card ${isActive ? "is-active" : ""}`} onClick={onSelect} type="button">
      <div className="row-top">
        <span className="row-title">{item.claim}</span>
        <RiskPill level={item.level} />
      </div>
      <span className="row-subtitle">{item.source}</span>
      <ProgressBar value={item.confidence * 100} level={item.level} />
      <div className="row-meta">
        <span>{t(item.method)}</span>
        <span>{t(`${formatPercent(item.disagreement)} disagreement`)}</span>
      </div>
    </button>
  );
}

function GraphVersionStudio({ data }: { data: SupplyRiskDashboardData }) {
  const { t } = useI18n();
  const studio = data.graphVersionStudio;
  const [candidateVersionId, setCandidateVersionId] = useState(studio.candidateVersionId);
  const [promotedVersionId, setPromotedVersionId] = useState(studio.baselineVersionId);
  const candidate = studio.versions.find((version) => version.id === candidateVersionId) ?? studio.versions[0];

  return (
    <div className="page-grid split-layout">
      <Panel title="Graph builds" subtitle="Select a candidate and compare it against the promoted baseline.">
        <div className="version-list">
          {studio.versions.map((version) => (
            <VersionButton
              isPromoted={version.id === promotedVersionId}
              isSelected={version.id === candidate.id}
              key={version.id}
              onSelect={() => setCandidateVersionId(version.id)}
              version={version}
            />
          ))}
        </div>
      </Panel>

      <div className="page-grid">
        <Panel
          title="Candidate readiness"
          subtitle={`${candidate.label}; built by ${candidate.author}.`}
          translateSubtitle={false}
          action={<Button icon={CheckCircle2} variant="primary" onClick={() => setPromotedVersionId(candidate.id)}>Promote</Button>}
        >
          <div className="version-grid">
            <Field label="Nodes" value={formatCompactNumber(candidate.nodes)} />
            <Field label="Edges" value={formatCompactNumber(candidate.edges)} />
            <Field label="Schema changes" value={candidate.schemaChanges} />
            <Field label="Validation pass rate" value={formatPercent(candidate.validationPassRate, 1)} />
          </div>
        </Panel>

        <Panel title="Diff matrix" subtitle="Material graph changes detected against the promoted baseline.">
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t("Area")}</th>
                  <th>{t("Change")}</th>
                  <th>{t("Count")}</th>
                  <th>{t("Severity")}</th>
                </tr>
              </thead>
              <tbody>
                {studio.diffRows.map((row) => (
                  <tr key={row.id}>
                    <td>{row.area}</td>
                    <td>{row.change}</td>
                    <td>{formatCompactNumber(row.count)}</td>
                    <td>
                      <RiskPill level={row.severity} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function VersionButton({
  version,
  isSelected,
  isPromoted,
  onSelect
}: {
  version: GraphVersion;
  isSelected: boolean;
  isPromoted: boolean;
  onSelect: () => void;
}) {
  const { t } = useI18n();
  return (
    <button className={`version-card ${isSelected ? "is-selected" : ""}`} onClick={onSelect} type="button">
      <div className="row-top">
        <div>
          <span className="row-title">{version.label}</span>
          <span className="row-subtitle">{version.createdAt}</span>
        </div>
        <StatusPill status={isPromoted ? "promoted" : version.status} />
      </div>
      <ProgressBar
        value={version.validationPassRate * 100}
        level={version.validationPassRate > 0.98 ? "low" : "elevated"}
      />
      <div className="row-meta">
        <span>{t(`${formatCompactNumber(version.nodes)} nodes`)}</span>
        <span>{t(`${formatCompactNumber(version.edges)} edges`)}</span>
      </div>
    </button>
  );
}

function SystemHealthCenter({ data }: { data: SupplyRiskDashboardData }) {
  const { t } = useI18n();
  const health = data.systemHealthCenter;
  const operationalCount = health.services.filter((service) => service.status === "operational").length;
  const pipelineTotal = health.stages.reduce((total, stage) => total + stage.total, 0);
  const pipelineProcessed = health.stages.reduce((total, stage) => total + stage.processed, 0);
  const sortedLatencies = [...health.services].map((service) => service.latencyMs).sort((left, right) => left - right);
  const medianLatency = sortedLatencies.length === 0 ? 0 : sortedLatencies[Math.floor(sortedLatencies.length / 2)];
  const maxFreshnessLag = Math.max(0, ...health.services.map((service) => service.freshnessMinutes));
  const serviceSummaryStatus =
    health.services.some((service) => service.status === "down")
      ? "down"
      : operationalCount === health.services.length
        ? "operational"
        : "degraded";
  const stageSummaryStatus = health.stages.some((stage) => stage.status === "blocked")
    ? "blocked"
    : health.stages.some((stage) => stage.status === "running")
      ? "running"
      : health.stages.some((stage) => stage.status === "queued")
        ? "queued"
        : "complete";
  const freshnessStatus = maxFreshnessLag === 0 ? "operational" : "degraded";
  const manifestChecksum = health.sourceRegistry.checksum.slice(0, 12);

  return (
    <div className="page-grid">
      <div className="metrics-grid">
        <article className="metric-tile">
          <div className="metric-head">
            <p className="metric-label">{t("Services operational")}</p>
            <StatusPill status={serviceSummaryStatus} />
          </div>
          <p className="metric-value">
            {operationalCount}
            <span className="metric-unit">/{health.services.length}</span>
          </p>
          <p className="metric-detail">{t("API, graph, model, and signal ingest fleet.")}</p>
        </article>
        <article className="metric-tile">
          <div className="metric-head">
            <p className="metric-label">{t("Pipeline processed")}</p>
            <StatusPill status={stageSummaryStatus} />
          </div>
          <p className="metric-value">{formatPercent(pipelineTotal === 0 ? 0 : pipelineProcessed / pipelineTotal)}</p>
          <p className="metric-detail">{t("Current build is advancing through entity resolution.")}</p>
        </article>
        <article className="metric-tile">
          <div className="metric-head">
            <p className="metric-label">{t("Median latency")}</p>
            <StatusPill status={serviceSummaryStatus} />
          </div>
          <p className="metric-value">
            {medianLatency}<span className="metric-unit">ms</span>
          </p>
          <p className="metric-detail">{t("Across API, graph query, ingest, and scorer endpoints.")}</p>
        </article>
        <article className="metric-tile">
          <div className="metric-head">
            <p className="metric-label">{t("Freshness lag")}</p>
            <StatusPill status={freshnessStatus} />
          </div>
          <p className="metric-value">
            {maxFreshnessLag}<span className="metric-unit">m</span>
          </p>
          <p className="metric-detail">{t("Signal ingest is the current freshness constraint.")}</p>
        </article>
      </div>

      <div className="page-grid split-layout">
        <Panel title="Service status" subtitle="Runtime health by service owner.">
          <ul className="health-list">
            {health.services.map((service) => (
              <li className="data-row" key={service.id}>
                <div className="row-top">
                  <div>
                    <span className="row-title">{service.service}</span>
                    <span className="row-subtitle">{service.owner}</span>
                  </div>
                  <StatusPill status={service.status} />
                </div>
                <div className="row-meta">
                  <span>{t(`${service.latencyMs} ms`)}</span>
                  <span>{t(`${service.freshnessMinutes} m freshness`)}</span>
                  <span>{t(`${formatPercent(service.errorRate, 1)} errors`)}</span>
                </div>
              </li>
            ))}
          </ul>
        </Panel>

        <div className="page-grid">
          <Panel title="Build pipeline" subtitle="Current graph and scoring run progress.">
            <ul className="timeline-list">
              {health.stages.map((stage) => {
                const value = stage.total === 0 ? 0 : (stage.processed / stage.total) * 100;
                return (
                  <li className="data-row stage-row" key={stage.id}>
                    <span className="row-title">{stage.label}</span>
                    <ProgressBar value={value} level={stage.status === "blocked" ? "critical" : "guarded"} />
                    <StatusPill status={stage.status} />
                  </li>
                );
              })}
            </ul>
          </Panel>

          <Panel
            title="Source registry"
            subtitle={`${health.sourceRegistry.manifestRef}; checksum ${manifestChecksum}; catalog ${health.sourceRegistry.catalogSource ?? "unknown"}.`}
            translateSubtitle={false}
          >
            <div className="inspector-grid" style={{ marginBottom: 16 }}>
              <Field label="Sources" value={health.sourceRegistry.sourceCount} />
              <Field label="Raw records" value={health.sourceRegistry.rawRecordCount} />
              <Field label="Silver entities" value={health.sourceRegistry.silverEntityCount} />
              <Field label="Gold edges" value={health.sourceRegistry.goldEdgeEventCount} />
              <Field label="Data nodes" value={health.sourceRegistry.dataNodeCount ?? 0} />
              <Field label="Promoted" value={health.sourceRegistry.promotedGraph?.status ?? "partial"} />
            </div>
            <ul className="health-list">
              {health.sourceRegistry.sources.map((source) => (
                <li className="data-row" key={source.id}>
                  <div className="row-top">
                    <div>
                      <span className="row-title">{source.name}</span>
                      <span className="row-subtitle">{source.license}</span>
                    </div>
                    <StatusPill status={source.status} />
                  </div>
                  <div className="row-meta">
                    <span>{source.updateFrequency}</span>
                    <span>{t(`${source.recordCount} records`)}</span>
                    <span>{t(`${source.maxStaleMinutes} m SLA`)}</span>
                    <span>{source.checksum.slice(0, 10)}</span>
                  </div>
                </li>
              ))}
            </ul>
          </Panel>

          {health.dataCatalog ? (
            <Panel
              title="Data node catalog"
              subtitle={`${health.dataCatalog.totalDataNodes} governed data nodes across source, dataset, indicator, license, release, field, and series classes.`}
            >
              <div className="driver-grid">
                <div className="table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>{t("Data node type")}</th>
                        <th>{t("Count")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {health.dataCatalog.byType.map((row) => (
                        <tr key={row.entityType}>
                          <td>{row.entityType}</td>
                          <td>{formatCompactNumber(row.count)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>{t("Source")}</th>
                        <th>{t("Data nodes")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {health.dataCatalog.bySource.map((row) => (
                        <tr key={row.sourceId}>
                          <td>{row.sourceId}</td>
                          <td>{formatCompactNumber(row.count)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              <ul className="health-list" style={{ marginTop: 16 }}>
                {health.dataCatalog.licensePolicies.slice(0, 6).map((license) => (
                  <li className="data-row" key={license.id}>
                    <div className="row-top">
                      <div>
                        <span className="row-title">{license.name}</span>
                        <span className="row-subtitle">{license.sourceIds.join(" / ")}</span>
                      </div>
                      <StatusPill status={health.dataCatalog?.promoted ? "operational" : "degraded"} />
                    </div>
                    <div className="row-meta">
                      <span>{license.licenseUrl || "license URL unavailable"}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </Panel>
          ) : null}

          <Panel
            title="Entity resolution"
            subtitle={`${health.entityResolution.totalEntities} silver entities; ${formatPercent(health.entityResolution.averageConfidence)} average confidence.`}
          >
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>{t("Entity type")}</th>
                    <th>{t("Count")}</th>
                    <th>{t("Source")}</th>
                    <th>{t("Entities")}</th>
                  </tr>
                </thead>
                <tbody>
                  {health.entityResolution.byEntityType.map((row, index) => {
                    const sourceRow = health.entityResolution.bySource[index];
                    return (
                      <tr key={row.entityType}>
                        <td>{row.entityType}</td>
                        <td>{formatCompactNumber(row.count)}</td>
                        <td>{sourceRow?.sourceId ?? "n/a"}</td>
                        <td>{formatCompactNumber(sourceRow?.entityCount ?? 0)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Panel>

          <Panel
            title="Evidence lineage"
            subtitle={`${health.evidenceLineage.manifestRef}; raw to silver to gold audit chain.`}
            translateSubtitle={false}
          >
            <div className="inspector-grid" style={{ marginBottom: 16 }}>
              <Field label="Raw records" value={health.evidenceLineage.rawRecordCount} />
              <Field label="Silver events" value={health.evidenceLineage.silverEventCount} />
              <Field label="Gold edges" value={health.evidenceLineage.goldEdgeEventCount} />
              <Field label="Checksum" value={health.evidenceLineage.checksum.slice(0, 12)} />
            </div>
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>{t("Source")}</th>
                    <th>{t("Raw record")}</th>
                    <th>{t("Silver events")}</th>
                    <th>{t("Gold edges")}</th>
                    <th>{t("Targets")}</th>
                    <th>{t("Confidence")}</th>
                  </tr>
                </thead>
                <tbody>
                  {health.evidenceLineage.records.slice(0, 8).map((record) => (
                    <tr key={record.id}>
                      <td>{record.sourceName}</td>
                      <td>{record.sourceRecordId}</td>
                      <td>{record.silverEventIds.length}</td>
                      <td>{record.goldEdgeEventIds.length}</td>
                      <td>{record.targetEntities.slice(0, 3).join(" / ")}</td>
                      <td>{formatPercent(record.confidence)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>

          <Panel
            title="Runtime log"
            subtitle="Recent platform events."
            action={<IconButton icon={TerminalSquare} label="Open terminal log" />}
          >
            <pre className="terminal-log">
              {health.logs.map((line) => (
                <code key={line}>{line}</code>
              ))}
            </pre>
          </Panel>
        </div>
      </div>
    </div>
  );
}
