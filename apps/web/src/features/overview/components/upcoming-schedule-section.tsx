import { CalendarClock, CalendarX2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/state/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import type { ScheduleItem } from "../types/overview.types";

export interface UpcomingScheduleSectionProps {
  items: ScheduleItem[];
  state?: "success" | "loading" | "empty";
}

export function UpcomingScheduleSection({ items, state = "success" }: UpcomingScheduleSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Upcoming Schedule</CardTitle>
        <CardDescription>Next scheduled agent activity</CardDescription>
      </CardHeader>

      {state === "loading" && (
        <CardContent className="flex flex-col gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </CardContent>
      )}

      {state === "empty" && (
        <EmptyState
          icon={CalendarX2}
          title="Nothing scheduled"
          description="Scheduled runs will appear here."
        />
      )}

      {state === "success" && (
        <CardContent className="flex flex-col gap-1">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex items-center gap-3 rounded-atlas-md px-2 py-2.5 -mx-2 transition-colors hover:bg-surface-hover"
            >
              <div className="flex size-8 shrink-0 items-center justify-center rounded-atlas-md bg-brand-subtle text-brand">
                <CalendarClock className="size-4" aria-hidden="true" />
              </div>
              <div className="flex min-w-0 flex-1 flex-col">
                <span className="truncate text-sm font-medium text-foreground">{item.task}</span>
                <span className="text-xs text-foreground-secondary">{item.agentName}</span>
              </div>
              <div className="flex shrink-0 flex-col items-end gap-1">
                <span className="font-mono text-xs text-foreground">{item.time}</span>
                <Badge variant="neutral">{item.cadence}</Badge>
              </div>
            </div>
          ))}
        </CardContent>
      )}
    </Card>
  );
}
