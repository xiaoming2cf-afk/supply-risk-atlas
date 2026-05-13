import { StackedBarChart, type BasicChartProps } from "./ChartPrimitives";

export function StageRiskContributionChart(props: BasicChartProps) {
  return <StackedBarChart title={props.title ?? "Stage risk contribution"} {...props} />;
}
