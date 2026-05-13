import type { GraphViewModel } from "./graphViewModel";

export function GraphPathView({ view }: { view: GraphViewModel }) {
  return (
    <div className="graph-v3-panel graph-v3-path-panel">
      <div className="section-kicker">Path mode evidence trail</div>
      <ol className="graph-step-table">
        {(view.activePath?.steps ?? []).map((step, index) => (
          <li key={step.id}>
            <strong>{index + 1}. {step.label}</strong>
            <span>{step.edgeType ?? "source"} / {step.evidence}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
