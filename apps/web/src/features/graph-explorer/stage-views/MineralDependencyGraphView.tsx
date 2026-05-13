import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function MineralDependencyGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[1]} />;
}
