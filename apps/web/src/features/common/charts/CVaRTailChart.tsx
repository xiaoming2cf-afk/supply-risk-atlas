import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function CVaRTailChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Tail loss detail"} {...props} />;
}
