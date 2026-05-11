export function GraphEmptyState({ message = "No graph elements match the current view." }: { message?: string }) {
  return (
    <div className="empty-state graph-empty-state">
      <div className="empty-state-shell">
        <h2>Graph view unavailable</h2>
        <p>{message}</p>
      </div>
    </div>
  );
}
