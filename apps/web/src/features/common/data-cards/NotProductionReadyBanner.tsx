export function NotProductionReadyBanner({ message = "not_production_ready" }: { message?: string }) {
  return <div className="warning-text" data-component="not-production-ready">{message}</div>;
}
