"use client";

import * as React from "react";
import Link from "next/link";
import { FilterX, ShieldCheck } from "lucide-react";
import {
  type PolicyRecord,
  type PolicyStatus,
  type PolicyType,
} from "./policy-data";
import { StatusBadge } from "@/components/badge/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { RiskChip } from "@/components/risk/risk-indicator";
import { EmptyState } from "@/components/state/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SearchField } from "@/components/ui/search-field";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const SELECT_CLASS =
  "h-9 rounded-atlas-md border border-border-default bg-surface px-3 text-sm text-foreground outline-none hover:border-border-strong focus:border-brand";

function PolicyDetails({ policy }: { policy: PolicyRecord }) {
  return (
    <details className="mt-2 whitespace-normal">
      <summary className="w-fit cursor-pointer text-xs font-medium text-brand hover:underline">
        View readable rule summary
      </summary>
      <div className="mt-3 rounded-atlas-md border border-border-subtle bg-surface-secondary p-3 text-xs">
        <ul className="grid gap-2 text-foreground-secondary">
          {policy.ruleSummary.map((rule) => (
            <li key={rule} className="flex gap-2">
              <span aria-hidden="true">•</span>
              <span>{rule}</span>
            </li>
          ))}
        </ul>
        <p className="mt-3 border-t border-border-subtle pt-3 font-medium text-foreground">
          Display summary only. No policy is evaluated or enforced.
        </p>
      </div>
    </details>
  );
}

export function PoliciesWorkspace({ policies }: { policies: PolicyRecord[] }) {
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState<PolicyStatus | "all">("all");
  const [type, setType] = React.useState<PolicyType | "all">("all");
  const [overrides, setOverrides] = React.useState<
    Record<string, PolicyStatus>
  >({});
  const [notice, setNotice] = React.useState("");
  const records = policies.map((policy) => ({
    ...policy,
    status: overrides[policy.id] ?? policy.status,
  }));
  const normalized = query.trim().toLowerCase();
  const visible = records.filter(
    (policy) =>
      (!normalized ||
        [
          policy.id,
          policy.name,
          policy.scope,
          policy.summary,
          ...policy.assignedAgents.map((agent) => agent.name),
        ]
          .join(" ")
          .toLowerCase()
          .includes(normalized)) &&
      (status === "all" || policy.status === status) &&
      (type === "all" || policy.type === type),
  );
  const hasFilters = Boolean(query || status !== "all" || type !== "all");
  const clear = () => {
    setQuery("");
    setStatus("all");
    setType("all");
  };
  const simulateToggle = (policy: PolicyRecord) => {
    const next = policy.status === "active" ? "paused" : "active";
    setOverrides((current) => ({ ...current, [policy.id]: next }));
    setNotice(
      `Simulated ${next === "active" ? "enable" : "disable"} for ${policy.id}. No policy engine was contacted; refresh restores the fixture.`,
    );
  };
  const Assignments = ({ policy }: { policy: PolicyRecord }) =>
    policy.assignedAgents.length ? (
      <ul className="grid gap-1">
        {policy.assignedAgents.map((agent) => (
          <li key={agent.id}>
            <Link
              href={`/agents/${agent.id}`}
              className="relative z-20 text-brand hover:underline"
            >
              {agent.name}
            </Link>
          </li>
        ))}
      </ul>
    ) : (
      <span className="text-foreground-tertiary">
        Workspace-wide declaration
      </span>
    );

  return (
    <div className="flex flex-col gap-5">
      <PageHeader
        eyebrow="Governance"
        title="Policies"
        description="Review fictional policy declarations, scope, and agent assignment."
        icon={ShieldCheck}
      />
      <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
        <strong>Frontend prototype.</strong> Policy summaries are fictional
        declarations only. No rule is evaluated, enforced, authorized, or
        persisted.
      </div>
      <p className="sr-only" aria-live="polite">
        {notice}
      </p>
      <div className="flex flex-col gap-3 rounded-atlas-lg border border-border-default bg-surface p-3 sm:flex-row sm:flex-wrap sm:items-center">
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Search policies"
          className="w-full sm:max-w-sm"
        />
        <label htmlFor="policy-status" className="sr-only">
          Status
        </label>
        <select
          id="policy-status"
          className={SELECT_CLASS}
          value={status}
          onChange={(event) =>
            setStatus(event.target.value as PolicyStatus | "all")
          }
        >
          <option value="all">All statuses</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
        </select>
        <label htmlFor="policy-type" className="sr-only">
          Type
        </label>
        <select
          id="policy-type"
          className={SELECT_CLASS}
          value={type}
          onChange={(event) =>
            setType(event.target.value as PolicyType | "all")
          }
        >
          <option value="all">All types</option>
          {[...new Set(policies.map((policy) => policy.type))].map((value) => (
            <option key={value}>{value}</option>
          ))}
        </select>
        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={clear}>
            <FilterX aria-hidden="true" />
            Clear filters
          </Button>
        )}
        <p className="text-xs text-foreground-secondary sm:ml-auto">
          {visible.length} of {policies.length} fictional policies
        </p>
      </div>
      {visible.length === 0 ? (
        <Card>
          <EmptyState
            icon={ShieldCheck}
            title="No policies match these filters"
            description="Clear filters to restore the fictional policy register."
            action={
              <Button variant="secondary" size="sm" onClick={clear}>
                Clear filters
              </Button>
            }
          />
        </Card>
      ) : (
        <>
          <Card className="hidden overflow-hidden md:block">
            <Table>
              <caption className="sr-only">Policy inventory</caption>
              <TableHeader>
                <TableRow>
                  <TableHead>Risk</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Policy</TableHead>
                  <TableHead>Type and scope</TableHead>
                  <TableHead>Assigned agents</TableHead>
                  <TableHead>Session-only action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {visible.map((policy) => (
                  <TableRow key={policy.id}>
                    <TableCell className="align-top text-xs">
                      <RiskChip risk={policy.risk} />
                    </TableCell>
                    <TableCell className="align-top text-xs">
                      <StatusBadge
                        status={policy.status}
                        plain
                        className="text-xs"
                      />
                    </TableCell>
                    <TableCell className="min-w-72 align-top whitespace-normal text-xs">
                      <p className="font-medium">{policy.name}</p>
                      <p className="mt-1 text-foreground-secondary">
                        {policy.summary}
                      </p>
                      <p className="mt-1 font-mono text-[10px] text-foreground-tertiary">
                        {policy.id} · v{policy.version}
                      </p>
                      <PolicyDetails policy={policy} />
                    </TableCell>
                    <TableCell className="align-top whitespace-normal text-xs">
                      <p>{policy.type}</p>
                      <p className="mt-1 text-foreground-secondary">
                        {policy.scope}
                      </p>
                    </TableCell>
                    <TableCell className="align-top whitespace-normal text-xs">
                      <Assignments policy={policy} />
                    </TableCell>
                    <TableCell className="align-top">
                      <Button
                        variant={
                          policy.status === "active" ? "secondary" : "primary"
                        }
                        size="sm"
                        onClick={() => simulateToggle(policy)}
                      >
                        Simulate{" "}
                        {policy.status === "active" ? "disable" : "enable"}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
          <ul className="grid gap-3 md:hidden">
            {visible.map((policy) => (
              <li key={policy.id}>
                <Card>
                  <CardContent className="grid gap-3 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <RiskChip risk={policy.risk} />
                        <h2 className="mt-2 font-medium">{policy.name}</h2>
                        <p className="mt-1 font-mono text-[10px] text-foreground-tertiary">
                          {policy.id} · v{policy.version}
                        </p>
                      </div>
                      <StatusBadge status={policy.status} />
                    </div>
                    <p className="text-sm text-foreground-secondary">
                      {policy.summary}
                    </p>
                    <dl className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Type
                        </dt>
                        <dd>{policy.type}</dd>
                      </div>
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Scope
                        </dt>
                        <dd>{policy.scope}</dd>
                      </div>
                      <div className="col-span-2">
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Assigned agents
                        </dt>
                        <dd className="mt-1">
                          <Assignments policy={policy} />
                        </dd>
                      </div>
                    </dl>
                    <PolicyDetails policy={policy} />
                    <Button
                      variant={
                        policy.status === "active" ? "secondary" : "primary"
                      }
                      size="sm"
                      onClick={() => simulateToggle(policy)}
                    >
                      Simulate{" "}
                      {policy.status === "active" ? "disable" : "enable"}
                    </Button>
                  </CardContent>
                </Card>
              </li>
            ))}
          </ul>
        </>
      )}
      {notice && (
        <div
          role="status"
          className="rounded-atlas-md border border-success-border bg-success-bg px-4 py-3 text-sm text-foreground"
        >
          {notice}
        </div>
      )}
    </div>
  );
}
