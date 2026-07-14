import { Circle, Triangle, TriangleAlert, Diamond } from "lucide-react";
import { cn } from "@/lib/utils";

export type RiskLevel = "Low" | "Medium" | "High" | "Critical";

const RISK_CONFIG: Record<
  RiskLevel,
  { icon: React.ComponentType<{ className?: string }>; text: string; bg: string; border: string }
> = {
  Low: { icon: Circle, text: "text-risk-low", bg: "bg-risk-low-bg", border: "border-risk-low-border" },
  Medium: { icon: Triangle, text: "text-risk-medium", bg: "bg-risk-medium-bg", border: "border-risk-medium-border" },
  High: { icon: TriangleAlert, text: "text-risk-high", bg: "bg-risk-high-bg", border: "border-risk-high-border" },
  Critical: { icon: Diamond, text: "text-risk-critical", bg: "bg-risk-critical-bg", border: "border-risk-critical-border" },
};

/**
 * Risk is communicated through two independent channels: a distinct
 * icon shape and the word itself, inside a fixed-width pill so every
 * chip in a column lines up regardless of label length. Earlier this
 * carried a third channel, a colored left-edge bar (RiskBar), but that
 * bar was color-only and, being a thin sliver, made adjacent hues
 * (red/orange) especially hard to discriminate. It was dropped rather
 * than fixed: the icon+label pill is already sufficient and reserving
 * strong color for that single pill (instead of duplicating it in a
 * second chrome element) also keeps rows from all shouting at once.
 */
export function RiskChip({ risk, label, iconOnly, className }: { risk: RiskLevel; label?: string; iconOnly?: boolean; className?: string }) {
  const config = RISK_CONFIG[risk];
  const Icon = config.icon;
  const text = label ?? risk;

  if (iconOnly) {
    return (
      <span className={cn("inline-flex shrink-0 items-center justify-center", config.text, className)}>
        <Icon className={cn("size-[11px]", risk === "Critical" && "fill-current")} aria-hidden="true" />
        <span className="sr-only">{text}</span>
      </span>
    );
  }

  return (
    <span
      className={cn(
        "inline-flex min-w-[78px] items-center justify-center gap-1.5 rounded-atlas-sm border px-2 py-0.5 text-xs font-semibold",
        config.text,
        config.bg,
        config.border,
        className
      )}
    >
      <Icon className={cn("size-3 shrink-0", risk === "Critical" && "fill-current")} aria-hidden="true" />
      {text}
    </span>
  );
}

export function riskRank(risk: RiskLevel) {
  return { Low: 0, Medium: 1, High: 2, Critical: 3 }[risk];
}
