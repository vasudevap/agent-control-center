"use client";

import Link from "next/link";
import * as React from "react";
import { RuntimeHealthIndicator } from "./runtime-health-indicator";
import { cn } from "@/lib/utils";
import {
  dashboardApiBaseUrl,
  fleetPulseFromRuntime,
  readDashboardAgents,
  readDashboardAlerts,
  readDashboardRuns,
  readDashboardSession,
  toAgentRecords,
  toAlertRecords,
} from "@/lib/dashboard-runtime";
import { CONTROL_CENTER_ROUTES } from "@/lib/control-center-routes";

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
  const apiBaseUrl = dashboardApiBaseUrl();
  const [pulse, setPulse] = React.useState(() =>
    fleetPulseFromRuntime([], [], []),
  );
  const [state, setState] = React.useState<"unconfigured" | "loading" | "live" | "unavailable">(
    "unconfigured",
  );

  React.useEffect(() => {
    let cancelled = false;
    async function loadRuntime() {
      if (!dashboardApiBaseUrl()) {
        setState("unconfigured");
        return;
      }
      setState("loading");
      try {
        await readDashboardSession();
        const [runtimeAgents, runtimeRuns, runtimeAlerts] =
          await Promise.all([
            readDashboardAgents(),
            readDashboardRuns(),
            readDashboardAlerts(),
          ]);
        if (!cancelled) {
          setPulse(
            fleetPulseFromRuntime(
              toAgentRecords(runtimeAgents, runtimeRuns),
              [],
              toAlertRecords(runtimeAlerts),
            ),
          );
          setState("live");
        }
      } catch {
        if (!cancelled) setState("unavailable");
      }
    }
    void loadRuntime();
    return () => {
      cancelled = true;
    };
  }, []);

  const needsAttention = pulse.degradedAgents + pulse.offlineAgents;

  return (
    <div
      className="sticky top-0 z-30 flex h-(--statusbar-height) items-center gap-2.5 border-b border-border-default bg-surface-secondary px-3 text-xs sm:px-4"
      role="region"
      aria-label="Fleet pulse"
    >
      <div className="flex flex-1 items-center gap-2.5 overflow-x-auto">
        <div className="flex items-center gap-1">
          <PulseItem href={CONTROL_CENTER_ROUTES.agents} tone="neutral" label="agents" value={pulse.totalAgents} />
          <PulseItem href={CONTROL_CENTER_ROUTES.agents} tone="brand" label="running" value={pulse.runningAgents} />
          {needsAttention > 0 && <PulseItem href={CONTROL_CENTER_ROUTES.agents} tone="warning" label="need attention" value={needsAttention} />}
        </div>
        <ClusterDivider />
        <PulseItem href={CONTROL_CENTER_ROUTES.alerts} tone={pulse.activeAlerts > 0 ? "error" : "neutral"} label="active alerts" value={pulse.activeAlerts} />
        {state === "loading" && (
          <span className="shrink-0 text-[11px] text-foreground-tertiary">
            Loading live metrics...
          </span>
        )}
        {state === "unavailable" && (
          <span className="shrink-0 text-[11px] text-warning">
            Live metrics unavailable
          </span>
        )}
        {state === "unconfigured" && (
          <span className="shrink-0 text-[11px] text-foreground-tertiary">
            Live metrics not configured
          </span>
        )}
      </div>
      <RuntimeHealthIndicator apiBaseUrl={apiBaseUrl} />
    </div>
  );
}
