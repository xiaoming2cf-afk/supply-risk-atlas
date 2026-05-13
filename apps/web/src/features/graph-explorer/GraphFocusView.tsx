import type { GraphViewModel } from "./graphViewModel";

export function GraphFocusView({ view }: { view: GraphViewModel }) {
  return (
    <div className="graph-v3-panel graph-v3-focus-panel">
      <div className="section-kicker">Focus mode</div>
      <p className="inspector-note">
        Focus keeps one selected node visually dominant, with explicit upstream, downstream, two-hop, pin, and low-confidence controls.
      </p>
      <ul className="evidence-list compact">
        {view.visibleNodes.slice(0, 5).map((node) => (
          <li key={node.id}>{node.label} / {node.kind} / {node.countryCode ?? "global"}</li>
        ))}
      </ul>
    </div>
  );
}
