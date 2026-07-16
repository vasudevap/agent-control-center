import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  CircleDashed,
  History,
  Loader2,
  Power,
  PowerOff,
  Undo2,
  Clock3,
  ListChecks,
  TimerOff,
  PackageCheck,
  FileWarning,
  SearchCheck,
  Ban,
} from "lucide-react";
import { cn } from "@/lib/utils";

export type AtlasStatus =
  | "healthy"
  | "degraded"
  | "offline"
  | "running"
  | "active"
  | "paused"
  | "queued"
  | "pending"
  | "approved"
  | "rejected"
  | "expired"
  | "cancelled"
  | "waiting"
  | "succeeded"
  | "partially-succeeded"
  | "failed"
  | "timed-out"
  | "available"
  | "review-required"
  | "investigating"
  | "resolved"
  | "revoked";

const STATUS_CONFIG: Record<
  AtlasStatus,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    text: string;
    className: string;
    spin?: boolean;
    iconSize?: string;
  }
> = {
  healthy: {
    label: "Healthy",
    icon: CheckCircle2,
    text: "text-success",
    className: "bg-success-bg text-success border-success-border",
  },
  degraded: {
    label: "Degraded",
    icon: AlertTriangle,
    text: "text-warning",
    className: "bg-warning-bg text-warning border-warning-border",
    // AlertTriangle occupies noticeably less of its bounding box than
    // CheckCircle2/XCircle at the same nominal size, so it reads as
    // smaller next to them even though the size is identical. Bumped
    // to compensate, so every health icon reads as the same weight.
    iconSize: "size-[13px]",
  },
  offline: {
    label: "Offline",
    icon: XCircle,
    text: "text-error",
    className: "bg-error-bg text-error border-error-border",
  },
  running: {
    label: "Running",
    icon: Loader2,
    text: "text-info",
    className: "bg-info-bg text-info border-info-border",
    spin: true,
  },
  active: {
    label: "Active",
    icon: Power,
    text: "text-success",
    className: "bg-success-bg text-success border-success-border",
  },
  paused: {
    label: "Paused",
    icon: PowerOff,
    text: "text-foreground-secondary",
    className:
      "bg-surface-tertiary text-foreground-secondary border-transparent",
  },
  queued: {
    label: "Queued",
    icon: CircleDashed,
    text: "text-foreground-secondary",
    className:
      "bg-surface-tertiary text-foreground-secondary border-transparent",
  },
  pending: {
    label: "Pending",
    icon: CircleDashed,
    text: "text-warning",
    className: "bg-warning-bg text-warning border-warning-border",
  },
  approved: {
    label: "Approved",
    icon: CheckCircle2,
    text: "text-success",
    className: "bg-success-bg text-success border-success-border",
  },
  rejected: {
    label: "Rejected",
    icon: XCircle,
    text: "text-error",
    className: "bg-error-bg text-error border-error-border",
  },
  expired: {
    label: "Expired",
    icon: History,
    text: "text-foreground-secondary",
    className:
      "bg-surface-tertiary text-foreground-secondary border-transparent",
  },
  cancelled: {
    label: "Cancelled",
    icon: Undo2,
    text: "text-foreground-secondary",
    className:
      "bg-surface-tertiary text-foreground-secondary border-transparent",
  },
  waiting: {
    label: "Waiting for approval",
    icon: Clock3,
    text: "text-warning",
    className: "bg-warning-bg text-warning border-warning-border",
  },
  succeeded: {
    label: "Succeeded",
    icon: CheckCircle2,
    text: "text-success",
    className: "bg-success-bg text-success border-success-border",
  },
  "partially-succeeded": {
    label: "Partially succeeded",
    icon: ListChecks,
    text: "text-warning",
    className: "bg-warning-bg text-warning border-warning-border",
  },
  failed: {
    label: "Failed",
    icon: XCircle,
    text: "text-error",
    className: "bg-error-bg text-error border-error-border",
  },
  "timed-out": {
    label: "Timed out",
    icon: TimerOff,
    text: "text-error",
    className: "bg-error-bg text-error border-error-border",
  },
  available: {
    label: "Available",
    icon: PackageCheck,
    text: "text-success",
    className: "bg-success-bg text-success border-success-border",
  },
  "review-required": {
    label: "Review required",
    icon: FileWarning,
    text: "text-warning",
    className: "bg-warning-bg text-warning border-warning-border",
  },
  investigating: {
    label: "Investigating",
    icon: SearchCheck,
    text: "text-info",
    className: "bg-info-bg text-info border-info-border",
  },
  resolved: {
    label: "Resolved",
    icon: CheckCircle2,
    text: "text-success",
    className: "bg-success-bg text-success border-success-border",
  },
  revoked: {
    label: "Revoked",
    icon: Ban,
    text: "text-error",
    className: "bg-error-bg text-error border-error-border",
  },
};

export interface StatusBadgeProps {
  status: AtlasStatus;
  iconOnly?: boolean;
  /** Icon + label in the status color, no pill background/border. For
   * contexts like a label/value fact list where every other value is
   * plain text and a filled pill would look like a different kind of
   * element rather than just another value in the same list. */
  plain?: boolean;
  className?: string;
}

/**
 * `iconOnly` is bare (no filled background/border), matching the same
 * convention RiskChip uses in compact contexts: a colored icon alone,
 * with the label preserved for screen readers via sr-only text. The
 * legend that explains the icon vocabulary belongs wherever this is
 * used compactly, in the same header/control-bar slot each time.
 */
export function StatusBadge({
  status,
  iconOnly,
  plain,
  className,
}: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  const Icon = config.icon;

  if (iconOnly) {
    return (
      <span
        className={cn(
          "inline-flex shrink-0 items-center justify-center",
          config.text,
          className,
        )}
      >
        <Icon
          className={cn(
            config.iconSize ?? "size-[11px]",
            config.spin && "animate-spin",
          )}
          aria-hidden="true"
        />
        <span className="sr-only">{config.label}</span>
      </span>
    );
  }

  if (plain) {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 font-medium",
          config.text,
          className,
        )}
      >
        <Icon
          className={cn(
            config.iconSize ?? "size-3.5",
            config.spin && "animate-spin",
          )}
          aria-hidden="true"
        />
        {config.label}
      </span>
    );
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        config.className,
        className,
      )}
    >
      <Icon
        className={cn("size-3.5", config.spin && "animate-spin")}
        aria-hidden="true"
      />
      {config.label}
    </span>
  );
}
