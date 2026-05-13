import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function DownstreamDemandPressureChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Downstream demand pressure"} {...props} />;
}
