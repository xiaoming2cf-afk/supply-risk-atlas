import { DataCard } from "./DataCards";
export function GraphQualityCard({ status = "unavailable" }: { status?: string }) {
  return <DataCard title="Graph quality" value={status} />;
}
