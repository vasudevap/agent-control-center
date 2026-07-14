import { Circle, Triangle, TriangleAlert, Diamond } from "lucide-react";
import { cn } from "@/lib/utils";

export type RiskLevel = "Low" | "Medium" | "High" | "Critical";

const RISK_CONFIG: Record<
  RiskLevel,
  { icon: React.ComponentType<{ className?: string }>; text: string; bg: string; border: string; bar: string }
> = {
  Low: { icon: Circle, text: "text-risk-low", bg: "bg-risk-low-bg", border: "border-risk-low-border", bar: "bg-risk-low" },
  Medium: { icon: Triangle, text: "text-risk-medium", bg: "bg-risk-medium-bg", border: "border-risk-medium-border", bar: "bg-risk-medium" },
  High: { icon: TriangleAlert, text: "text-risk-high", bg: "bg-risk-high-bg", border: "border-risk-high-border", bar: "bg-risk-high" },
  Critical: { icon: Diamond, text: "text-risk-critical", bg: "bg-risk-critical-bg", border: "border-risk-critical-border", bar: "bg-risk-critical" },
};

/**
 * Risk is communicated through three independent channels at once:
 * a distinct icon shape, the word itself, and an accent color/bar.
 * Any one channel alone is sufficient for a color-independent or
 * low-vision reading, satisfying "risk must not rely on color alone"
 * without depending on hue recognition at all.
 */
export function RiskChip({ risk, className }: { risk: RiskLevel; className?: string }) {
  const config = RISK_CONFIG[risk];
  const Icon = config.icon;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-atlas-sm border px-2 py-0.5 text-xs font-semibold",
        config.text,
        config.bg,
        config.border,
        className
      )}
    >
      <Icon className={cn("size-3", risk === "Critical" && "fill-current")} aria-hidden="true" />
      {risk}
    </span>
  );
}

/** A 3px accent bar for row/card leading edges. Purely supplementary
 * to the RiskChip's icon+text; never the only risk signal on screen. */
export function RiskBar({ risk, className }: { risk: RiskLevel; className?: string }) {
  return <span aria-hidden="true" className={cn("absolute inset-y-0 left-0 w-[3px]", RISK_CONFIG[risk].bar, className)} />;
}

export function riskRank(risk: RiskLevel) {
  return { Low: 0, Medium: 1, High: 2, Critical: 3 }[risk];
}
