"use client";

import Link from "next/link";
import { Boxes, ShieldCheck } from "lucide-react";
import { FLEET_PULSE } from "./nav-items";
import { cn } from "@/lib/utils";

/**
 * Persistent operator status strip. This is the exploration's central
 * structural departure from the baseline shell: instead of situational
 * awareness living only on the Overview page, a compact fleet pulse is
 * visible on every screen, all the time, satisfying Atlas's own
 * "Operational Clarity" principle ("users should immediately understand
 * current state") regardless of which object an operator is currently
 * inspecting.
 *
 * Each figure is a real link to the screen that explains it, and pairs
 * a numeral with a short label so it reads correctly without color.
 */
function PulseItem({ href, tone, label, value }: { href: string; tone: "neutral" | "warning" | "error" | "brand"; label: string; value: number }) {
  const toneClass = {
    neutral: "text-foreground-secondary",
    warning: "text-warning",
    error: "text-error",
    brand: "text-brand",
  }[tone];
  return (
    <Link
      href={href}
      className="flex items-center gap-1.5 rounded-atlas-sm px-1.5 py-0.5 text-xs hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus-ring"
    >
      <span className={cn("font-mono text-[13px] font-semibold tabular-nums", toneClass)}>{value}</span>
      <span className="hidden text-foreground-secondary sm:inline">{label}</span>
    </Link>
  );
}

export function StatusBar() {
  return (
    <div
      className="sticky top-0 z-30 flex h-(--statusbar-height) items-center gap-4 border-b border-border-default bg-surface-secondary px-3 text-xs sm:px-4"
      role="region"
      aria-label="Fleet pulse"
    >
      <div className="flex shrink-0 items-center gap-1.5">
        <span className="flex size-5 items-center justify-center rounded-atlas-sm bg-brand-solid text-foreground-on-brand">
          <Boxes className="size-3" aria-hidden="true" />
        </span>
        <span className="font-mono text-[11px] font-semibold uppercase tracking-[0.12em] text-foreground">Atlas</span>
      </div>
      <div className="h-4 w-px shrink-0 bg-border-default" aria-hidden="true" />
      <div className="flex flex-1 items-center gap-1 overflow-x-auto">
        <PulseItem href="/agents" tone="neutral" label="agents" value={FLEET_PULSE.totalAgents} />
        <PulseItem href="/agents" tone="brand" label="running" value={FLEET_PULSE.runningAgents} />
        {FLEET_PULSE.degradedAgents + FLEET_PULSE.offlineAgents > 0 && (
          <PulseItem href="/agents" tone="warning" label="need attention" value={FLEET_PULSE.degradedAgents + FLEET_PULSE.offlineAgents} />
        )}
        <PulseItem href="/approvals" tone={FLEET_PULSE.pendingApprovals > 0 ? "warning" : "neutral"} label="pending approvals" value={FLEET_PULSE.pendingApprovals} />
        <PulseItem href="/alerts" tone={FLEET_PULSE.activeAlerts > 0 ? "error" : "neutral"} label="active alerts" value={FLEET_PULSE.activeAlerts} />
      </div>
      <div className="hidden shrink-0 items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-foreground-tertiary md:flex">
        <ShieldCheck className="size-3" aria-hidden="true" />
        Frontend prototype
      </div>
    </div>
  );
}
