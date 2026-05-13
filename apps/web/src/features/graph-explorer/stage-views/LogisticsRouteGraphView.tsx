import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function LogisticsRouteGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[8]} />;
}
