import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function EventTimelineGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[10]} />;
}
