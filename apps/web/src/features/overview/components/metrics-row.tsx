import type { LucideIcon } from "lucide-react";
import { Bot, Play, ShieldCheck, TriangleAlert } from "lucide-react";
import { cn } from "@/lib/utils";
import { FLEET_PULSE } from "@/components/layout/nav-items";

interface Pulse {
  label: string;
  value: number;
  icon: LucideIcon;
  tone: "default" | "brand" | "warning" | "error";
  href: string;
}

const TONE_CLASS: Record<Pulse["tone"], string> = {
  default: "text-foreground-secondary",
  brand: "text-brand",
  warning: "text-warning",
  error: "text-error",
};

/**
 * Replaces the baseline's four large metric cards (each ~oversized
 * relative to the number it holds) with one compact strip of small
 * multiples. The Fleet Pulse status bar already repeats total/running
 * counts on every screen, so Overview's version adds the two counts
 * that only make sense here: agents needing attention, and today's
 * pending-approval total with a direct link into the queue.
 */
export function MetricsRow() {
  const attention = FLEET_PULSE.degradedAgents + FLEET_PULSE.offlineAgents;
  const items: Pulse[] = [
    { label: "Agents in fleet", value: FLEET_PULSE.totalAgents, icon: Bot, tone: "default", href: "/agents" },
    { label: "Running now", value: FLEET_PULSE.runningAgents, icon: Play, tone: "brand", href: "/agents" },
    { label: "Need attention", value: attention, icon: TriangleAlert, tone: attention > 0 ? "warning" : "default", href: "/agents" },
    { label: "Pending approvals", value: FLEET_PULSE.pendingApprovals, icon: ShieldCheck, tone: FLEET_PULSE.pendingApprovals > 0 ? "warning" : "default", href: "/approvals" },
  ];

  return (
    <div className="grid grid-cols-2 gap-px overflow-hidden rounded-atlas-md border border-border-default bg-border-default sm:grid-cols-4">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <a
            key={item.label}
            href={item.href}
            className="flex items-center gap-3 bg-surface px-4 py-3.5 transition-colors hover:bg-surface-hover"
          >
            <Icon className={cn("size-4 shrink-0", TONE_CLASS[item.tone])} aria-hidden="true" />
            <div className="min-w-0">
              <p className={cn("font-mono text-xl font-semibold leading-none tabular-nums", TONE_CLASS[item.tone])}>{item.value}</p>
              <p className="mt-1 truncate text-[11px] text-foreground-secondary">{item.label}</p>
            </div>
          </a>
        );
      })}
    </div>
  );
}
