import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function FabHazardExposureChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Fab hazard exposure"} {...props} />;
}
