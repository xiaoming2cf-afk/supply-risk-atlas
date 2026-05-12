import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function OptimizerBeforeAfterChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Optimizer before after"} {...props} />;
}
