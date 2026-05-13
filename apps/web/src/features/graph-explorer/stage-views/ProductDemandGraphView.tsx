import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function ProductDemandGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[6]} />;
}
