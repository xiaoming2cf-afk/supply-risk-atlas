import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function FabProcessGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[5]} />;
}
