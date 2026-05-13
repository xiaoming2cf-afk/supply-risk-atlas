import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function CriticalInputBottleneckChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Critical input bottlenecks"} {...props} />;
}
