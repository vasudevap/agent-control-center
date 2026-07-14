"use client";

import * as React from "react";
import Link from "next/link";
import { AlertTriangle, Bot, CircleOff, FilterX } from "lucide-react";
import {
  HEALTH_LABELS,
  MOCK_AGENTS,
  STATUS_LABELS,
  STATUS_VARIANTS,
  type AgentHealth,
  type AgentRecord,
  type AgentStatus,
} from "./agent-data";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/state/empty-state";
import { StatusBadge } from "@/components/badge/status-badge";
import { ErrorState } from "@/components/state/error-state";
import { Badge, type BadgeProps } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SearchField } from "@/components/ui/search-field";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export type { AgentRecord } from "./agent-data";

type InventoryState = "loaded" | "loading" | "error";

interface AgentsInventoryProps {
  agents?: AgentRecord[];
  state?: InventoryState;
}

function getAttentionRank(agent: AgentRecord) {
  if (agent.currentIssue) return 0;
  if (agent.health === "degraded" || agent.health === "offline") return 1;
  if (agent.status === "running") return 2;
  return 3;
}

function orderAgentsByAttention(agents: AgentRecord[]) {
  return [...agents].sort((a, b) => getAttentionRank(a) - getAttentionRank(b) || a.name.localeCompare(b.name));
}

function filterAgents(agents: AgentRecord[], query: string, status: AgentStatus | "all", health: AgentHealth | "all") {
  const q = query.trim().toLowerCase();
  return orderAgentsByAttention(agents).filter((agent) => {
    const matchesQuery = !q || agent.name.toLowerCase().includes(q) || agent.description.toLowerCase().includes(q) || agent.id.toLowerCase().includes(q);
    return matchesQuery && (status === "all" || agent.status === status) && (health === "all" || agent.health === health);
  });
}

function AgentBadge({ label, variant }: { label: string; variant: BadgeProps["variant"] }) {
  return <Badge variant={variant}>{label}</Badge>;
}

function FieldPair({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="font-mono text-[10px] font-medium uppercase tracking-wider text-foreground-tertiary">{label}</dt>
      <dd className="text-sm text-foreground">{value}</dd>
    </div>
  );
}

function AgentIdentity({ agent }: { agent: AgentRecord }) {
  const issueLabel = agent.issueSummary ?? agent.currentIssue;
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <Link href={`/agents/${agent.id}`} className="relative z-10 w-fit font-medium text-foreground underline-offset-4 after:absolute after:inset-0 after:content-[''] hover:text-brand hover:underline">
        {agent.name}
      </Link>
      <p className="max-w-md truncate text-xs text-foreground-secondary">{agent.description}</p>
      {issueLabel && (
        <p className="mt-0.5 flex items-center gap-1.5 text-xs text-warning">
          <AlertTriangle className="size-3.5 shrink-0" aria-hidden="true" />
          <span className="truncate">{issueLabel}</span>
        </p>
      )}
    </div>
  );
}

function AgentsTable({ agents }: { agents: AgentRecord[] }) {
  return (
    <Card className="hidden overflow-hidden md:block">
      <Table>
        <caption className="sr-only">Agents inventory</caption>
        <TableHeader>
          <TableRow>
            <TableHead>Agent</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Health</TableHead>
            <TableHead className="hidden lg:table-cell">Owner</TableHead>
            <TableHead>Last run</TableHead>
            <TableHead>Next run</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {agents.map((agent) => (
            <TableRow key={agent.id} className="relative">
              <TableCell className="min-w-[18rem] py-2.5"><AgentIdentity agent={agent} /></TableCell>
              <TableCell className="py-2.5"><AgentBadge label={STATUS_LABELS[agent.status]} variant={STATUS_VARIANTS[agent.status]} /></TableCell>
              <TableCell className="py-2.5"><StatusBadge status={agent.health} /></TableCell>
              <TableCell className="hidden py-2.5 text-sm text-foreground-secondary lg:table-cell">{agent.owner}</TableCell>
              <TableCell className="py-2.5 text-xs text-foreground-secondary">{agent.lastRun}</TableCell>
              <TableCell className="py-2.5 text-xs text-foreground-secondary">{agent.nextRun}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}

function MobileAgentsList({ agents }: { agents: AgentRecord[] }) {
  return (
    <div className="grid gap-2.5 md:hidden" aria-label="Agents inventory summaries">
      {agents.map((agent) => (
        <Link key={agent.id} href={`/agents/${agent.id}`} className="block rounded-atlas-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus-ring" aria-label={`${agent.name} details`}>
          <Card className="transition-colors hover:bg-surface-hover">
            <CardContent className="flex flex-col gap-3 p-4">
              <h2 className="text-sm font-semibold text-foreground">{agent.name}</h2>
              <dl className="grid grid-cols-2 gap-3">
                <FieldPair label="Status" value={<AgentBadge label={STATUS_LABELS[agent.status]} variant={STATUS_VARIANTS[agent.status]} />} />
                <FieldPair label="Health" value={<StatusBadge status={agent.health} />} />
                <FieldPair label="Last run" value={agent.lastRun} />
                <FieldPair label="Next run" value={agent.nextRun} />
              </dl>
              {(agent.issueSummary ?? agent.currentIssue) && (
                <div className="rounded-atlas-sm border border-warning-border bg-warning-bg px-3 py-2 text-xs leading-relaxed text-warning">
                  {agent.issueSummary ?? agent.currentIssue}
                </div>
              )}
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}

function InventorySkeleton() {
  return (
    <div className="flex flex-col gap-4" aria-label="Loading agents inventory">
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_12rem_12rem_auto]">
        <Skeleton className="h-9" /><Skeleton className="h-9" /><Skeleton className="h-9" /><Skeleton className="h-9" />
      </div>
      <Card className="hidden p-4 md:block">
        <div className="flex flex-col gap-3">
          {Array.from({ length: 5 }).map((_, index) => <Skeleton key={index} className="h-12" />)}
        </div>
      </Card>
    </div>
  );
}

export function AgentsInventory({ agents = MOCK_AGENTS, state = "loaded" }: AgentsInventoryProps) {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState<AgentStatus | "all">("all");
  const [healthFilter, setHealthFilter] = React.useState<AgentHealth | "all">("all");

  const hasActiveFilters = searchQuery.trim() !== "" || statusFilter !== "all" || healthFilter !== "all";
  const filteredAgents = filterAgents(agents, searchQuery, statusFilter, healthFilter);
  const clearFilters = () => { setSearchQuery(""); setStatusFilter("all"); setHealthFilter("all"); };

  return (
    <div className="flex flex-col gap-6">
      <PageHeader eyebrow="Fleet" title="Agents" icon={Bot} description="Monitor the status, health, and activity of your AI workforce." meta={<span className="font-mono text-[11px] text-foreground-tertiary">{agents.length} registered</span>} />

      {state === "loading" && <InventorySkeleton />}

      {state === "error" && (
        <Card>
          <ErrorState title="Agents inventory could not be displayed" description="The local inventory state is unavailable. No agent operation was started." className="py-16" />
        </Card>
      )}

      {state === "loaded" && agents.length > 0 && (
        <section className="flex flex-col gap-3" aria-labelledby="agents-inventory-heading">
          <div className="flex flex-col gap-3 rounded-atlas-md border border-border-default bg-surface-secondary p-3.5">
            <div className="flex items-center justify-between">
              <h2 id="agents-inventory-heading" className="text-xs font-semibold uppercase tracking-wide text-foreground-secondary">
                Showing {filteredAgents.length} of {agents.length}
              </h2>
              {hasActiveFilters && (
                <Button type="button" variant="ghost" size="sm" onClick={clearFilters}>
                  <FilterX aria-hidden="true" />
                  Clear
                </Button>
              )}
            </div>
            <div className="grid gap-2.5 lg:grid-cols-[minmax(0,1fr)_12rem_12rem]">
              <SearchField id="agent-search" value={searchQuery} onChange={setSearchQuery} placeholder="Search name, description, or ID" aria-label="Search agents by name, description, or ID" />
              <select id="agent-status-filter" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as AgentStatus | "all")} aria-label="Filter by status" className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none transition-colors hover:border-border-strong focus:border-brand">
                <option value="all">All statuses</option>
                {Object.entries(STATUS_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
              <select id="agent-health-filter" value={healthFilter} onChange={(e) => setHealthFilter(e.target.value as AgentHealth | "all")} aria-label="Filter by health" className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none transition-colors hover:border-border-strong focus:border-brand">
                <option value="all">All health states</option>
                {Object.entries(HEALTH_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </div>
          </div>

          {filteredAgents.length > 0 ? (
            <>
              <AgentsTable agents={filteredAgents} />
              <MobileAgentsList agents={filteredAgents} />
            </>
          ) : (
            <Card>
              <EmptyState icon={CircleOff} title="No agents match the current search or filters" description="Adjust the criteria or clear filters to restore the full inventory." action={<Button type="button" variant="secondary" size="sm" onClick={clearFilters}>Clear filters</Button>} className="py-16" />
            </Card>
          )}
        </section>
      )}
    </div>
  );
}
