import type { SupplyRiskApiClient, SupplyRiskDashboardData } from "@supply-risk/api-client";
import type { DashboardPageId } from "@supply-risk/shared-types";
import type { ReactNode } from "react";
import { CausalEvidenceBoard } from "../features/evidence-board/CausalEvidenceBoard";
import { CompanyRisk360 } from "../features/entity-risk/EntityRisk360";
import { ForwardShockSimulator } from "../features/forward-stress/ForwardShockSimulator";
import { GraphExplorer } from "../features/graph-explorer/GraphExplorer";
import { InvestigationReport } from "../features/investigation-report/InvestigationReport";
import { InterventionOptimizer } from "../features/intervention-optimizer/InterventionOptimizer";
import { ReverseStressLab } from "../features/reverse-stress/ReverseStressLab";
import { SystemHealthCenter } from "../features/system-health/SystemHealthCenter";
import { getPageRelevancePolicy } from "../features/common/pageRelevance";
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
  const policy = getPageRelevancePolicy(pageId);
  const wrapRelevantPage = (content: ReactNode) => (
    <section
      data-page-relevance-policy={policy.pageId}
      data-page-purpose={policy.purpose}
      data-allowed-major-sections={policy.allowedMajorSections.join("|")}
      data-required-signals={policy.requiredSignals.join("|")}
      data-disallowed-major-sections={policy.disallowedMajorSections.join("|")}
      data-allows-dense-graph={policy.allowsDenseGraph ? "true" : "false"}
    >
      {content}
    </section>
  );

  switch (pageId) {
    case "global-risk-cockpit":
      return wrapRelevantPage(props.data.globalRiskCockpit ? <GlobalRiskCockpit data={props.data as SupplyRiskDashboardData} /> : <PageDataUnavailable />);
    case "graph-explorer":
      return wrapRelevantPage(props.data.graphExplorer && props.data.pathExplainer ? (
        <GraphExplorer apiClient={props.apiClient} data={props.data as SupplyRiskDashboardData} initialMode="supply-chain-flow" />
      ) : (
        <PageDataUnavailable />
      ));
    case "company-risk-360":
      return wrapRelevantPage(<CompanyRisk360 apiClient={props.apiClient} data={props.data} />);
    case "prediction-center":
      return wrapRelevantPage(props.data.predictionCenter ? <PredictionCenter data={props.data as SupplyRiskDashboardData} /> : <PageDataUnavailable />);
    case "path-analysis":
      return wrapRelevantPage(props.data.graphExplorer && props.data.pathExplainer ? (
        <GraphExplorer apiClient={props.apiClient} data={props.data as SupplyRiskDashboardData} initialMode="risk-propagation" />
      ) : (
        <PageDataUnavailable />
      ));
    case "country-lens":
      return wrapRelevantPage(props.data.graphExplorer && props.data.pathExplainer ? (
        <GraphExplorer apiClient={props.apiClient} data={props.data as SupplyRiskDashboardData} initialMode="geo-aggregate" />
      ) : (
        <PageDataUnavailable />
      ));
    case "path-explainer":
      return wrapRelevantPage(props.data.pathExplainer ? <PathExplainer data={props.data as SupplyRiskDashboardData} /> : <PageDataUnavailable />);
    case "shock-simulator":
      return wrapRelevantPage(<ForwardShockSimulator apiClient={props.apiClient} />);
    case "reverse-stress-lab":
      return wrapRelevantPage(<ReverseStressLab apiClient={props.apiClient} />);
    case "intervention-optimizer":
      return wrapRelevantPage(<InterventionOptimizer apiClient={props.apiClient} />);
    case "investigation-report":
      return wrapRelevantPage(<InvestigationReport apiClient={props.apiClient} />);
    case "causal-evidence-board":
      return wrapRelevantPage(props.data.causalEvidenceBoard ? <CausalEvidenceBoard data={props.data as SupplyRiskDashboardData} /> : <PageDataUnavailable />);
    case "graph-version-studio":
      return wrapRelevantPage(props.data.graphVersionStudio ? (
        <GraphVersionStudio data={props.data as SupplyRiskDashboardData} />
      ) : (
        <PageDataUnavailable title="This workspace is not available in the public view." />
      ));
    case "system-health-center":
      return wrapRelevantPage(props.data.systemHealthCenter ? <SystemHealthCenter data={props.data as SupplyRiskDashboardData} /> : <PageDataUnavailable />);
    default:
      return wrapRelevantPage(
        <div className="empty-state">
          <p>Page not configured.</p>
        </div>
      );
  }
}
