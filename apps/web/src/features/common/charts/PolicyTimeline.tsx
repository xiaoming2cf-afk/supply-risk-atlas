import { LineChart, type BasicChartProps } from "./ChartPrimitives";

export function PolicyTimeline(props: BasicChartProps) {
  return <LineChart title={props.title ?? "Policy timeline"} {...props} />;
}
