import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function ComplianceRiskGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[11]} />;
}
