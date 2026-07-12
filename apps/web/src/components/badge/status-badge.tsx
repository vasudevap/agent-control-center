import { CheckCircle2, AlertTriangle, XCircle, CircleDashed, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export type AtlasStatus =
  | "healthy"
  | "degraded"
  | "offline"
  | "running"
  | "queued"
  | "pending"
  | "approved"
  | "rejected";

const STATUS_CONFIG: Record<
  AtlasStatus,
  { label: string; icon: React.ComponentType<{ className?: string }>; className: string; spin?: boolean }
> = {
  healthy: {
    label: "Healthy",
    icon: CheckCircle2,
    className: "bg-success-bg text-success border-success-border",
  },
  degraded: {
    label: "Degraded",
    icon: AlertTriangle,
    className: "bg-warning-bg text-warning border-warning-border",
  },
  offline: {
    label: "Offline",
    icon: XCircle,
    className: "bg-error-bg text-error border-error-border",
  },
  running: {
    label: "Running",
    icon: Loader2,
    className: "bg-info-bg text-info border-info-border",
    spin: true,
  },
  queued: {
    label: "Queued",
    icon: CircleDashed,
    className: "bg-surface-tertiary text-foreground-secondary border-transparent",
  },
  pending: {
    label: "Pending",
    icon: CircleDashed,
    className: "bg-warning-bg text-warning border-warning-border",
  },
  approved: {
    label: "Approved",
    icon: CheckCircle2,
    className: "bg-success-bg text-success border-success-border",
  },
  rejected: {
    label: "Rejected",
    icon: XCircle,
    className: "bg-error-bg text-error border-error-border",
  },
};

export interface StatusBadgeProps {
  status: AtlasStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        config.className,
        className
      )}
    >
      <Icon className={cn("size-3.5", config.spin && "animate-spin")} aria-hidden="true" />
      {config.label}
    </span>
  );
}
