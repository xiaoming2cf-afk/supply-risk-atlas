import type { SupplyRiskApiClient, SupplyRiskDashboardData } from "@supply-risk/api-client";
import type { DashboardPageId } from "@supply-risk/shared-types";
import { CausalEvidenceBoard } from "../features/evidence-board/CausalEvidenceBoard";
import { CompanyRisk360 } from "../features/entity-risk/EntityRisk360";
import { ForwardShockSimulator } from "../features/forward-stress/ForwardShockSimulator";
import { GraphExplorer } from "../features/graph-explorer/GraphExplorer";
import { InvestigationReport } from "../features/investigation-report/InvestigationReport";
import { InterventionOptimizer } from "../features/intervention-optimizer/InterventionOptimizer";
import { ReverseStressLab } from "../features/reverse-stress/ReverseStressLab";
import { SystemHealthCenter } from "../features/system-health/SystemHealthCenter";
import {
  GlobalRiskCockpit,
  GraphVersionStudio,
  PageDataUnavailable,
  PathExplainer,
  PredictionCenter
} from "../features/common/legacyDashboard";

export interface PageRenderProps {
  data: Partial<SupplyRiskDashboardData>;
  apiClient: SupplyRiskApiClient;
}

export function renderPage(pageId: DashboardPageId, props: PageRenderProps) {
  switch (pageId) {
    case "global-risk-cockpit":
      return props.data.globalRiskCockpit ? <GlobalRiskCockpit data={props.data as SupplyRiskDashboardData} /> : <PageDataUnavailable />;
    case "graph-explorer":
      return props.data.graphExplorer && props.data.pathExplainer ? (
        <GraphExplorer apiClient={props.apiClient} data={props.data as SupplyRiskDashboardData} initialMode="supply-chain-flow" />
      ) : (
        <PageDataUnavailable />
      );
    case "company-risk-360":
      return <CompanyRisk360 apiClient={props.apiClient} data={props.data} />;
    case "prediction-center":
      return props.data.predictionCenter ? <PredictionCenter data={props.data as SupplyRiskDashboardData} /> : <PageDataUnavailable />;
    case "path-analysis":
      return props.data.graphExplorer && props.data.pathExplainer ? (
        <GraphExplorer apiClient={props.apiClient} data={props.data as SupplyRiskDashboardData} initialMode="risk-propagation" />
      ) : (
        <PageDataUnavailable />
      );
    case "country-lens":
      return props.data.graphExplorer && props.data.pathExplainer ? (
        <GraphExplorer apiClient={props.apiClient} data={props.data as SupplyRiskDashboardData} initialMode="geo-aggregate" />
      ) : (
        <PageDataUnavailable />
      );
    case "path-explainer":
      return props.data.pathExplainer ? <PathExplainer data={props.data as SupplyRiskDashboardData} /> : <PageDataUnavailable />;
    case "shock-simulator":
      return <ForwardShockSimulator apiClient={props.apiClient} />;
    case "reverse-stress-lab":
      return <ReverseStressLab apiClient={props.apiClient} />;
    case "intervention-optimizer":
      return <InterventionOptimizer apiClient={props.apiClient} />;
    case "investigation-report":
      return <InvestigationReport apiClient={props.apiClient} />;
    case "causal-evidence-board":
      return props.data.causalEvidenceBoard ? <CausalEvidenceBoard data={props.data as SupplyRiskDashboardData} /> : <PageDataUnavailable />;
    case "graph-version-studio":
      return props.data.graphVersionStudio ? (
        <GraphVersionStudio data={props.data as SupplyRiskDashboardData} />
      ) : (
        <PageDataUnavailable title="This workspace is not available in the public view." />
      );
    case "system-health-center":
      return props.data.systemHealthCenter ? <SystemHealthCenter data={props.data as SupplyRiskDashboardData} /> : <PageDataUnavailable />;
    default:
      return (
        <div className="empty-state">
          <p>Page not configured.</p>
        </div>
      );
  }
}
