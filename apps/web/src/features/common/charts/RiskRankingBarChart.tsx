import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function RiskRankingBarChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Risk ranking"} {...props} />;
}
