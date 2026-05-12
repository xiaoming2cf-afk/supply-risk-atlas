import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function SourceFreshnessChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Source freshness"} {...props} />;
}
