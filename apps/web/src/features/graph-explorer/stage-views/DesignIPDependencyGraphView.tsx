import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function DesignIPDependencyGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[3]} />;
}
