import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function DownstreamDemandGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[9]} />;
}
