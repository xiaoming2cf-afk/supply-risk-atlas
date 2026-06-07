import { useEffect, useMemo, useState } from "react";
import type { SupplyRiskApiClient, SupplyRiskDashboardData } from "@supply-risk/api-client";
import type {
  ApiResult,
  GraphEvidenceData,
  GraphExplorerData,
  GraphGeoData,
  GraphMatrixData,
  GraphNodeCatalogData,
  GraphNode,
  GraphNodeKind,
  GraphRelationshipData,
  GraphScenarioOverlayData,
  GraphSourceCoverageData,
  GraphSupplyDemandBalanceData,
  GraphTimelineData,
} from "@supply-risk/shared-types";
import { Panel } from "../../app/components";
import { useI18n } from "../../app/i18n";
import { DiagnosticDetails, MetadataSummary } from "../common/AuditDetails";
import { GraphBreadcrumbs } from "./GraphBreadcrumbs";
import { GraphCanvas } from "./GraphCanvas";
import { GraphControls } from "./GraphControls";
import { GraphEmptyState } from "./GraphEmptyState";
import { GraphEvidenceView } from "./GraphEvidenceView";
import { GraphFocusView } from "./GraphFocusView";
import { GraphGeoView } from "./GraphGeoView";
import { GraphInspector } from "./GraphInspector";
import { GraphLayers } from "./GraphLayers";
import { GraphLegend } from "./GraphLegend";
import { GraphMatrixView } from "./GraphMatrixView";
import { GraphNodeCatalogView } from "./GraphNodeCatalogView";
import { GraphOverviewView } from "./GraphOverviewView";
import { GraphPathView } from "./GraphPathView";
import { GraphScenarioOverlay } from "./GraphScenarioOverlay";
import { GraphSourceCoverageView } from "./GraphSourceCoverageView";
import { GraphTimelineView } from "./GraphTimelineView";
import { DemandRelationshipView } from "./DemandRelationshipView";
import { ProductionDependencyView } from "./ProductionDependencyView";
import { SupplyDemandBalanceView } from "./SupplyDemandBalanceView";
import { SupplyRelationshipView } from "./SupplyRelationshipView";
import {
  ComplianceRiskGraphView,
  DesignIPDependencyGraphView,
  DownstreamDemandGraphView,
  EquipmentProcessDependencyGraphView,
  EventTimelineGraphView,
  FabProcessGraphView,
  LogisticsRouteGraphView,
  MaterialChemicalDependencyGraphView,
  MineralDependencyGraphView,
  PackagingTestingGraphView,
  PolicyMacroGraphView,
  ProductDemandGraphView,
  type RelationshipClassFilter,
  type StageId,
} from "./stage-views";
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

const GRAPH_ENDPOINT_LOADING_TIMEOUT_MS = 15000;
const GRAPH_ENDPOINT_UNAVAILABLE_MESSAGE = "Backend graph data unavailable; authoritative rows are hidden.";
const STAGE_ENDPOINT_UNAVAILABLE_MESSAGE = "Backend stage graph data unavailable; authoritative rows are hidden.";
const GRAPH_DATA_LOADING_MESSAGE = "Loading authoritative graph data.";
const GRAPH_DATA_TIMEOUT_MESSAGE = "Authoritative graph data timed out; rows are hidden.";
const GRAPH_DATA_LOADED_MESSAGE = "Authoritative graph data loaded.";
const STAGE_DATA_LOADING_MESSAGE = "Loading authoritative stage graph data.";
const STAGE_DATA_TIMEOUT_MESSAGE = "Authoritative stage graph data timed out; rows are hidden.";
const STAGE_DATA_LOADED_MESSAGE = "Authoritative stage graph data loaded.";

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
  const [selectedStage, setSelectedStage] = useState<StageId>("L5_fabrication");
  const [relationshipClassFilter, setRelationshipClassFilter] = useState<RelationshipClassFilter>("all");
  const [confidenceMin, setConfidenceMin] = useState(0);
  const [evidenceOnly, setEvidenceOnly] = useState(false);
  const [endpointDetails, setEndpointDetails] = useState<GraphEndpointDetails>({
    mode,
    source: "fallback",
    status: "fallback",
    message: GRAPH_ENDPOINT_UNAVAILABLE_MESSAGE,
  });
  const [relationshipEndpointLoadingExpired, setRelationshipEndpointLoadingExpired] = useState(false);
  const [stageEndpointDetails, setStageEndpointDetails] = useState<GraphEndpointDetails>({
    source: "fallback",
    status: "fallback",
    message: STAGE_ENDPOINT_UNAVAILABLE_MESSAGE,
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
    if (!isRelationshipGraphMode(mode) || endpointDetails.status !== "loading") {
      setRelationshipEndpointLoadingExpired(false);
      return;
    }
    setRelationshipEndpointLoadingExpired(false);
    const timeoutHandle = globalThis.setTimeout(() => {
      setRelationshipEndpointLoadingExpired(true);
    }, GRAPH_ENDPOINT_LOADING_TIMEOUT_MS);
    return () => globalThis.clearTimeout(timeoutHandle);
  }, [endpointDetails.status, mode]);

  useEffect(() => {
    let cancelled = false;
    let timeoutHandle: ReturnType<typeof globalThis.setTimeout> | undefined;
    if (!apiClient) {
      setEndpointDetails({
        mode,
        source: "fallback",
        status: "fallback",
        message: GRAPH_ENDPOINT_UNAVAILABLE_MESSAGE,
      });
      return;
    }

    const loadEndpointDetails = async () => {
      setEndpointDetails({
        mode,
        source: "backend",
        status: "loading",
        message: GRAPH_DATA_LOADING_MESSAGE,
      });
      timeoutHandle = globalThis.setTimeout(() => {
        if (cancelled) return;
        setEndpointDetails({
          mode,
          source: "fallback",
          status: "fallback",
          message: GRAPH_DATA_TIMEOUT_MESSAGE,
          diagnostics: {
            retryHint: "Retry the graph view request. The UI keeps loading bounded and hides non-authoritative rows.",
            transportAttempts: 0,
          },
        });
      }, GRAPH_ENDPOINT_LOADING_TIMEOUT_MS);
      try {
        const result = await fetchGraphEndpointDetails(apiClient, {
          mode,
          selectedNodeId: selectedNodeId ?? graph.selectedNodeId,
          focusDepth,
          selectedPath: graph.transmissionPaths?.find((path) => path.id === selectedPathId) ?? graph.transmissionPaths?.[0],
        });
        if (cancelled) return;
        if (timeoutHandle) globalThis.clearTimeout(timeoutHandle);
        setEndpointDetails(result);
      } catch (error) {
        if (cancelled) return;
        if (timeoutHandle) globalThis.clearTimeout(timeoutHandle);
        setEndpointDetails({
          mode,
          source: "fallback",
          status: "fallback",
          message: GRAPH_ENDPOINT_UNAVAILABLE_MESSAGE,
        });
      }
    };

    void loadEndpointDetails();
    return () => {
      cancelled = true;
      if (timeoutHandle) globalThis.clearTimeout(timeoutHandle);
    };
  }, [apiClient, focusDepth, graph.selectedNodeId, graph.transmissionPaths, mode, selectedNodeId, selectedPathId]);

  useEffect(() => {
    let cancelled = false;
    let timeoutHandle: ReturnType<typeof globalThis.setTimeout> | undefined;
    if (!apiClient) {
      setStageEndpointDetails({
        source: "fallback",
        status: "fallback",
        message: STAGE_ENDPOINT_UNAVAILABLE_MESSAGE,
      });
      return;
    }

    const loadStageEndpoint = async () => {
      setStageEndpointDetails((current) => ({
        ...current,
        status: "loading",
        message: STAGE_DATA_LOADING_MESSAGE,
      }));
      timeoutHandle = globalThis.setTimeout(() => {
        if (cancelled) return;
        setStageEndpointDetails({
          source: "fallback",
          status: "fallback",
          message: STAGE_DATA_TIMEOUT_MESSAGE,
          diagnostics: {
            retryHint: "Retry the stage graph request. The UI keeps loading bounded and hides non-authoritative rows.",
            transportAttempts: 0,
          },
        });
      }, GRAPH_ENDPOINT_LOADING_TIMEOUT_MS);
      const result = await apiClient.getStageGraph({
        stageId: selectedStage,
        relationshipClass: relationshipClassFilter === "all" ? null : relationshipClassFilter,
        limit: 18,
      });
      if (cancelled) return;
      if (timeoutHandle) globalThis.clearTimeout(timeoutHandle);
      if (result.data && result.envelope.status !== "error") {
        setStageEndpointDetails({
          data: result.data,
          message: STAGE_DATA_LOADED_MESSAGE,
          source: "backend",
          status: "active",
        });
      } else {
        setStageEndpointDetails({
          source: "fallback",
          status: "fallback",
          message: STAGE_ENDPOINT_UNAVAILABLE_MESSAGE,
          diagnostics: diagnosticsForEndpointResult(result),
        });
      }
    };

    void loadStageEndpoint().catch((error) => {
      if (cancelled) return;
      if (timeoutHandle) globalThis.clearTimeout(timeoutHandle);
      setStageEndpointDetails({
        source: "fallback",
        status: "fallback",
        message: STAGE_ENDPOINT_UNAVAILABLE_MESSAGE,
      });
    });
    return () => {
      cancelled = true;
      if (timeoutHandle) globalThis.clearTimeout(timeoutHandle);
    };
  }, [apiClient, relationshipClassFilter, selectedStage]);

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
  const displayedEndpointDetails =
    relationshipEndpointLoadingExpired && isRelationshipGraphMode(mode) && endpointDetails.status === "loading"
      ? ({
          ...endpointDetails,
          source: "fallback",
          status: "fallback",
          message: GRAPH_DATA_TIMEOUT_MESSAGE,
          diagnostics: {
            retryHint: "Retry the graph view request. The UI keeps loading bounded and hides non-authoritative rows.",
            transportAttempts: 0,
          },
        } satisfies GraphEndpointDetails)
      : endpointDetails;
  const endpointDataForMode =
    displayedEndpointDetails.mode === mode &&
    displayedEndpointDetails.source === "backend" &&
    displayedEndpointDetails.status === "active"
      ? displayedEndpointDetails.data
      : undefined;
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
    setSelectedStage("L5_fabrication");
    setRelationshipClassFilter("all");
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
    const relationshipSummary = buildRelationshipExportSummary(mode, endpointDataForMode, displayedEndpointDetails, metadata);
    const summary = relationshipSummary ?? {
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
          onRelationshipClassFilterChange={setRelationshipClassFilter}
          onStageChange={setSelectedStage}
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
          selectedStage={selectedStage}
          sourceFilter={sourceFilter}
          sourceOptions={sourceOptions}
          relationshipClassFilter={relationshipClassFilter}
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
        subtitle={`${graphModeLabel(mode)} view; ${view.visibleNodes.length} entities and ${view.visibleLinks.length} relationships shown.`}
        className="graph-main-panel"
        translateSubtitle={false}
      >
        <GraphBreadcrumbs mode={mode} selectedEdge={view.selectedEdge} selectedNode={view.selectedNode} />
        <div className="graph-view-summary">
          <span>overview limit: 20 entities / 35 relationships</span>
          <span>focus limit: 25 entities / 40 relationships</span>
          <span>relationship labels hidden by default</span>
        </div>
        <EndpointStatusPanel details={displayedEndpointDetails} />
        <EndpointStatusPanel details={stageEndpointDetails} />
        <StageModePanel
          endpointDetails={stageEndpointDetails}
          metadata={metadata}
          relationshipClassFilter={relationshipClassFilter}
          selectedStage={selectedStage}
          view={view}
        />
        <div className="graph-canvas">
          {mode === "supply" ? (
            <SupplyRelationshipView view={view} endpointData={endpointDataForMode} />
          ) : mode === "demand" ? (
            <DemandRelationshipView view={view} endpointData={endpointDataForMode} />
          ) : mode === "production-dependency" ? (
            <ProductionDependencyView view={view} endpointData={endpointDataForMode} />
          ) : mode === "supply-demand-balance" ? (
            <SupplyDemandBalanceView view={view} endpointData={endpointDataForMode} />
          ) : mode === "matrix" ? (
            <GraphMatrixView graph={graph} view={view} endpointData={endpointDataForMode} />
          ) : mode === "evidence" ? (
            <GraphEvidenceView view={view} endpointData={endpointDataForMode} />
          ) : mode === "source-coverage" ? (
            <GraphSourceCoverageView view={view} endpointData={endpointDataForMode} />
          ) : mode === "node-catalog" ? (
            <GraphNodeCatalogView view={view} endpointData={endpointDataForMode} />
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
          endpointData={endpointDataForMode}
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

function StageModePanel({
  endpointDetails,
  metadata,
  relationshipClassFilter,
  selectedStage,
  view,
}: {
  endpointDetails: GraphEndpointDetails;
  metadata: GraphVersionMetadata;
  relationshipClassFilter: RelationshipClassFilter;
  selectedStage: StageId;
  view: GraphViewModel;
}) {
  const props = {
    endpointData: endpointDetails.data as Record<string, unknown> | undefined,
    endpointStatus: endpointDetails.status,
    metadata,
    relationshipClassFilter,
    view,
  };
  if (selectedStage === "L0_policy_macro") return <PolicyMacroGraphView {...props} />;
  if (selectedStage === "L1_raw_minerals") return <MineralDependencyGraphView {...props} />;
  if (selectedStage === "L2_materials_chemicals") return <MaterialChemicalDependencyGraphView {...props} />;
  if (selectedStage === "L3_design_eda_ip") return <DesignIPDependencyGraphView {...props} />;
  if (selectedStage === "L4_equipment") return <EquipmentProcessDependencyGraphView {...props} />;
  if (selectedStage === "L5_fabrication") return <FabProcessGraphView {...props} />;
  if (selectedStage === "L6_products") return <ProductDemandGraphView {...props} />;
  if (selectedStage === "L7_packaging_testing") return <PackagingTestingGraphView {...props} />;
  if (selectedStage === "L8_logistics") return <LogisticsRouteGraphView {...props} />;
  if (selectedStage === "L9_downstream_demand") return <DownstreamDemandGraphView {...props} />;
  if (selectedStage === "L10_risk_events") return <EventTimelineGraphView {...props} />;
  return <ComplianceRiskGraphView {...props} />;
}

function buildRelationshipExportSummary(
  mode: GraphViewMode,
  endpointData: GraphEndpointDetails["data"] | undefined,
  endpointDetails: GraphEndpointDetails,
  metadata: GraphVersionMetadata,
) {
  const expectedClassByMode: Partial<Record<GraphViewMode, string>> = {
    supply: "SUPPLY_RELATIONSHIP",
    demand: "DEMAND_RELATIONSHIP",
    "production-dependency": "PRODUCTION_DEPENDENCY",
    "supply-demand-balance": "SUPPLY_DEMAND_BALANCE",
  };
  const expectedClass = expectedClassByMode[mode];
  if (!expectedClass) return undefined;
  const base = {
    export_type: "relationship_view_summary",
    exported_at: new Date().toISOString(),
    mode,
    graph_version: metadata.graphVersion,
    source_manifest_id: metadata.sourceManifestId,
    warnings: metadata.warnings,
    relationship_class: expectedClass,
  };
  if (!isPlainRecord(endpointData) || endpointData.relationship_class !== expectedClass) {
    return {
      ...base,
      data_scope: "unavailable_preview_no_authoritative_relationship_rows",
      preview_state: "unavailable_preview",
      endpoint_status: endpointDetails.status,
      endpoint_source: endpointDetails.source,
      diagnostics: endpointDetails.diagnostics,
      relationships: [],
      balance_rows: [],
      warnings: [...metadata.warnings, "relationship_endpoint_unavailable_or_wrong_class"],
    };
  }
  if (mode === "supply-demand-balance") {
    const balanceRows = Array.isArray(endpointData.balance_rows)
      ? endpointData.balance_rows.filter(
          (row) =>
            isPlainRecord(row) &&
            row.relationship_class === expectedClass &&
            row.row_type === "aggregate" &&
            row.not_supply_chain_dependency === true,
        )
      : [];
    return {
      ...base,
      data_scope: "authoritative_backend_aggregate_rows_only",
      balance_rows: balanceRows,
      relationships: [],
    };
  }
  const relationships = Array.isArray(endpointData.relationships)
    ? endpointData.relationships.filter(
        (row) => isPlainRecord(row) && row.relationship_class === expectedClass,
      )
    : [];
  return {
    ...base,
    data_scope: "authoritative_backend_relationship_rows_only",
    relationships,
    balance_rows: [],
  };
}

function isRelationshipGraphMode(mode: GraphViewMode) {
  return mode === "supply" || mode === "demand" || mode === "production-dependency" || mode === "supply-demand-balance";
}

function isPlainRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

type GraphEndpointDetails = {
  data?:
    | GraphTimelineData
    | GraphGeoData
    | GraphMatrixData
    | GraphEvidenceData
    | GraphScenarioOverlayData
    | GraphSourceCoverageData
    | GraphNodeCatalogData
    | GraphRelationshipData
    | GraphSupplyDemandBalanceData
    | Record<string, unknown>;
  message: string;
  mode?: GraphViewMode;
  source: "backend" | "fallback";
  status: "active" | "fallback" | "loading";
  diagnostics?: {
    failedEndpoint?: string;
    sourceStatus?: string;
    retryHint?: string;
    transportAttempts?: number;
  };
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
  } else if (options.mode === "source-coverage") {
    result = await apiClient.getGraphSourceCoverage({ limit: 50 });
  } else if (options.mode === "node-catalog") {
    result = await apiClient.getGraphNodeCatalog({ limit: 50 });
  } else if (options.mode === "supply") {
    result = await apiClient.getGraphSupplyRelationships({ limit: 50 });
  } else if (options.mode === "demand") {
    result = await apiClient.getGraphDemandRelationships({ limit: 50 });
  } else if (options.mode === "production-dependency") {
    result = await apiClient.getGraphProductionDependencies({ limit: 50 });
  } else if (options.mode === "supply-demand-balance") {
    result = await apiClient.getGraphSupplyDemandBalance({ limit: 50 });
  } else {
    result = await apiClient.getGraphScenarioOverlay({ runId: null });
  }

  if (result.data && result.envelope.status !== "error") {
    return {
      data: result.data as GraphEndpointDetails["data"],
      message: GRAPH_DATA_LOADED_MESSAGE,
      mode: options.mode,
      source: "backend",
      status: "active",
    };
  }
  return {
    message: GRAPH_ENDPOINT_UNAVAILABLE_MESSAGE,
    mode: options.mode,
    source: "fallback",
    status: "fallback",
    diagnostics: diagnosticsForEndpointResult(result),
  };
}

function EndpointStatusPanel({ details }: { details: GraphEndpointDetails }) {
  return (
    <div className={`graph-endpoint-status is-${details.status}`}>
      <strong>{endpointStatusTitle(details)}</strong>
      <span>{details.message}</span>
      {details.diagnostics ? (
        <MetadataSummary
          ariaLabel="Graph data diagnostic summary"
          items={[{ label: "Backend relationship data unavailable; authoritative rows are hidden.", tone: "warning" }]}
        />
      ) : null}
      {details.diagnostics ? (
        <DiagnosticDetails
          items={[
            { label: "failed_endpoint", value: details.diagnostics.failedEndpoint },
            { label: "source_status", value: details.diagnostics.sourceStatus },
            { label: "retry_hint", value: details.diagnostics.retryHint },
            { label: "transport_attempts", value: details.diagnostics.transportAttempts },
          ]}
        />
      ) : null}
    </div>
  );
}

function endpointStatusTitle(details: GraphEndpointDetails) {
  if (details.status === "loading") return "Authoritative data loading";
  if (details.source === "backend") return "Authoritative data connected";
  return "Backend data unavailable";
}

function diagnosticsForEndpointResult(result: ApiResult<unknown>): GraphEndpointDetails["diagnostics"] {
  const metadata = result.envelope.metadata;
  return {
    failedEndpoint: sanitizeEndpointDiagnostic(metadata?.failed_endpoint),
    sourceStatus: sanitizeEndpointDiagnostic(metadata?.source_status ?? result.sourceStatus),
    retryHint: sanitizeEndpointDiagnostic(metadata?.retry_hint),
    transportAttempts:
      typeof metadata?.transport_attempts === "number" ? metadata.transport_attempts : undefined,
  };
}

function sanitizeEndpointDiagnostic(value: unknown) {
  if (typeof value !== "string") return undefined;
  return value
    .replace(/[a-z][a-z0-9+.-]*:\/\/[^\s)]+/gi, "endpoint://redacted")
    .replace(/[?&][A-Za-z0-9_.~-]+=[^&\s)]+/g, "")
    .slice(0, 160);
}

function GraphModeDetailPanel({
  endpointData,
  graph,
  metadata,
  mode,
  view,
}: {
  endpointData: GraphEndpointDetails["data"];
  graph: GraphExplorerData;
  metadata: GraphVersionMetadata;
  mode: GraphViewMode;
  view: GraphViewModel;
}) {
  if (mode === "overview") return <GraphOverviewView graph={graph} metadata={metadata} view={view} />;
  if (mode === "timeline") return <GraphTimelineView graph={graph} endpointData={endpointData} view={view} />;
  if (mode === "geo") return <GraphGeoView endpointData={endpointData} graph={graph} view={view} />;
  if (mode === "scenario") return <GraphScenarioOverlay endpointData={endpointData} view={view} />;
  if (mode === "source-coverage") return <GraphSourceCoverageView endpointData={endpointData} view={view} />;
  if (mode === "node-catalog") return <GraphNodeCatalogView endpointData={endpointData} view={view} />;
  if (mode === "path") return <GraphPathView view={view} />;
  if (mode === "focus") return <GraphFocusView view={view} />;
  return null;
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
