import { Field, Panel } from "../../app/components";
import { EvidenceCountCard, SourceFreshnessCard } from "../common/data-cards";
import { buildSanitizedJsonExport } from "../common/exports";
import { EvidenceRefsTable } from "../common/tables";

export function EvidenceAuditPanel({
  activeSource,
  confidenceFloor,
  graphVersion,
  rows,
  sourceManifestId,
  warnings,
}: {
  activeSource: string;
  confidenceFloor: string;
  graphVersion?: string | null;
  rows: Array<Record<string, unknown>>;
  sourceManifestId?: string | null;
  warnings?: string[];
}) {
  const sanitizedExport = buildSanitizedJsonExport({
    graphVersion,
    rows,
    sourceManifestId,
    tableId: "evidence_refs",
    warnings,
  });
  return (
    <Panel title="Evidence audit table" subtitle="Source filters and confidence fields are bounded display summaries only.">
      <div className="lineage-chips" style={{ marginBottom: 12 }}>
        <SourceFreshnessCard status="fixture_proxy_not_live" />
        <EvidenceCountCard count={rows.length} />
      </div>
      <div className="field-grid">
        <Field label="source_filter" value={activeSource} />
        <Field label="confidence_filter" value={confidenceFloor} />
        <Field label="evidence_to_graph_path" value={String(rows[0]?.graph_path_ref ?? "unavailable")} />
        <Field label="export_scope" value={sanitizedExport.export_scope} />
      </div>
      <EvidenceRefsTable
        rows={rows}
        columns={["id", "source", "method", "confidence", "disagreement", "graph_path_ref"]}
        limit={10}
        metadata={{ graphVersion, sourceManifestId, warnings }}
      />
    </Panel>
  );
}
