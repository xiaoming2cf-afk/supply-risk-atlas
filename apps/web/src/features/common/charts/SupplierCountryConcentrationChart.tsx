import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function SupplierCountryConcentrationChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Supplier country concentration"} {...props} />;
}
