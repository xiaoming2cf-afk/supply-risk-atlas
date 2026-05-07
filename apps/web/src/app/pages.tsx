import { useEffect, useMemo, useState, type ChangeEvent } from "react";
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
  Filter,
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
  DashboardPageId,
  EvidenceItem,
  ExplainedPath,
  GraphLink,
  GraphNode,
  GraphNodeKind,
  GraphVersion,
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
      return <GraphExplorer data={props.data} />;
    case "company-risk-360":
      return <CompanyRisk360 data={props.data} />;
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

function GraphExplorer({ data }: { data: SupplyRiskDashboardData }) {
  const { t } = useI18n();
  const graph = data.graphExplorer;
  const [kind, setKind] = useState<GraphNodeKind | "all">("all");
  const [query, setQuery] = useState("");
  const [selectedNodeId, setSelectedNodeId] = useState(graph.selectedNodeId);
  const normalizedQuery = query.trim().toLowerCase();

  const visibleNodes = useMemo(
    () =>
      graph.nodes.filter((node) => {
        const kindMatches = kind === "all" || node.kind === kind;
        if (!kindMatches) return false;
        if (!normalizedQuery) return true;
        const metadataValues = Object.values(node.metadata).map((value) => String(value).toLowerCase());
        return [node.id, node.label, node.kind, ...metadataValues].some((value) =>
          value.toLowerCase().includes(normalizedQuery),
        );
      }),
    [graph.nodes, kind, normalizedQuery]
  );
  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map((node) => node.id)), [visibleNodes]);
  const visibleLinks = graph.links.filter((link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target));
  const selectedNode =
    visibleNodes.find((node) => node.id === selectedNodeId) ??
    visibleNodes[0] ??
    graph.nodes.find((node) => node.id === selectedNodeId) ??
    graph.nodes[0];
  const graphStats = graph.graphStats;

  return (
    <div className="page-grid split-layout">
      <Panel title="Graph filters" subtitle="Scope the visible network without losing node context.">
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
        <div style={{ marginTop: 16 }} className="inspector-grid">
          <Field label="Visible nodes" value={visibleNodes.length} />
          <Field label="Visible links" value={visibleLinks.length} />
          <Field label="Total nodes" value={formatCompactNumber(graphStats?.totalNodes ?? graph.nodes.length)} />
          <Field label="Total links" value={formatCompactNumber(graphStats?.totalLinks ?? graph.links.length)} />
          <Field label="Data nodes" value={graph.dataSummary?.totalDataNodes ?? 0} />
          <Field label="High-risk edges" value={formatCompactNumber(graphStats?.highRiskLinks ?? 0)} />
          <Field label="Focus score" value={`${selectedNode.score}/100`} />
          <Field label="Focus type" value={selectedNode.kind} />
        </div>
        <label className="form-control" style={{ marginTop: 16 }}>
          <span>{t("Entity search")}</span>
          <input
            aria-label={t("Entity search")}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={t("Search name, source, country, or external id")}
            type="search"
            value={query}
          />
        </label>
      </Panel>

      <Panel
        title="Entity network"
        subtitle="Click a node to inspect metadata and high-risk adjacency."
        action={<Button icon={Filter}>Save view</Button>}
      >
        <div className="graph-canvas">
          <GraphNetwork
            links={visibleLinks}
            nodes={visibleNodes}
            onSelectNode={setSelectedNodeId}
            selectedNodeId={selectedNode.id}
          />
          {visibleNodes.length === 0 ? <div className="empty-state">{t("No entities match the current filters.")}</div> : null}
        </div>
      </Panel>

      <Panel title="Node inspector" subtitle="Live metadata attached to the selected graph node.">
        <div className="inspector-grid">
          <Field label="Name" value={selectedNode.label} />
          <Field label="Risk level" value={<RiskPill level={selectedNode.level} />} />
          <Field label="Score" value={`${selectedNode.score}/100`} />
          <Field label="Kind" value={selectedNode.kind} />
          {Object.entries(selectedNode.metadata).map(([label, value]) => (
            <Field key={label} label={label} value={String(value)} />
          ))}
        </div>
      </Panel>
    </div>
  );
}

type RiskFlowNodeData = {
  graphNode: GraphNode;
  selected: boolean;
};

type RiskFlowNode = FlowNode<RiskFlowNodeData, "risk">;
type RiskFlowEdge = FlowEdge<{ level: RiskLevel; label: string }>;

const graphKindLanes: GraphNodeKind[] = ["supplier", "company", "facility", "route", "commodity", "country", "data"];

const graphColorByLevel: Record<RiskLevel, string> = {
  low: "#52d7d0",
  guarded: "#9fb2a9",
  elevated: "#f2b84b",
  severe: "#ff7a4d",
  critical: "#ff4d6d"
};

const graphNodeTypes = { risk: RiskFlowNodeCard };

function GraphNetwork({
  links,
  nodes,
  onSelectNode,
  selectedNodeId
}: {
  links: GraphLink[];
  nodes: GraphNode[];
  onSelectNode: (nodeId: string) => void;
  selectedNodeId: string;
}) {
  const flowNodes = useMemo<RiskFlowNode[]>(
    () => layoutGraphNodes(nodes, selectedNodeId),
    [nodes, selectedNodeId]
  );
  const flowEdges = useMemo<RiskFlowEdge[]>(
    () => layoutGraphEdges(links, new Set(nodes.map((node) => node.id)), selectedNodeId),
    [links, nodes, selectedNodeId]
  );

  return (
    <ReactFlow
      className="risk-flow"
      colorMode="dark"
      defaultEdgeOptions={{ type: "smoothstep" }}
      edges={flowEdges}
      fitView
      fitViewOptions={{ padding: 0.18, maxZoom: 1.1 }}
      maxZoom={1.65}
      minZoom={0.24}
      nodeTypes={graphNodeTypes}
      nodes={flowNodes}
      nodesDraggable={false}
      onNodeClick={(_, node) => onSelectNode(node.id)}
      proOptions={{ hideAttribution: true }}
    >
      <Background color="rgba(238,247,242,0.12)" gap={28} size={1} />
      <MiniMap
        className="risk-flow-minimap"
        nodeColor={(node) => graphColorByLevel[(node.data as RiskFlowNodeData).graphNode.level]}
        pannable
        zoomable
      />
      <Controls className="risk-flow-controls" fitViewOptions={{ padding: 0.18 }} />
    </ReactFlow>
  );
}

function RiskFlowNodeCard({ data }: NodeProps<RiskFlowNode>) {
  const node = data.graphNode;
  return (
    <div className={`risk-flow-node ${riskClassByLevel[node.level]} ${data.selected ? "is-selected" : ""}`}>
      <Handle className="risk-flow-handle" position={Position.Left} type="target" />
      <Handle className="risk-flow-handle" position={Position.Right} type="source" />
      <div className="risk-flow-node-topline">
        <span>{node.kind}</span>
        <strong>{node.score}</strong>
      </div>
      <p>{node.label}</p>
      <small>{String(node.metadata.source ?? node.metadata.country ?? "public source")}</small>
    </div>
  );
}

function layoutGraphNodes(nodes: GraphNode[], selectedNodeId: string): RiskFlowNode[] {
  const grouped = new Map<GraphNodeKind, GraphNode[]>();
  for (const kind of graphKindLanes) {
    grouped.set(kind, []);
  }
  for (const node of nodes) {
    grouped.get(node.kind)?.push(node);
  }
  return graphKindLanes.flatMap((kind, laneIndex) => {
    const laneNodes = [...(grouped.get(kind) ?? [])].sort((a, b) => {
      const riskDelta = riskLevelRank(b.level) - riskLevelRank(a.level);
      return riskDelta || b.score - a.score || a.label.localeCompare(b.label);
    });
    const columnCount = laneNodes.length > 24 ? 3 : laneNodes.length > 10 ? 2 : 1;
    const rowCount = Math.max(1, Math.ceil(laneNodes.length / columnCount));
    const rowGap = 118;
    const columnGap = 238;
    const laneCenter = (laneIndex - (graphKindLanes.length - 1) / 2) * 430;
    return laneNodes.map((node, rowIndex) => ({
      id: node.id,
      type: "risk",
      position: {
        x: laneCenter + ((rowIndex % columnCount) - (columnCount - 1) / 2) * columnGap,
        y: (Math.floor(rowIndex / columnCount) - (rowCount - 1) / 2) * rowGap + (laneIndex % 2 === 0 ? -28 : 28),
      },
      data: { graphNode: node, selected: node.id === selectedNodeId },
      selected: node.id === selectedNodeId,
    }));
  });
}

function layoutGraphEdges(links: GraphLink[], visibleNodeIds: Set<string>, selectedNodeId: string): RiskFlowEdge[] {
  return links
    .filter((link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target))
    .map((link) => {
      const color = graphColorByLevel[link.level];
      const isSelectedAdjacency = link.source === selectedNodeId || link.target === selectedNodeId;
      return {
        id: link.id,
        source: link.source,
        target: link.target,
        type: "smoothstep",
        animated: isSelectedAdjacency || link.level === "critical" || link.level === "severe",
        label: link.level === "critical" || link.level === "severe" ? link.label : undefined,
        data: { level: link.level, label: link.label },
        markerEnd: { type: MarkerType.ArrowClosed, color },
        style: {
          stroke: color,
          strokeOpacity: isSelectedAdjacency ? 0.95 : 0.46,
          strokeWidth: Math.max(1.2, Math.min(4.6, link.weight * 2.8)),
        },
      };
    });
}

function riskLevelRank(level: RiskLevel) {
  return { low: 0, guarded: 1, elevated: 2, severe: 3, critical: 4 }[level];
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
