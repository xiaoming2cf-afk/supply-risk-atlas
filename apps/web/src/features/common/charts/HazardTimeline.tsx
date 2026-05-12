import { LineChart, type BasicChartProps } from "./ChartPrimitives";

export function HazardTimeline(props: BasicChartProps) {
  return <LineChart title={props.title ?? "Hazard timeline"} {...props} />;
}
