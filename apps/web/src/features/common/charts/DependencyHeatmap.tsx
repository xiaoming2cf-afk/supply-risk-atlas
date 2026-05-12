import { HeatmapChart, type BasicChartProps } from "./ChartPrimitives";

export function DependencyHeatmap(props: BasicChartProps) {
  return <HeatmapChart title={props.title ?? "Dependency heatmap"} {...props} />;
}
