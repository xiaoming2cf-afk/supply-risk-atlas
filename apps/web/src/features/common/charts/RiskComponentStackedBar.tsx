import { StackedBarChart, type BasicChartProps } from "./ChartPrimitives";

export function RiskComponentStackedBar(props: BasicChartProps) {
  return <StackedBarChart title={props.title ?? "Risk component breakdown"} {...props} />;
}
