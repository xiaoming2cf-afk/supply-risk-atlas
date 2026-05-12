import { DataCard } from "./DataCards";
export function EvidenceCountCard({ count = 0 }: { count?: number }) {
  return <DataCard title="Evidence count" value={count} />;
}
