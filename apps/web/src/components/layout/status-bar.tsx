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
 *
 * The logo block below is sized to `--sidebar-width`, the exact same
 * variable the Sidebar itself reads, at the same `lg:` breakpoint
 * where the sidebar becomes a persistent rail. That keeps the vertical
 * divider directly under this strip continuous with the sidebar/content
 * boundary, rather than two independently-sized widths that only
 * happen to line up by coincidence. Below `lg`, where the sidebar isn't
 * a persistent rail at all, the logo block reverts to its natural
 * width since there's no boundary to align to.
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

/** A quiet vertical rule between destination clusters, reusing the same
 * divider language already used next to the logo, so grouping reads as
 * "these numbers behave the same way" rather than one undifferentiated row. */
function ClusterDivider() {
  return <span className="h-4 w-px shrink-0 bg-border-default" aria-hidden="true" />;
}

export function StatusBar() {
  const needsAttention = FLEET_PULSE.degradedAgents + FLEET_PULSE.offlineAgents;

  return (
    <div
      className="sticky top-0 z-30 flex h-(--statusbar-height) items-center gap-4 border-b border-border-default bg-surface-secondary px-3 text-xs sm:px-4"
      role="region"
      aria-label="Fleet pulse"
    >
      <div className="flex h-full shrink-0 items-center gap-1.5 lg:w-(--sidebar-width)">
        <span className="flex size-5 items-center justify-center rounded-atlas-sm bg-brand-solid text-foreground-on-brand">
          <Boxes className="size-3" aria-hidden="true" />
        </span>
        <span className="font-mono text-[11px] font-semibold uppercase tracking-[0.12em] text-foreground">Atlas</span>
      </div>
      <div className="h-4 w-px shrink-0 bg-border-default" aria-hidden="true" />
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
      <div className="hidden shrink-0 items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-foreground-tertiary md:flex">
        <ShieldCheck className="size-3" aria-hidden="true" />
        Frontend prototype
      </div>
    </div>
  );
}
