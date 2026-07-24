"use client";

import * as React from "react";
import { PageHeader } from "@/components/layout/page-header";
import { LayoutDashboard } from "lucide-react";
import { AttentionQueue } from "./attention-queue";
import { ActiveRunsSection } from "./active-runs-section";
import { MOCK_AGENTS } from "@/app/(shell)/agents/agent-data";
import { mockAlerts } from "../data/mock-data";
import { Card } from "@/components/ui/card";
import { ErrorState } from "@/components/state/error-state";
import { EmptyState } from "@/components/state/empty-state";
import { SignedOutState } from "@/components/state/signed-out-state";
import { Skeleton } from "@/components/ui/skeleton";
import {
  dashboardApiBaseUrl,
  readDashboardAgents,
  readDashboardAlerts,
  readDashboardRuns,
  readDashboardSessionOrRequireSignIn,
  toAgentRecords,
  toAlertRecords,
  type DashboardRuntimeMode,
} from "@/lib/dashboard-runtime";

export function OverviewDashboard({ runtimeRequired = false }: { runtimeRequired?: boolean }) {
  const [runtimeMode, setRuntimeMode] =
    React.useState<DashboardRuntimeMode>(() =>
      runtimeRequired ? (dashboardApiBaseUrl() ? "loading" : "error") : "fixture",
    );
  const [agents, setAgents] = React.useState(MOCK_AGENTS);
  const [alerts, setAlerts] = React.useState(mockAlerts);

  React.useEffect(() => {
    let cancelled = false;
    async function loadRuntime() {
      if (!dashboardApiBaseUrl()) {
        setRuntimeMode(runtimeRequired ? "error" : "fixture");
        return;
      }
      setRuntimeMode("loading");
      try {
        await readDashboardSessionOrRequireSignIn();
        const [runtimeAgents, runtimeRuns, runtimeAlerts] =
          await Promise.all([
            readDashboardAgents(),
            readDashboardRuns(),
            readDashboardAlerts(),
          ]);
        if (!cancelled) {
          setAgents(toAgentRecords(runtimeAgents, runtimeRuns));
          setAlerts(toAlertRecords(runtimeAlerts));
          setRuntimeMode("live");
        }
      } catch (error) {
        if (cancelled) return;
        if (
          error instanceof Error &&
          "status" in error &&
          (error as { status: number }).status === 401
        ) {
          setRuntimeMode("unauthenticated");
        } else {
          setRuntimeMode("error");
        }
      }
    }
    void loadRuntime();
    return () => {
      cancelled = true;
    };
  }, [runtimeRequired]);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Control plane"
        title="Overview"
        icon={LayoutDashboard}
        description={
          runtimeMode === "live"
            ? "What requires attention across the owner-authenticated Atlas runtime right now."
            : "What requires attention across your AI workforce right now."
        }
      />

      {runtimeMode === "live" ? (
        <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
          <strong>Live runtime.</strong> Overview data is loaded from
          owner-authenticated agent, execution, and alert APIs.
        </div>
      ) : runtimeMode === "loading" ? (
        <div className="grid gap-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-72 w-full" />
        </div>
      ) : runtimeMode === "unauthenticated" ? (
        <SignedOutState description="Sign in to load runtime overview data from the Atlas API." />
      ) : runtimeMode === "error" ? (
        <Card>
          <ErrorState
            title="Overview data is unavailable"
            description={
              runtimeRequired && !dashboardApiBaseUrl()
                ? "No runtime API base URL is configured for this build, so the live overview cannot be displayed."
                : "The owner-authenticated Atlas APIs could not return live overview data."
            }
            className="py-12"
          />
        </Card>
      ) : null}

      {runtimeMode === "live" && agents.length === 0 ? (
        <Card>
          <EmptyState
            icon={LayoutDashboard}
            title="Nothing to display yet"
            description="No agents have been enrolled, so there is no activity, execution history, or alert data to show."
            className="py-16"
          />
        </Card>
      ) : runtimeMode !== "loading" && runtimeMode !== "unauthenticated" && runtimeMode !== "error" && (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="min-w-0 flex flex-col gap-6 xl:col-span-2">
          <AttentionQueue agents={agents} alerts={alerts} />
        </div>

        <div className="min-w-0 flex flex-col gap-6">
          <ActiveRunsSection agents={agents} />
        </div>
      </div>
      )}
    </div>
  );
}
