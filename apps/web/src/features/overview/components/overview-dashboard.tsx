import { PageHeader } from "@/components/layout/page-header";
import { LayoutDashboard } from "lucide-react";
import { MetricsRow } from "./metrics-row";
import { AttentionQueue } from "./attention-queue";
import { FleetHealthSection } from "./fleet-health-section";
import { ActiveRunsSection } from "./active-runs-section";
import { UpcomingScheduleSection } from "./upcoming-schedule-section";
import { MOCK_AGENTS } from "@/app/(shell)/agents/agent-data";

export function OverviewDashboard() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader eyebrow="Control plane" title="Overview" icon={LayoutDashboard} description="What requires attention across your AI workforce right now." />

      <MetricsRow />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="min-w-0 flex flex-col gap-6 xl:col-span-2">
          <AttentionQueue />
          <FleetHealthSection agents={MOCK_AGENTS} />
        </div>

        <div className="min-w-0 flex flex-col gap-6">
          <ActiveRunsSection agents={MOCK_AGENTS} />
          <UpcomingScheduleSection agents={MOCK_AGENTS} />
        </div>
      </div>
    </div>
  );
}
