import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function ProductToProcessDependencyChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Product to process dependency"} {...props} />;
}
