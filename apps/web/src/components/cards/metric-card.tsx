import type { LucideIcon } from "lucide-react";
import { TrendingUp, TrendingDown, AlertCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export interface MetricCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    direction: "up" | "down";
    value: string;
    tone?: "positive" | "negative" | "neutral";
  };
  tone?: "default" | "success" | "warning" | "error";
  state?: "success" | "loading" | "error";
  errorMessage?: string;
  className?: string;
}

const TONE_ICON_CLASS: Record<NonNullable<MetricCardProps["tone"]>, string> = {
  default: "bg-surface-tertiary text-foreground-secondary",
  success: "bg-success-bg text-success",
  warning: "bg-warning-bg text-warning",
  error: "bg-error-bg text-error",
};

export function MetricCard({
  label,
  value,
  icon: Icon,
  trend,
  tone = "default",
  state = "success",
  errorMessage = "Unable to load metric",
  className,
}: MetricCardProps) {
  if (state === "loading") {
    return (
      <Card className={cn("p-6 sm:p-8", className)} aria-busy="true">
        <div className="flex items-start justify-between">
          <div className="flex flex-col gap-3">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-10 w-20" />
          </div>
          <Skeleton className="size-8 rounded-atlas-md" />
        </div>
      </Card>
    );
  }

  if (state === "error") {
    return (
      <Card className={cn("p-6 sm:p-8", className)}>
        <div className="flex items-start gap-3">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-atlas-md bg-error-bg text-error">
            <AlertCircle className="size-4" aria-hidden="true" />
          </div>
          <div className="flex flex-col gap-0.5">
            <p className="text-sm font-medium text-foreground">{label}</p>
            <p className="text-xs text-foreground-secondary">{errorMessage}</p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className={cn("p-6 sm:p-8", className)}>
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-2">
          <p className="font-mono text-[11px] font-medium uppercase tracking-wider text-foreground-tertiary">
            {label}
          </p>
          <p className="text-4xl font-semibold tracking-tight tabular-nums text-foreground sm:text-5xl">
            {value}
          </p>
          {trend && (
            <div
              className={cn(
                "flex items-center gap-1 text-xs font-medium",
                trend.tone === "negative"
                  ? "text-error"
                  : trend.tone === "neutral"
                    ? "text-foreground-secondary"
                    : "text-success"
              )}
            >
              {trend.direction === "up" ? (
                <TrendingUp className="size-3.5" aria-hidden="true" />
              ) : (
                <TrendingDown className="size-3.5" aria-hidden="true" />
              )}
              <span className="font-mono">{trend.value}</span>
            </div>
          )}
        </div>
        <div
          className={cn(
            "flex size-8 shrink-0 items-center justify-center rounded-atlas-md",
            TONE_ICON_CLASS[tone]
          )}
        >
          <Icon className="size-4" aria-hidden="true" />
        </div>
      </div>
    </Card>
  );
}
