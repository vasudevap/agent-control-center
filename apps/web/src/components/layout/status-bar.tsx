"use client";

import Link from "next/link";
import { FLEET_PULSE } from "./nav-items";
import { RuntimeHealthIndicator } from "./runtime-health-indicator";
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
 *
 * The logo/app-name now lives in the Sidebar itself (see sidebar.tsx),
 * not here. Sizing this strip to independently match the sidebar's
 * width was solving the wrong problem — the actual fix is that this
 * strip only ever renders in the content column next to the sidebar
 * (see dashboard-layout.tsx), so there is no seam to keep aligned in
 * the first place.
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
      className="flex items-center gap-1.5 rounded-atlas-sm px-1.5 py-0.5 text-xs hover:bg-surface-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus-ring"
    >
      <span className={cn("font-mono text-[13px] font-semibold tabular-nums", toneClass)}>{value}</span>
      <span className="hidden text-foreground-secondary sm:inline">{label}</span>
    </Link>
  );
}

/** A quiet vertical rule between destination clusters, so grouping reads
 * as "these numbers behave the same way" rather than one undifferentiated row. */
function ClusterDivider() {
  return <span className="h-4 w-px shrink-0 bg-border-default" aria-hidden="true" />;
}

export function StatusBar() {
  const needsAttention = FLEET_PULSE.degradedAgents + FLEET_PULSE.offlineAgents;

  return (
    <div
      className="sticky top-0 z-30 flex h-(--statusbar-height) items-center gap-2.5 border-b border-border-default bg-surface-secondary px-3 text-xs sm:px-4"
      role="region"
      aria-label="Fleet pulse"
    >
      <div className="flex flex-1 items-center gap-2.5 overflow-x-auto">
        <div className="flex items-center gap-1">
          <PulseItem href="/agents" tone="neutral" label="agents" value={FLEET_PULSE.totalAgents} />
          <PulseItem href="/agents" tone="brand" label="running" value={FLEET_PULSE.runningAgents} />
          {needsAttention > 0 && <PulseItem href="/agents" tone="warning" label="need attention" value={needsAttention} />}
        </div>
        <ClusterDivider />
        <PulseItem href="/approvals" tone={FLEET_PULSE.pendingApprovals > 0 ? "warning" : "neutral"} label="pending approvals" value={FLEET_PULSE.pendingApprovals} />
        <ClusterDivider />
        <PulseItem href="/alerts" tone={FLEET_PULSE.activeAlerts > 0 ? "error" : "neutral"} label="active alerts" value={FLEET_PULSE.activeAlerts} />
      </div>
      <RuntimeHealthIndicator />
    </div>
  );
}
