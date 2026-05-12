import { DataCard } from "./DataCards";
export function SourceFreshnessCard({ status = "unavailable" }: { status?: string }) {
  return <DataCard title="Source freshness" value={status} />;
}
