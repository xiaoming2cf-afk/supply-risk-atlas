import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function EquipmentProcessDependencyGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[4]} />;
}
