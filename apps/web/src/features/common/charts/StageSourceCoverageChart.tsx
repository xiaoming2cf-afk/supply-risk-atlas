import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function StageSourceCoverageChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Stage source coverage"} {...props} />;
}
