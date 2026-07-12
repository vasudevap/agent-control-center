import { BellOff } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { AlertCard } from "@/components/cards/alert-card";
import { EmptyState } from "@/components/state/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import type { AlertItem } from "../types/overview.types";

export interface AlertsSectionProps {
  alerts: AlertItem[];
  state?: "success" | "loading" | "empty";
}

export function AlertsSection({ alerts, state = "success" }: AlertsSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Alerts</CardTitle>
        <CardDescription>Critical, warning, and informational events</CardDescription>
      </CardHeader>

      {state === "loading" && (
        <CardContent className="flex flex-col gap-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      )}

      {state === "empty" && (
        <EmptyState
          icon={BellOff}
          title="No alerts"
          description="You're all caught up. New alerts will appear here."
        />
      )}

      {state === "success" && (
        <CardContent className="flex flex-col gap-2">
          {alerts.map((alert) => (
            <AlertCard
              key={alert.id}
              severity={alert.severity}
              title={alert.title}
              description={alert.description}
              timestamp={alert.timestamp}
              source={alert.source}
            />
          ))}
        </CardContent>
      )}
    </Card>
  );
}
