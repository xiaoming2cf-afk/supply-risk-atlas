import { LineChart, type BasicChartProps } from "./ChartPrimitives";

export function FunctionalityCurveChart(props: BasicChartProps) {
  return <LineChart title={props.title ?? "Functionality curve"} {...props} />;
}
