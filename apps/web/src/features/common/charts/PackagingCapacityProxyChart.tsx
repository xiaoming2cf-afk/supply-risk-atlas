import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function PackagingCapacityProxyChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Packaging capacity proxy"} {...props} />;
}
