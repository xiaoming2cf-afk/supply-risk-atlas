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
  const visibleRows = rows.map((row, index) => ({
    ...row,
    graph_path_ref: formatEvidencePathLabel(index),
  }));
  return (
    <Panel title="Evidence review table" subtitle="Source filters and confidence fields are bounded display summaries only.">
      <div className="lineage-chips" style={{ marginBottom: 12 }}>
        <SourceFreshnessCard status="fixture_proxy_not_live" />
        <EvidenceCountCard count={rows.length} />
      </div>
      <div className="field-grid">
        <Field label="Source filter" value={activeSource} />
        <Field label="Confidence filter" value={confidenceFloor} />
        <Field label="Graph path link" value={visibleRows.length ? formatEvidencePathLabel(0) : "unavailable"} />
        <Field label="Export scope" value={sanitizedExport.export_scope} />
      </div>
      <EvidenceRefsTable
        rows={visibleRows}
        columns={["id", "source", "method", "confidence", "disagreement", "graph_path_ref"]}
        limit={10}
        metadata={{ graphVersion, sourceManifestId, warnings }}
      />
    </Panel>
  );
}

function formatEvidencePathLabel(index: number) {
  return `Evidence path ${index + 1}`;
}
