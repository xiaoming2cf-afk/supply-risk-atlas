import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function HazardExposureByLayerChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Hazard exposure by layer"} {...props} />;
}
