import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function CVaRTailChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "CVaR tail"} {...props} />;
}
