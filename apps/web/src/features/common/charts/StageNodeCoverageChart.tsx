import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function StageNodeCoverageChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Stage node coverage"} {...props} />;
}
