import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function GraphQualityChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Graph quality"} {...props} />;
}
