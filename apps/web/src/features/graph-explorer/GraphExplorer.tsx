import { useEffect, useMemo, useState } from "react";
import type { SupplyRiskApiClient, SupplyRiskDashboardData } from "@supply-risk/api-client";
import type {
  ApiResult,
  GraphEvidenceData,
  GraphExplorerData,
  GraphGeoData,
  GraphLink,
  GraphMatrixData,
  GraphNode,
  GraphNodeKind,
  GraphScenarioOverlayData,
  GraphTimelineData,
} from "@supply-risk/shared-types";
import { Panel } from "../../app/components";
import { useI18n } from "../../app/i18n";
import { GraphBreadcrumbs } from "./GraphBreadcrumbs";
import { GraphCanvas } from "./GraphCanvas";
import { GraphControls } from "./GraphControls";
import { GraphEmptyState } from "./GraphEmptyState";
import { GraphInspector } from "./GraphInspector";
import { GraphLayers } from "./GraphLayers";
import { GraphLegend } from "./GraphLegend";
import { defaultGraphLayerSet, findFirstGraphSearchMatch, type GraphLayerCategory } from "./graphFilters";
import {
  buildGraphViewModel,
  criticalGraphNodes,
  graphModeLabel,
  graphViewModeUsesPath,
  normalizeGraphViewMode,
  type GraphFocusDirection,
  type GraphViewModel,
  type GraphVersionMetadata,
  type GraphViewMode,
  type LegacyGraphExplorerMode,
} from "./graphViewModel";

export function GraphExplorer({
  apiClient,
  data,
  initialMode = "overview",
}: {
  apiClient?: SupplyRiskApiClient;
  data: SupplyRiskDashboardData;
  initialMode?: LegacyGraphExplorerMode;
}) {
  const { t } = useI18n();
  const graph = data.graphExplorer;
  const [mode, setMode] = useState<GraphViewMode>(() => normalizeGraphViewMode(initialMode));
  const [nodeKind, setNodeKind] = useState<GraphNodeKind | "all">("all");
  const [query, setQuery] = useState("");
  const [selectedNodeId, setSelectedNodeId] = useState(graph.selectedNodeId);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [selectedPathId, setSelectedPathId] = useState(graph.transmissionPaths?.[0]?.id ?? data.pathExplainer.selectedPathId);
  const [selectedPathStepIndex, setSelectedPathStepIndex] = useState(0);
  const [selectedCountryCode, setSelectedCountryCode] = useState(
    graph.countryLens?.selectedCountryCode ?? graph.availableCountries?.[0]?.code ?? "US",
  );
  const [enabledLayers, setEnabledLayers] = useState<Set<GraphLayerCategory>>(() => new Set(defaultGraphLayerSet));
  const [sourceFilter, setSourceFilter] = useState("all");
  const [countryFilter, setCountryFilter] = useState("all");
  const [productFilter, setProductFilter] = useState("all");
  const [confidenceMin, setConfidenceMin] = useState(0);
  const [evidenceOnly, setEvidenceOnly] = useState(false);
  const [endpointDetails, setEndpointDetails] = useState<GraphEndpointDetails>({
    source: "fallback",
    status: "fallback",
    message: "Fallback graph payload: dashboard graph used until a backend graph view endpoint responds.",
  });
  const [hideLowConfidence, setHideLowConfidence] = useState(false);
  const [showEdgeLabels, setShowEdgeLabels] = useState(false);
  const [focusDepth, setFocusDepth] = useState(1);
  const [focusDirection, setFocusDirection] = useState<GraphFocusDirection>("both");
  const [pinnedNodeIds, setPinnedNodeIds] = useState<Set<string>>(() => new Set());
  const metadata = useMemo(() => graphMetadata(data), [data]);
  const countries = graph.availableCountries ?? graph.countryLens?.countries ?? [];
  const criticalNodes = useMemo(() => criticalGraphNodes(graph), [graph]);
  const sourceOptions = useMemo(() => graphSourceOptions(graph), [graph]);
  const productOptions = useMemo(() => graphProductOptions(graph), [graph]);

  useEffect(() => {
    const nextMode = normalizeGraphViewMode(initialMode);
    setMode(nextMode);
    setSelectedEdgeId(null);
  }, [initialMode]);

  useEffect(() => {
    const match = findFirstGraphSearchMatch(graph.nodes, query, nodeKind);
    if (!query.trim() || !match) return;
    if (selectedNodeId !== match.id) setSelectedNodeId(match.id);
    setMode((current) => (current === "overview" || current === "geo" || current === "scenario" ? "focus" : current));
    setFocusDepth(1);
    setFocusDirection("both");
  }, [graph.nodes, nodeKind, query, selectedNodeId]);

  useEffect(() => {
    setSelectedPathStepIndex(0);
  }, [selectedPathId]);

  useEffect(() => {
    let cancelled = false;
    if (!apiClient) {
      setEndpointDetails({
        source: "fallback",
        status: "fallback",
        message: "Fallback graph payload: dashboard graph used until a backend graph view endpoint responds.",
      });
      return;
    }

    const loadEndpointDetails = async () => {
      setEndpointDetails((current) => ({
        ...current,
        status: "loading",
        message: "Backend graph view endpoint loading.",
      }));
      try {
        const result = await fetchGraphEndpointDetails(apiClient, {
          mode,
          selectedNodeId: selectedNodeId ?? graph.selectedNodeId,
          focusDepth,
          selectedPath: graph.transmissionPaths?.find((path) => path.id === selectedPathId) ?? graph.transmissionPaths?.[0],
        });
        if (cancelled) return;
        setEndpointDetails(result);
      } catch (error) {
        if (cancelled) return;
        setEndpointDetails({
          source: "fallback",
          status: "fallback",
          message: error instanceof Error ? error.message : "Fallback graph payload: backend graph view endpoint unavailable.",
        });
      }
    };

    void loadEndpointDetails();
    return () => {
      cancelled = true;
    };
  }, [apiClient, focusDepth, graph.selectedNodeId, graph.transmissionPaths, mode, selectedNodeId, selectedPathId]);

  const view = useMemo(
    () =>
      buildGraphViewModel({
        graph,
        mode,
        selectedNodeId,
        selectedEdgeId,
        selectedPathId,
        selectedPathStepIndex,
        selectedCountryCode,
        searchQuery: query,
        nodeKind,
        enabledLayers,
        confidenceMin,
        countryFilter,
        evidenceOnly,
        hideLowConfidence,
        productFilter,
        sourceFilter,
        pinnedNodeIds,
        focusDepth,
        focusDirection,
      }),
    [
      enabledLayers,
      focusDepth,
      focusDirection,
      graph,
      confidenceMin,
      countryFilter,
      evidenceOnly,
      hideLowConfidence,
      mode,
      nodeKind,
      pinnedNodeIds,
      productFilter,
      query,
      selectedCountryCode,
      selectedEdgeId,
      selectedNodeId,
      selectedPathId,
      selectedPathStepIndex,
      sourceFilter,
    ],
  );
  const selectedPathStepEdgeId =
    view.selectedPathStep?.edgeId ??
    (view.activePath && selectedPathStepIndex > 0 ? view.activePath.edgeSequence[selectedPathStepIndex - 1] : undefined);

  const toggleLayer = (layer: GraphLayerCategory) => {
    setEnabledLayers((current) => {
      const next = new Set(current);
      if (next.has(layer)) next.delete(layer);
      else next.add(layer);
      return next;
    });
  };

  const pinSelectedNode = () => {
    const nodeId = view.selectedNode?.id;
    if (!nodeId) return;
    setPinnedNodeIds((current) => {
      const next = new Set(current);
      if (next.has(nodeId)) next.delete(nodeId);
      else next.add(nodeId);
      return next;
    });
  };

  const changeMode = (nextMode: GraphViewMode) => {
    setMode(nextMode);
    setSelectedEdgeId(null);
    if (nextMode === "focus") {
      setFocusDepth(1);
      setFocusDirection("both");
    }
  };

  const resetView = () => {
    setMode("overview");
    setSelectedEdgeId(null);
    setSelectedNodeId(graph.selectedNodeId);
    setSelectedPathId(graph.transmissionPaths?.[0]?.id ?? data.pathExplainer.selectedPathId);
    setSelectedPathStepIndex(0);
    setSourceFilter("all");
    setCountryFilter("all");
    setProductFilter("all");
    setConfidenceMin(0);
    setEvidenceOnly(false);
    setHideLowConfidence(false);
    setShowEdgeLabels(false);
    setFocusDepth(1);
    setFocusDirection("both");
    setPinnedNodeIds(new Set());
    setEnabledLayers(new Set(defaultGraphLayerSet));
  };

  const exportViewSummary = () => {
    if (typeof document === "undefined") return;
    const summary = {
      export_type: "graph_view_summary",
      exported_at: new Date().toISOString(),
      mode,
      graph_version: metadata.graphVersion,
      source_manifest_id: metadata.sourceManifestId,
      warnings: metadata.warnings,
      data_scope: "sanitized_visible_graph_only",
      filters: {
        nodeKind,
        sourceFilter,
        countryFilter,
        productFilter,
        confidenceMin,
        evidenceOnly,
        hideLowConfidence,
        enabledLayers: Array.from(enabledLayers),
      },
      nodes: view.visibleNodes.map((node) => ({
        id: node.id,
        label: node.label,
        kind: node.kind,
        countryCode: node.countryCode,
        score: node.score,
      })),
      links: view.visibleLinks.map((link) => ({
        id: link.id,
        source: link.source,
        target: link.target,
        label: link.label,
        edgeType: link.edgeType,
        edgeRole: link.edgeRole,
        sourceId: link.sourceId,
        derived_context: link.metadata?.derived_context === true,
        not_supply_chain_dependency: link.metadata?.not_supply_chain_dependency === true,
      })),
    };
    const blob = new Blob([JSON.stringify(summary, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `graph-view-summary-${mode}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="graph-workbench graph-workbench-v2 graph-workbench-v3">
      <Panel title="Graph scope" subtitle="Graph Explorer v2 / v3 layered views." className="graph-side-panel">
        <div className="graph-version-strip">
          <strong>Graph Explorer v2 / v3</strong>
          <span>{graphModeLabel(mode)}</span>
        </div>
        <GraphControls
          confidenceMin={confidenceMin}
          countries={countries}
          countryFilter={countryFilter}
          criticalNodes={criticalNodes}
          evidenceOnly={evidenceOnly}
          filters={graph.filters}
          focusDepth={focusDepth}
          focusDirection={focusDirection}
          mode={mode}
          nodeKind={nodeKind}
          onConfidenceMinChange={setConfidenceMin}
          onCountryFilterChange={setCountryFilter}
          onCountrySelect={(countryCode) => {
            setSelectedCountryCode(countryCode);
            setCountryFilter(countryCode);
            setSelectedEdgeId(null);
            setMode("geo");
          }}
          onCriticalNodeSelect={(nodeId) => {
            setSelectedNodeId(nodeId);
            setSelectedEdgeId(null);
            setMode("focus");
            setFocusDepth(1);
            setFocusDirection("both");
          }}
          onEvidenceOnlyChange={setEvidenceOnly}
          onExportView={exportViewSummary}
          onFocusChange={(direction, depth) => {
            setFocusDirection(direction);
            setFocusDepth(depth);
            setMode("focus");
          }}
          onModeChange={changeMode}
          onNodeKindChange={setNodeKind}
          onPathSelect={(pathId) => {
            setSelectedPathId(pathId);
            setSelectedEdgeId(null);
            setMode("path");
          }}
          onPinSelected={pinSelectedNode}
          onProductFilterChange={setProductFilter}
          onResetView={resetView}
          onSearchChange={setQuery}
          onSourceFilterChange={setSourceFilter}
          paths={graph.transmissionPaths ?? []}
          productFilter={productFilter}
          productOptions={productOptions}
          query={query}
          renderCounts={{
            edgeLimit: view.renderLimits.edgeLimit,
            nodeLimit: view.renderLimits.nodeLimit,
            totalEligibleEdges: view.totalEligibleEdges,
            totalEligibleNodes: view.totalEligibleNodes,
            visibleLinks: view.visibleLinks.length,
            visibleNodes: view.visibleNodes.length,
          }}
          selectedCountryCode={view.selectedCountry?.code}
          selectedNodeId={view.selectedNode?.id}
          selectedPathId={view.activePath?.id}
          sourceFilter={sourceFilter}
          sourceOptions={sourceOptions}
        />
        <GraphLayers
          enabledLayers={enabledLayers}
          hideLowConfidence={hideLowConfidence}
          onLayerToggle={toggleLayer}
          onToggleHideLowConfidence={() => setHideLowConfidence((current) => !current)}
          onToggleShowEdgeLabels={() => setShowEdgeLabels((current) => !current)}
          showEdgeLabels={showEdgeLabels}
        />
        <GraphLegend metadata={metadata} />
      </Panel>

      <Panel
        title="Entity network"
        subtitle={`${graphModeLabel(mode)} view; ${view.visibleNodes.length} nodes and ${view.visibleLinks.length} edges rendered.`}
        className="graph-main-panel"
        translateSubtitle={false}
      >
        <GraphBreadcrumbs mode={mode} selectedEdge={view.selectedEdge} selectedNode={view.selectedNode} />
        <div className="graph-view-summary">
          <span>initial cap: 20 nodes / 35 edges</span>
          <span>focus cap: 25 nodes / 40 edges</span>
          <span>edge labels hidden by default</span>
        </div>
        <EndpointStatusPanel details={endpointDetails} />
        <div className="graph-canvas">
          {mode === "matrix" ? (
            <GraphMatrixPanel graph={graph} view={view} endpointDetails={endpointDetails} />
          ) : mode === "evidence" ? (
            <GraphEvidencePanel view={view} endpointDetails={endpointDetails} />
          ) : view.visibleNodes.length > 0 ? (
            <GraphCanvas
              activePathEdgeIds={view.activePathEdgeIds}
              activePathNodeIds={view.activePathNodeIds}
              activePathNodeIndex={view.activePathNodeIndex}
              links={view.visibleLinks}
              matchedNodeIds={view.matchedNodeIds}
              mode={mode}
              nodes={view.visibleNodes}
              onSelectEdge={(edgeId) => {
                setSelectedEdgeId(edgeId);
              }}
              onSelectNode={(nodeId) => {
                setSelectedNodeId(nodeId);
                setSelectedEdgeId(null);
                if (mode === "overview") setMode("focus");
              }}
              pinnedNodeIds={pinnedNodeIds}
              selectedEdgeId={selectedEdgeId}
              selectedNodeId={view.selectedNode?.id}
              selectedPathStepEdgeId={selectedPathStepEdgeId}
              selectedPathStepNodeId={view.selectedPathStep?.nodeId}
              showEdgeLabels={showEdgeLabels}
            />
          ) : (
            <GraphEmptyState message={view.emptyReason ?? "No entities match the active graph filters."} />
          )}
        </div>
        <GraphModeDetailPanel
          endpointDetails={endpointDetails}
          graph={graph}
          metadata={metadata}
          mode={mode}
          view={view}
        />
      </Panel>

      <Panel title="Inspector" subtitle="Evidence, selection, and fixture limits." className="graph-inspector-panel">
        {view.emptyReason && mode === "scenario" ? <p className="inspector-note">{t(view.emptyReason)}</p> : null}
        <GraphInspector
          activePath={graphViewModeUsesPath(mode) ? view.activePath : undefined}
          countryLens={graph.countryLens}
          edge={view.selectedEdge}
          node={view.selectedEdge ? undefined : view.selectedNode}
          onSelectPathStep={(index, nodeId) => {
            setSelectedPathStepIndex(index);
            setSelectedNodeId(nodeId);
            setSelectedEdgeId(null);
          }}
          selectedCountry={mode === "geo" ? view.selectedCountry : undefined}
          selectedPath={graphViewModeUsesPath(mode)}
          selectedPathStepIndex={selectedPathStepIndex}
        />
      </Panel>
    </div>
  );
}

type GraphEndpointDetails = {
  data?: GraphTimelineData | GraphGeoData | GraphMatrixData | GraphEvidenceData | GraphScenarioOverlayData | Record<string, unknown>;
  message: string;
  source: "backend" | "fallback";
  status: "active" | "fallback" | "loading";
};

async function fetchGraphEndpointDetails(
  apiClient: SupplyRiskApiClient,
  options: {
    mode: GraphViewMode;
    selectedNodeId?: string;
    focusDepth: number;
    selectedPath?: { sourceId: string; targetId: string };
  },
): Promise<GraphEndpointDetails> {
  let result: ApiResult<unknown>;
  if (options.mode === "overview") {
    result = await apiClient.getGraphView({ mode: "overview" });
  } else if (options.mode === "focus") {
    result = await apiClient.getGraphFocus({
      nodeId: options.selectedNodeId ?? "company:tsmc",
      depth: options.focusDepth,
    });
  } else if (options.mode === "path") {
    result = await apiClient.getGraphPathView({
      sourceNodeId: options.selectedPath?.sourceId ?? "company:tsmc",
      targetNodeId: options.selectedPath?.targetId ?? "product_grade:advanced_logic",
    });
  } else if (options.mode === "timeline") {
    result = await apiClient.getGraphTimeline({ limit: 50 });
  } else if (options.mode === "geo") {
    result = await apiClient.getGraphGeo({ limit: 50 });
  } else if (options.mode === "matrix") {
    result = await apiClient.getGraphMatrix({ limit: 30 });
  } else if (options.mode === "evidence") {
    result = await apiClient.getGraphEvidence({ limit: 50 });
  } else {
    result = await apiClient.getGraphScenarioOverlay({ runId: null });
  }

  if (result.data && result.envelope.status !== "error") {
    return {
      data: result.data as GraphEndpointDetails["data"],
      message: "Backend graph view endpoint active.",
      source: "backend",
      status: "active",
    };
  }
  return {
    message: result.envelope.warnings?.[0] ?? "Fallback graph payload: backend graph view endpoint unavailable.",
    source: "fallback",
    status: "fallback",
  };
}

function EndpointStatusPanel({ details }: { details: GraphEndpointDetails }) {
  return (
    <div className={`graph-endpoint-status is-${details.status}`}>
      <strong>{details.source === "backend" ? "Backend graph view endpoint" : "Fallback graph payload"}</strong>
      <span>{details.message}</span>
    </div>
  );
}

function GraphModeDetailPanel({
  endpointDetails,
  graph,
  metadata,
  mode,
  view,
}: {
  endpointDetails: GraphEndpointDetails;
  graph: GraphExplorerData;
  metadata: GraphVersionMetadata;
  mode: GraphViewMode;
  view: GraphViewModel;
}) {
  if (mode === "overview") return <GraphOverviewPanel graph={graph} metadata={metadata} view={view} />;
  if (mode === "timeline") return <GraphTimelinePanel graph={graph} endpointDetails={endpointDetails} view={view} />;
  if (mode === "geo") return <GraphGeoPanel endpointDetails={endpointDetails} graph={graph} view={view} />;
  if (mode === "scenario") return <GraphScenarioPanel endpointDetails={endpointDetails} view={view} />;
  if (mode === "path") return <GraphPathEvidencePanel view={view} />;
  if (mode === "focus") return <GraphFocusPanel view={view} />;
  return null;
}

function GraphOverviewPanel({
  graph,
  metadata,
  view,
}: {
  graph: GraphExplorerData;
  metadata: GraphVersionMetadata;
  view: GraphViewModel;
}) {
  const sourceRows = graph.graphStats?.bySource ?? [];
  return (
    <div className="graph-v3-panel graph-v3-overview-panel">
      <div className="section-kicker">Overview mode source coverage summary</div>
      <div className="inspector-grid">
        <span>Visible nodes: {view.visibleNodes.length} / 20</span>
        <span>Visible links: {view.visibleLinks.length} / 35</span>
        <span>graph_version: {metadata.graphVersion}</span>
        <span>source_manifest_id: {metadata.sourceManifestId}</span>
      </div>
      <ul className="evidence-list compact">
        {sourceRows.slice(0, 6).map((row) => (
          <li key={row.source ?? row.kind ?? "source"}>
            {row.source ?? row.kind ?? "source"}: {row.count}
          </li>
        ))}
        {sourceRows.length === 0 ? <li>Source coverage is provided by the fixture/proxy dashboard graph.</li> : null}
      </ul>
    </div>
  );
}

function GraphFocusPanel({ view }: { view: GraphViewModel }) {
  return (
    <div className="graph-v3-panel graph-v3-focus-panel">
      <div className="section-kicker">Focus mode</div>
      <p className="inspector-note">
        Focus keeps one selected node visually dominant, with explicit upstream, downstream, two-hop, pin, and low-confidence controls.
      </p>
      <ul className="evidence-list compact">
        {view.visibleNodes.slice(0, 5).map((node) => (
          <li key={node.id}>{node.label} / {node.kind} / {node.countryCode ?? "global"}</li>
        ))}
      </ul>
    </div>
  );
}

function GraphPathEvidencePanel({ view }: { view: GraphViewModel }) {
  return (
    <div className="graph-v3-panel graph-v3-path-panel">
      <div className="section-kicker">Path mode evidence trail</div>
      <ol className="graph-step-table">
        {(view.activePath?.steps ?? []).map((step, index) => (
          <li key={step.id}>
            <strong>{index + 1}. {step.label}</strong>
            <span>{step.edgeType ?? "source"} / {step.evidence}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

function GraphTimelinePanel({
  endpointDetails,
  graph,
  view,
}: {
  endpointDetails: GraphEndpointDetails;
  graph: GraphExplorerData;
  view: GraphViewModel;
}) {
  const endpointEvents = Array.isArray((endpointDetails.data as GraphTimelineData | undefined)?.events)
    ? ((endpointDetails.data as GraphTimelineData).events ?? [])
    : [];
  const pathSteps = view.activePath?.steps ?? graph.transmissionPaths?.[0]?.steps ?? [];
  return (
    <div className="graph-v3-panel graph-v3-timeline-panel">
      <div className="section-kicker">Timeline mode</div>
      <p className="inspector-note">Event timeline shows event nodes and affected graph nodes over hop order; it does not render the full graph.</p>
      <ul className="timeline-list compact">
        {endpointEvents.slice(0, 6).map((event, index) => (
          <li key={String(event.id ?? index)}>{String(event.label ?? event.event_type ?? event.id ?? "event")} / hop {String(event.hop_order ?? index)}</li>
        ))}
        {endpointEvents.length === 0
          ? pathSteps.slice(0, 6).map((step, index) => (
              <li key={step.id}>{step.label} / hop {index} / {step.evidence}</li>
            ))
          : null}
      </ul>
    </div>
  );
}

function GraphGeoPanel({
  endpointDetails,
  graph,
  view,
}: {
  endpointDetails: GraphEndpointDetails;
  graph: GraphExplorerData;
  view: GraphViewModel;
}) {
  const countries = Array.isArray((endpointDetails.data as GraphGeoData | undefined)?.countries)
    ? ((endpointDetails.data as GraphGeoData).countries ?? [])
    : graph.availableCountries ?? graph.countryLens?.countries ?? [];
  return (
    <div className="graph-v3-panel graph-v3-geo-panel">
      <div className="section-kicker">Geo mode</div>
      <p className="inspector-note">Geo aggregates countries, regions, trade/dependency links, logistics context, and hazard exposure overlays.</p>
      <div className="inspector-grid">
        <span>Rendered geo nodes: {view.visibleNodes.length}</span>
        <span>Rendered geo links: {view.visibleLinks.length}</span>
      </div>
      <ul className="evidence-list compact">
        {countries.slice(0, 6).map((country, index) => (
          <li key={String((country as Record<string, unknown>).code ?? (country as Record<string, unknown>).id ?? index)}>
            {String((country as Record<string, unknown>).label ?? (country as Record<string, unknown>).countryName ?? (country as Record<string, unknown>).code ?? "country")}
          </li>
        ))}
      </ul>
    </div>
  );
}

function GraphScenarioPanel({
  endpointDetails,
  view,
}: {
  endpointDetails: GraphEndpointDetails;
  view: GraphViewModel;
}) {
  const overlay = endpointDetails.data as GraphScenarioOverlayData | undefined;
  const affectedNodes = Array.isArray(overlay?.affected_nodes) ? overlay.affected_nodes : [];
  return (
    <div className="graph-v3-panel graph-v3-scenario-panel">
      <div className="section-kicker">Scenario overlay mode</div>
      <p className="inspector-note">Scenario overlay renders only a selected run. It never displays all runs by default.</p>
      <div className="inspector-grid">
        <span>run_id: {overlay?.run_id ?? "none_selected"}</span>
        <span>affected nodes: {affectedNodes.length || view.visibleNodes.length}</span>
      </div>
    </div>
  );
}

function GraphMatrixPanel({
  endpointDetails,
  graph,
  view,
}: {
  endpointDetails: GraphEndpointDetails;
  graph: GraphExplorerData;
  view: GraphViewModel;
}) {
  const matrixRows = Array.isArray((endpointDetails.data as GraphMatrixData | undefined)?.dependency_matrix)
    ? ((endpointDetails.data as GraphMatrixData).dependency_matrix ?? [])
    : view.visibleLinks.slice(0, 12).map((link) => ({
        source: graph.nodes.find((node) => node.id === link.source)?.label ?? link.source,
        target: graph.nodes.find((node) => node.id === link.target)?.label ?? link.target,
        value: link.transmissionWeight ?? link.weight,
        edge_type: link.edgeType ?? "dependency",
      }));
  return (
    <div className="graph-v3-panel graph-v3-matrix-panel">
      <div className="section-kicker">Matrix mode</div>
      <p className="inspector-note">Matrix mode uses bounded tables and heatmap-style cells instead of a dense node cloud.</p>
      <table className="graph-matrix-table">
        <thead>
          <tr>
            <th>Source</th>
            <th>Target</th>
            <th>Type</th>
            <th>Weight</th>
          </tr>
        </thead>
        <tbody>
          {matrixRows.slice(0, 12).map((row, index) => (
            <tr key={String((row as Record<string, unknown>).id ?? index)}>
              <td>{String((row as Record<string, unknown>).source ?? "")}</td>
              <td>{String((row as Record<string, unknown>).target ?? "")}</td>
              <td>{String((row as Record<string, unknown>).edge_type ?? (row as Record<string, unknown>).layer ?? "")}</td>
              <td>
                <span className="matrix-weight-cell">
                  {Number((row as Record<string, unknown>).value ?? (row as Record<string, unknown>).weight ?? 0).toFixed(2)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function GraphEvidencePanel({
  endpointDetails,
  view,
}: {
  endpointDetails: GraphEndpointDetails;
  view: GraphViewModel;
}) {
  const evidenceRows = Array.isArray((endpointDetails.data as GraphEvidenceData | undefined)?.evidence_refs)
    ? ((endpointDetails.data as GraphEvidenceData).evidence_refs ?? [])
    : evidenceRowsFromLinks(view.visibleLinks);
  return (
    <div className="graph-v3-panel graph-v3-evidence-panel">
      <div className="section-kicker">Evidence mode</div>
      <p className="inspector-warning">This is not a supply-chain dependency edge.</p>
      <p className="inspector-note">Evidence-context link rows are separated from real graph edges and scenario traces.</p>
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Evidence ref</th>
            <th>Edge semantics</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {evidenceRows.slice(0, 12).map((row, index) => (
            <tr key={String((row as Record<string, unknown>).edge_id ?? (row as Record<string, unknown>).id ?? index)}>
              <td>{String((row as Record<string, unknown>).source_id ?? (row as Record<string, unknown>).edge_id ?? "evidence_ref")}</td>
              <td>
                {String((row as Record<string, unknown>).edge_type ?? "evidence-context link")}
                {Boolean((row as Record<string, unknown>).not_supply_chain_dependency) ? " / not supply-chain dependency" : ""}
              </td>
              <td>{Number((row as Record<string, unknown>).confidence ?? 0).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function evidenceRowsFromLinks(links: GraphLink[]) {
  return links.map((link) => ({
    edge_id: link.id,
    edge_type: link.edgeType ?? link.edgeRole ?? "graph_edge",
    source_id: link.sourceId ?? String(link.metadata?.source ?? "source_ref"),
    confidence: link.confidence ?? 0,
    not_supply_chain_dependency: link.metadata?.not_supply_chain_dependency === true,
  }));
}

function graphSourceOptions(graph: GraphExplorerData) {
  const sources = new Set<string>();
  for (const node of graph.nodes) {
    collectOption(sources, node.metadata.source);
    collectOption(sources, node.metadata.source_id);
    collectOption(sources, node.metadata.sourceId);
    collectOption(sources, node.metadata.dataset);
  }
  for (const link of graph.links) {
    collectOption(sources, link.sourceId);
    collectOption(sources, link.metadata?.source);
    collectOption(sources, link.metadata?.source_label);
  }
  return [...sources].sort().slice(0, 40);
}

function graphProductOptions(graph: GraphExplorerData) {
  const products = new Set<string>();
  for (const node of graph.nodes) {
    if (node.kind === "product_grade" || node.kind === "commodity" || node.kind === "component" || node.kind === "raw_material") {
      collectOption(products, node.kind);
    }
    collectOption(products, node.entityType);
    collectOption(products, node.metadata.product_grade);
    collectOption(products, node.metadata.product_category);
    collectOption(products, node.metadata.commodity_code);
    collectOption(products, node.metadata.category);
  }
  return [...products].sort().slice(0, 40);
}

function collectOption(target: Set<string>, value: unknown) {
  if (typeof value !== "string") return;
  const normalized = value.trim();
  if (normalized && normalized.length <= 80) target.add(normalized);
}

function graphMetadata(data: SupplyRiskDashboardData): GraphVersionMetadata {
  const health = data.systemHealthCenter?.semiconductorGraph;
  return {
    graphVersion: health?.graphVersion ?? "fixture_graph:v0.1",
    sourceManifestId: health?.sourceManifestId ?? "fixture_manifest:semirisk:v0.1",
    asOfTime: health?.asOfTime ?? "fixture_as_of_time:unavailable",
    fixtureGraph: health?.fixtureGraph ?? true,
    warnings: Array.from(new Set([...(health?.warnings ?? []), "fixture_graph:not_production_ready"])),
  };
}
