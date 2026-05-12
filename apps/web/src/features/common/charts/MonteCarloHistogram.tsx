import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function MonteCarloHistogram(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Monte Carlo histogram"} {...props} />;
}
