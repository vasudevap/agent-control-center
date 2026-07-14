import { CalendarClock, CalendarOff } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/state/empty-state";
import type { AgentRecord } from "@/app/(shell)/agents/agent-data";

/** Derived from MOCK_AGENTS.nextRun; agents with no scheduled next run are excluded. */
export function UpcomingScheduleSection({ agents }: { agents: AgentRecord[] }) {
  const scheduled = agents.filter((agent) => agent.nextRun !== "Not scheduled" && agent.nextRun !== "Paused");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upcoming schedule</CardTitle>
        <CardDescription>Next scheduled run per agent</CardDescription>
      </CardHeader>
      {scheduled.length === 0 ? (
        <EmptyState icon={CalendarOff} title="Nothing scheduled" description="No agents have an upcoming scheduled run." className="py-10" />
      ) : (
        <CardContent className="grid gap-2">
          {scheduled.map((agent) => (
            <div key={agent.id} className="flex items-center gap-3 overflow-hidden rounded-atlas-sm border border-border-default bg-surface-secondary px-3 py-2.5">
              <CalendarClock className="size-4 shrink-0 text-foreground-tertiary" aria-hidden="true" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-foreground">{agent.name}</p>
                <p className="truncate text-xs text-foreground-secondary">{agent.description}</p>
              </div>
              <span className="shrink-0 font-mono text-xs text-foreground-secondary">{agent.nextRun}</span>
            </div>
          ))}
        </CardContent>
      )}
    </Card>
  );
}
