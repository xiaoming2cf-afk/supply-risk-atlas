import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function PolicyMacroGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[0]} />;
}
