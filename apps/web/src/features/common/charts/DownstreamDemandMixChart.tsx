import { StackedBarChart, type BasicChartProps } from "./ChartPrimitives";

export function DownstreamDemandMixChart(props: BasicChartProps) {
  return <StackedBarChart title={props.title ?? "Downstream demand mix"} {...props} />;
}
