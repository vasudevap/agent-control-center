import { AlertOctagon, AlertTriangle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

export type AlertSeverity = "critical" | "warning" | "information";

export interface AlertCardProps {
  severity: AlertSeverity;
  title: string;
  description: string;
  timestamp: string;
  source?: string;
  className?: string;
}

const SEVERITY_CONFIG: Record<
  AlertSeverity,
  { icon: React.ComponentType<{ className?: string }>; iconClass: string; label: string }
> = {
  critical: { icon: AlertOctagon, iconClass: "bg-error-bg text-error", label: "Critical" },
  warning: { icon: AlertTriangle, iconClass: "bg-warning-bg text-warning", label: "Warning" },
  information: { icon: Info, iconClass: "bg-info-bg text-info", label: "Info" },
};

export function AlertCard({
  severity,
  title,
  description,
  timestamp,
  source,
  className,
}: AlertCardProps) {
  const config = SEVERITY_CONFIG[severity];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        "flex gap-3 rounded-atlas-md border border-border-default bg-surface p-3",
        className
      )}
    >
      <div
        className={cn(
          "flex size-8 shrink-0 items-center justify-center rounded-atlas-md",
          config.iconClass
        )}
      >
        <Icon className="size-4" aria-hidden="true" />
      </div>
      <div className="flex min-w-0 flex-1 flex-col gap-0.5">
        <div className="flex items-center justify-between gap-2">
          <p className="truncate text-sm font-medium text-foreground">{title}</p>
          <span className="shrink-0 font-mono text-xs text-foreground-tertiary">
            {timestamp}
          </span>
        </div>
        <p className="text-xs text-foreground-secondary">{description}</p>
        {source && (
          <span className="mt-0.5 text-xs font-medium text-foreground-tertiary">{source}</span>
        )}
      </div>
    </div>
  );
}
