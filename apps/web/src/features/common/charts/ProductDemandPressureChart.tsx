import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function ProductDemandPressureChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Product demand pressure"} {...props} />;
}
