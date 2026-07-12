"use client";

import { useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { MetricsRow } from "./metrics-row";
import { FleetHealthSection } from "./fleet-health-section";
import { ActiveRunsSection } from "./active-runs-section";
import { PendingApprovalsSection } from "./pending-approvals-section";
import { AlertsSection } from "./alerts-section";
import { UpcomingScheduleSection } from "./upcoming-schedule-section";
import {
  mockMetrics,
  mockFleetHealth,
  mockActiveRuns,
  mockPendingApprovals,
  mockAlerts,
  mockSchedule,
} from "../data/mock-data";

export function OverviewDashboard() {
  const [approvals, setApprovals] = useState(mockPendingApprovals);

  function handleDecision(id: string) {
    setApprovals((prev) => prev.filter((approval) => approval.id !== id));
  }

  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        title="Overview"
        description="Fleet-wide status for your AI workforce"
        actions={
          <Button variant="secondary" size="sm">
            <RefreshCw className="size-3.5" />
            Refresh
          </Button>
        }
      />

      <MetricsRow
        metrics={{ ...mockMetrics, pendingApprovals: approvals.length }}
      />

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-3">
        <div className="flex flex-col gap-8 xl:col-span-2">
          <FleetHealthSection agents={mockFleetHealth} />
          <ActiveRunsSection runs={mockActiveRuns} />
        </div>

        <div className="flex flex-col gap-8">
          <PendingApprovalsSection
            approvals={approvals}
            state={approvals.length === 0 ? "empty" : "success"}
            onDecision={handleDecision}
          />
          <AlertsSection alerts={mockAlerts} />
          <UpcomingScheduleSection items={mockSchedule} />
        </div>
      </div>
    </div>
  );
}
