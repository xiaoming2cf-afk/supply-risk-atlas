import { StageGraphView, stageViewOptions, type StageGraphViewProps } from "./StageGraphView";

export function MaterialChemicalDependencyGraphView(props: Omit<StageGraphViewProps, "stage">) {
  return <StageGraphView {...props} stage={stageViewOptions[2]} />;
}
