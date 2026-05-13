import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function StageEvidenceQualityChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Stage evidence quality"} {...props} />;
}
