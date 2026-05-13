import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function LogisticsRouteExposureChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Logistics route exposure"} {...props} />;
}
