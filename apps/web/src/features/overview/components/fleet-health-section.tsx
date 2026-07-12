import { ServerCog } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { StatusBadge } from "@/components/badge/status-badge";
import { EmptyState } from "@/components/state/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import type { FleetAgentRow } from "../types/overview.types";

export interface FleetHealthSectionProps {
  agents: FleetAgentRow[];
  state?: "success" | "loading" | "empty";
}

export function FleetHealthSection({ agents, state = "success" }: FleetHealthSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Fleet Health</CardTitle>
        <CardDescription>Live status across every deployed agent</CardDescription>
      </CardHeader>

      {state === "loading" && (
        <div className="flex flex-col gap-3 px-4 pb-6 sm:px-6">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      )}

      {state === "empty" && (
        <EmptyState
          icon={ServerCog}
          title="No agents deployed"
          description="Deploy your first agent to see fleet health here."
        />
      )}

      {state === "success" && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Agent</TableHead>
              <TableHead>Health</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Last run</TableHead>
              <TableHead>Next run</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {agents.map((agent) => (
              <TableRow key={agent.id}>
                <TableCell className="font-medium">{agent.name}</TableCell>
                <TableCell>
                  <StatusBadge status={agent.health} />
                </TableCell>
                <TableCell className="text-foreground-secondary">{agent.status}</TableCell>
                <TableCell className="font-mono text-xs text-foreground-secondary">
                  {agent.lastRun}
                </TableCell>
                <TableCell className="font-mono text-xs text-foreground-secondary">
                  {agent.nextRun}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Card>
  );
}
