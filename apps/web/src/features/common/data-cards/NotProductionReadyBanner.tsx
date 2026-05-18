export function NotProductionReadyBanner({ message = "Research fixture mode" }: { message?: string }) {
  return <div className="warning-text" data-component="not-production-ready">{message}</div>;
}
