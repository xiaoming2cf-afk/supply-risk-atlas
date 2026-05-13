import { LineChart, type BasicChartProps } from "./ChartPrimitives";

export function EquipmentRestrictionTimelineChart(props: BasicChartProps) {
  return <LineChart title={props.title ?? "Equipment restriction timeline"} {...props} />;
}
