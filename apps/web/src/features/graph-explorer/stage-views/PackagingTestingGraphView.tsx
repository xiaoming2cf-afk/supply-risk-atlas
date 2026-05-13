import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function PackagingTestingGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[7]} />;
}
