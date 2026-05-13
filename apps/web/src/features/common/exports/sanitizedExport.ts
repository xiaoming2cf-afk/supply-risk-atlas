const blockedKeyParts = ["raw", "payload", "secret", "token", "private", "cookie", "authorization", "password", "internal_path"];

export function sanitizeExportRows(rows: Array<Record<string, unknown>>) {
  return rows.map((row) => sanitizeRow(row));
}

export function buildSanitizedJsonExport({
  graphVersion,
  sourceManifestId,
  tableId,
  warnings = [],
  rows,
}: {
  graphVersion?: string | null;
  rows: Array<Record<string, unknown>>;
  sourceManifestId?: string | null;
  tableId: string;
  warnings?: string[];
}) {
  return {
    table_id: tableId,
    graph_version: graphVersion ?? "unavailable",
    source_manifest_id: sourceManifestId ?? "unavailable",
    export_scope: "sanitized_visible_rows",
    warnings,
    rows: sanitizeExportRows(rows),
  };
}

function sanitizeRow(row: Record<string, unknown>) {
  const clean: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(row)) {
    const lowered = key.toLowerCase();
    if (blockedKeyParts.some((part) => lowered.includes(part))) continue;
    clean[key] = sanitizeValue(value);
  }
  return clean;
}

function sanitizeValue(value: unknown): unknown {
  if (value === null || typeof value === "number" || typeof value === "boolean") return value;
  if (typeof value === "string") return sanitizeText(value);
  if (Array.isArray(value)) return value.slice(0, 50).map(sanitizeValue);
  if (typeof value === "object") return sanitizeRow(value as Record<string, unknown>);
  return sanitizeText(String(value));
}

function sanitizeText(value: string) {
  const stripped = value.replace(/[<>]/g, "");
  if (/script|onerror|javascript:/i.test(stripped)) return "[sanitized external text]";
  return stripped.length > 500 ? `${stripped.slice(0, 497)}...` : stripped;
}
