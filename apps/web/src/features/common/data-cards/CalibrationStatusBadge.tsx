import { MetadataBadge, type BadgeProps } from "./DataCards";

export function CalibrationStatusBadge(props: Omit<BadgeProps, "label"> & { label?: string }) {
  return <MetadataBadge label={props.label ?? "calibration_status"} tone={props.tone ?? "warn"} value={props.value} />;
}
