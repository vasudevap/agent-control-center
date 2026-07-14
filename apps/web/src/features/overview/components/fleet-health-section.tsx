import Link from "next/link";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { StatusBadge } from "@/components/badge/status-badge";
import { STATUS_LABELS, type AgentRecord } from "@/app/(shell)/agents/agent-data";

/**
 * Reads MOCK_AGENTS directly rather than a separately authored Fleet
 * Health fixture, so this table can never list a different roster
 * than /agents does.
 *
 * This is a roster you drill into, not a status you only read, so the
 * whole row routes to Agent Detail (not just the name), the header
 * gets the same shaded "actionable" treatment as Attention Queue, and
 * the health column matches that card's icon-only convention with a
 * legend in the same header slot. The "stretched link" on the name
 * anchor gives the whole row a click target while keeping exactly one
 * accessible link per row, the same one a screen reader already
 * announced before this change — just with a larger hit area.
 */
export function FleetHealthSection({ agents }: { agents: AgentRecord[] }) {
  return (
    <Card>
      <CardHeader actionable className="flex-row items-start justify-between gap-3 space-y-0">
        <div>
          <CardTitle>Fleet roster</CardTitle>
          <CardDescription>Every agent in the current fleet, by name</CardDescription>
        </div>
        <div className="hidden items-center gap-2.5 text-[10px] text-foreground-tertiary sm:flex">
          <span className="flex items-center gap-1"><CheckCircle2 className="size-3 text-success" aria-hidden="true" />Healthy</span>
          <span className="flex items-center gap-1"><AlertTriangle className="size-3 text-warning" aria-hidden="true" />Degraded</span>
          <span className="flex items-center gap-1"><XCircle className="size-3 text-error" aria-hidden="true" />Offline</span>
        </div>
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Agent</TableHead>
            <TableHead>Health</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="hidden md:table-cell">Last run</TableHead>
            <TableHead className="hidden md:table-cell">Next run</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {agents.map((agent) => (
            <TableRow key={agent.id} className="relative">
              <TableCell className="font-medium">
                <Link
                  href={`/agents/${agent.id}`}
                  className="relative z-10 after:absolute after:inset-0 after:content-[''] hover:text-brand hover:underline"
                >
                  {agent.name}
                </Link>
              </TableCell>
              <TableCell>
                <StatusBadge status={agent.health} iconOnly />
              </TableCell>
              <TableCell className="text-foreground-secondary">{STATUS_LABELS[agent.status]}</TableCell>
              <TableCell className="hidden text-xs text-foreground-secondary md:table-cell">{agent.lastRun}</TableCell>
              <TableCell className="hidden text-xs text-foreground-secondary md:table-cell">{agent.nextRun}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}
