import type {
  CountryLensData,
  CountryRiskSummary,
  GraphLink,
  GraphNode,
  GraphTransmissionPath,
} from "@supply-risk/shared-types";
import { formatPercent } from "@supply-risk/design-system";
import { Field, RiskPill } from "../../app/components";
import { formatDisplayLabel, formatDisplayValue, formatNodeDisplayRef, formatSourceDisplayRef } from "../common/displayLabels";
import { graphScore } from "./graphLayout";

export function GraphInspector({
  activePath,
  countryLens,
  edge,
  node,
  onSelectPathStep,
  selectedCountry,
  selectedPath,
  selectedPathStepIndex,
}: {
  activePath?: GraphTransmissionPath;
  countryLens?: CountryLensData;
  edge?: GraphLink;
  node?: GraphNode;
  onSelectPathStep?: (index: number, nodeId: string) => void;
  selectedCountry?: CountryRiskSummary;
  selectedPath?: boolean;
  selectedPathStepIndex?: number;
}) {
  if (edge) return <EdgeInspector edge={edge} />;
  if (selectedCountry && countryLens) return <CountryInspector country={selectedCountry} countryLens={countryLens} />;
  if (selectedPath && activePath) {
    return <PathInspector onSelectStep={onSelectPathStep} path={activePath} selectedStepIndex={selectedPathStepIndex ?? 0} />;
  }
  if (node) return <NodeInspector node={node} />;
  return <div className="empty-state">Select an object to inspect.</div>;
}

function NodeInspector({ node }: { node: GraphNode }) {
  const evidenceRefs = nodeEvidenceRefs(node);
  const countryRef = formatCountryRef(node.countryCode ?? String(node.metadata.country ?? "global"));
  const metadataFields = nodeMetadataFields(node.metadata);
  return (
    <div className="inspector-stack">
      <div className="inspector-grid">
        <Field label="Name" value={node.label} />
        <Field label="Risk level" value={<RiskPill level={node.level} />} />
        <Field label="Risk score" value={`${graphScore(node.riskScore ?? node.score)}/100`} />
        <Field label="Centrality" value={`${graphScore(node.centralityScore ?? 0)}/100`} />
        <Field label="Criticality" value={`${graphScore(node.criticalityScore ?? node.score)}/100`} />
        <Field label="Rank" value={node.criticalityRank ? `#${node.criticalityRank}` : "n/a"} />
        <Field label="In / out degree" value={`${node.inDegree ?? 0} / ${node.outDegree ?? 0}`} />
        <Field label="Country" value={countryRef} />
      </div>
      <EvidenceRefs refs={evidenceRefs} />
      {metadataFields.length ? (
        <div className="inspector-grid">
          {metadataFields.map((field) => (
            <Field key={field.label} label={formatDisplayLabel(field.label)} value={formatInspectorValue(field.value)} />
          ))}
        </div>
      ) : null}
    </div>
  );
}

const NODE_METADATA_FIELD_ALLOWLIST: Array<{ label: string; keys: string[] }> = [
  { label: "Entity type", keys: ["entity_type", "node_type"] },
  { label: "Layer", keys: ["layer", "tier"] },
  { label: "Stage", keys: ["stage", "stage_id", "stage_label"] },
  { label: "Product grade", keys: ["product_grade"] },
  { label: "Product category", keys: ["product_category", "category"] },
  { label: "Commodity code", keys: ["commodity_code"] },
  { label: "Sector", keys: ["sector", "industry", "downstream_sector"] },
  { label: "Process stage", keys: ["process_stage", "process"] },
  { label: "Technology node", keys: ["technology_node", "node_generation"] },
  { label: "Material family", keys: ["material_family", "chemical_family"] },
  { label: "Evidence coverage", keys: ["source_status", "coverage_status"] },
  { label: "Confidence", keys: ["confidence"] },
];

function nodeMetadataFields(metadata: GraphNode["metadata"]) {
  const record = (metadata ?? {}) as Record<string, unknown>;
  const fields: Array<{ label: string; value: unknown }> = [];
  const usedKeys = new Set<string>();

  for (const field of NODE_METADATA_FIELD_ALLOWLIST) {
    const match = field.keys.find((key) => !usedKeys.has(key) && isDisplayableMetadataValue(record[key]));
    if (!match) continue;
    usedKeys.add(match);
    fields.push({ label: field.label, value: record[match] });
    if (fields.length >= 8) break;
  }

  return fields;
}

function isDisplayableMetadataValue(value: unknown) {
  if (value === null || value === undefined || value === "") return false;
  if (Array.isArray(value)) {
    return value.some((item) => item !== null && item !== undefined && item !== "") && value.every(isPrimitiveMetadataValue);
  }
  return isPrimitiveMetadataValue(value);
}

function isPrimitiveMetadataValue(value: unknown) {
  return value === null || value === undefined || ["string", "number", "boolean"].includes(typeof value);
}

function EdgeInspector({ edge }: { edge: GraphLink }) {
  const evidenceContext =
    edge.edgeType === "evidence_context" ||
    edge.metadata?.derived_context === true ||
    edge.metadata?.not_supply_chain_dependency === true;
  const scenarioTrace = edge.edgeType === "simulation_trace" || edge.edgeRole === "simulation_trace" || edge.metadata?.scenario_trace === true;
  return (
    <div className={`inspector-stack edge-inspector ${evidenceContext ? "is-evidence-context" : ""}`}>
      <div className="inspector-grid">
        <Field label="Inspector section" value={evidenceContext ? "Evidence context" : scenarioTrace ? "Scenario trace" : "Graph relationship"} />
        <Field label="Relationship type" value={formatInspectorValue(evidenceContext ? "evidence_context_link" : edge.edgeType ?? edge.label)} />
        <Field label="Role" value={formatInspectorValue(edge.edgeRole ?? "context")} />
        <Field label="Risk score" value={`${edge.riskScore ?? Math.round(edge.weight * 100)}/100`} />
        <Field label="Weight" value={formatPercent(edge.transmissionWeight ?? edge.weight)} />
        <Field label="Confidence" value={formatPercent(edge.confidence ?? 0)} />
        <Field label="Lag days" value={edge.lagDays ?? 0} />
        <Field label="Source country" value={formatCountryRef(edge.sourceCountry ?? "global")} />
        <Field label="Target country" value={formatCountryRef(edge.targetCountry ?? "global")} />
      </div>
      {evidenceContext ? (
        <p className="inspector-warning">Evidence context is inspection support, not supply-chain dependency.</p>
      ) : null}
      <EvidenceRefs refs={[edge.sourceId ?? "public_source_manifest", edge.edgeType ?? edge.edgeRole ?? "graph_edge", String(edge.metadata?.source ?? "")]} />
      <p className="inspector-note">
        {formatNodeRef(edge.source)} -&gt; {formatNodeRef(edge.target)}
      </p>
    </div>
  );
}

function PathInspector({
  onSelectStep,
  path,
  selectedStepIndex,
}: {
  onSelectStep?: (index: number, nodeId: string) => void;
  path: GraphTransmissionPath;
  selectedStepIndex: number;
}) {
  const boundedStepIndex = Math.min(selectedStepIndex, Math.max(0, path.steps.length - 1));
  return (
    <div className="inspector-stack path-inspector">
      <div className="inspector-grid">
        <Field label="Path risk" value={`${Math.round(path.pathRisk * 100)}/100`} />
        <Field label="Transmission" value={`${Math.round(path.transmissionScore * 100)}/100`} />
        <Field label="Confidence" value={formatPercent(path.pathConfidence)} />
        <Field label="Hops" value={path.edgeSequence.length} />
        <Field label="Countries" value={path.countrySequence.map(formatCountryRef).join(" -> ")} />
        <Field label="Bottleneck" value={formatInspectorValue(path.bottleneckEdgeId)} />
      </div>
      {path.steps.length > 1 ? (
        <div className="path-scrubber">
          <button
            aria-label="Previous path step"
            disabled={boundedStepIndex === 0}
            onClick={() => {
              const nextIndex = Math.max(0, boundedStepIndex - 1);
              const nextStep = path.steps[nextIndex];
              if (nextStep) onSelectStep?.(nextIndex, nextStep.nodeId);
            }}
            type="button"
          >
            Prev
          </button>
          <input
            aria-label="Selected path step"
            max={path.steps.length - 1}
            min={0}
            onChange={(event) => {
              const nextIndex = Number(event.target.value);
              const nextStep = path.steps[nextIndex];
              if (nextStep) onSelectStep?.(nextIndex, nextStep.nodeId);
            }}
            step={1}
            type="range"
            value={boundedStepIndex}
          />
          <button
            aria-label="Next path step"
            disabled={boundedStepIndex === path.steps.length - 1}
            onClick={() => {
              const nextIndex = Math.min(path.steps.length - 1, boundedStepIndex + 1);
              const nextStep = path.steps[nextIndex];
              if (nextStep) onSelectStep?.(nextIndex, nextStep.nodeId);
            }}
            type="button"
          >
            Next
          </button>
        </div>
      ) : null}
      <div className="transmission-step-list">
        {path.steps.map((step, index) => (
          <button
            className={`transmission-step ${index === boundedStepIndex ? "is-active" : ""}`}
            key={step.id}
            onClick={() => onSelectStep?.(index, step.nodeId)}
            type="button"
          >
            <span>{index + 1}</span>
            <div>
              <strong>{step.label}</strong>
              <small>{formatInspectorValue(step.edgeType ?? "source")} / {formatCountryRef(step.countryCode ?? "global")} / {formatInspectorValue(step.evidence)}</small>
            </div>
            <b>{step.contribution}</b>
          </button>
        ))}
      </div>
      <EvidenceRefs refs={path.steps.map((step) => step.sourceId ?? step.evidence)} />
    </div>
  );
}

function CountryInspector({
  country,
  countryLens,
}: {
  country: CountryRiskSummary;
  countryLens: CountryLensData;
}) {
  const selectedNodes = countryLens.topCriticalNodes?.length ? countryLens.topCriticalNodes : countryLens.criticalNodes;
  const selectedPaths = countryLens.topPaths?.length ? countryLens.topPaths : countryLens.transmissionPaths;
  return (
    <div className="inspector-stack country-inspector">
      <div className="inspector-grid">
        <Field label="Country" value={formatCountryRef(country.code) || country.label} />
        <Field label="Risk score" value={`${graphScore(country.riskScore)}/100`} />
        <Field label="Centrality" value={`${graphScore(country.centralityScore)}/100`} />
        <Field label="Entities" value={country.entityCount} />
        <Field label="Inbound risk" value={country.inboundRisk.toFixed(1)} />
        <Field label="Outbound risk" value={country.outboundRisk.toFixed(1)} />
      </div>
      <div className="country-lens-grid">
        <div>
          <div className="section-kicker">Top entities</div>
          <ul className="evidence-list compact">
            {selectedNodes.slice(0, 5).map((node) => (
              <li key={node.id}>{node.label} / {graphScore(node.criticalityScore ?? node.score)}</li>
            ))}
          </ul>
        </div>
        <div>
          <div className="section-kicker">High-risk paths</div>
          <ul className="evidence-list compact">
            {selectedPaths.slice(0, 4).map((path) => (
              <li key={path.id}>{path.sourceLabel} -&gt; {path.targetLabel}</li>
            ))}
          </ul>
        </div>
      </div>
      {country.subdivisions?.length ? (
        <div>
          <div className="section-kicker">Province / region detail</div>
          <ul className="evidence-list compact">
            {country.subdivisions.slice(0, 6).map((subdivision) => (
              <li key={subdivision.geoId}>
                {subdivision.label}: {subdivision.entityCount} entities / {graphScore(subdivision.riskScore)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      <EvidenceRefs refs={countryLens.dataCoverage.filter((coverage) => coverage.countryCode === country.code).map((coverage) => coverage.sourceId)} />
    </div>
  );
}

function EvidenceRefs({ refs }: { refs: string[] }) {
  const uniqueRefs = Array.from(new Set(refs.filter(Boolean))).slice(0, 8);
  if (uniqueRefs.length === 0) return null;
  return (
    <div>
      <div className="section-kicker">Evidence records</div>
      <ul className="evidence-list compact">
        {uniqueRefs.map((ref) => (
          <li key={ref}>{formatEvidenceRef(ref)}</li>
        ))}
      </ul>
    </div>
  );
}

function nodeEvidenceRefs(node: GraphNode) {
  return [
    ...(node.riskDrivers ?? []),
    String(node.metadata.source_id ?? ""),
    String(node.metadata.sourceId ?? ""),
    String(node.metadata.dataset ?? ""),
    String(node.metadata.evidence_ref ?? ""),
  ].filter(Boolean);
}

function formatCountryRef(value?: string | null) {
  const raw = String(value ?? "").trim();
  if (!raw || raw === "global") return "Global";
  const prefixed = raw.includes(":") ? raw : `country:${raw}`;
  return formatNodeDisplayRef(prefixed) || formatInspectorValue(raw);
}

function formatNodeRef(value?: string | null) {
  const raw = String(value ?? "").trim();
  return formatNodeDisplayRef(raw) || formatInspectorValue(raw);
}

function formatEvidenceRef(ref: string) {
  const sourceLabel = formatSourceDisplayRef(ref);
  if (sourceLabel) return sourceLabel;
  const nodeLabel = formatNodeDisplayRef(ref);
  if (nodeLabel) return nodeLabel;
  if (ref.startsWith("edge:")) return "Graph relationship evidence";
  return formatInspectorValue(ref);
}

function formatInspectorValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "n/a";
  if (Array.isArray(value)) {
    return value.map((item) => formatInspectorValue(item)).join(", ");
  }
  if (typeof value === "object") return "Structured metadata";

  const raw = String(value).trim();
  return formatSourceDisplayRef(raw) || formatNodeDisplayRef(raw) || String(formatDisplayValue(raw));
}
