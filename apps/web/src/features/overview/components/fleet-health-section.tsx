import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { StatusBadge } from "@/components/badge/status-badge";
import { STATUS_LABELS, type AgentRecord } from "@/app/(shell)/agents/agent-data";

/**
 * Reads MOCK_AGENTS directly rather than a separately authored Fleet
 * Health fixture, so this table can never list a different roster
 * than /agents does.
 */
export function FleetHealthSection({ agents }: { agents: AgentRecord[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Fleet roster</CardTitle>
        <CardDescription>Every agent in the current fleet, by name</CardDescription>
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
            <TableRow key={agent.id}>
              <TableCell className="font-medium">
                <Link href={`/agents/${agent.id}`} className="hover:text-brand hover:underline">
                  {agent.name}
                </Link>
              </TableCell>
              <TableCell>
                <StatusBadge status={agent.health} />
              </TableCell>
              <TableCell className="text-foreground-secondary">{STATUS_LABELS[agent.status]}</TableCell>
              <TableCell className="hidden font-mono text-xs text-foreground-secondary md:table-cell">{agent.lastRun}</TableCell>
              <TableCell className="hidden font-mono text-xs text-foreground-secondary md:table-cell">{agent.nextRun}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}
