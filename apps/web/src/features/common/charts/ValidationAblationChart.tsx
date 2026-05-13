import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function ValidationAblationChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Validation ablation"} {...props} />;
}
