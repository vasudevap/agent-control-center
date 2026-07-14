"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowDown, ArrowUp, ArrowUpDown, Circle, Diamond, Search, ShieldAlert, Triangle, TriangleAlert } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SearchField } from "@/components/ui/search-field";
import { Skeleton } from "@/components/ui/skeleton";
import { RiskChip, riskRank, type RiskLevel } from "@/components/risk/risk-indicator";
import { cn } from "@/lib/utils";
import { isQueueApproval, type ApprovalRecord } from "./approval-data";
import { getExpiryPresentation, relativeTime } from "./approval-presentation";
import { ExpiryLabel, ReviewProgressTag, StateChip } from "./approval-badges";

type View = "queue" | "history";
type Presentation = "ready" | "loading" | "error" | "empty";
type SortKey = "attention" | "risk" | "requested" | "expiry";
const PAGE_SIZE = 8;

function SortHeader({ label, sortKey, active, direction, onSort }: { label: string; sortKey: SortKey; active: boolean; direction: "asc" | "desc"; onSort: (key: SortKey) => void }) {
  return (
    <button type="button" onClick={() => onSort(sortKey)} className="inline-flex items-center gap-1 font-mono text-[11px] font-medium uppercase tracking-wider text-foreground-tertiary hover:text-foreground">
      {label}
      {active ? direction === "asc" ? <ArrowUp className="size-3" aria-hidden="true" /> : <ArrowDown className="size-3" aria-hidden="true" /> : <ArrowUpDown className="size-3 opacity-40" aria-hidden="true" />}
    </button>
  );
}

const initialParams = () => (typeof window === "undefined" ? new URLSearchParams() : new URLSearchParams(window.location.search));

export function ApprovalsWorkspace({ approvals, presentationState = "ready" }: { approvals: ApprovalRecord[]; presentationState?: Presentation }) {
  const params = React.useMemo(() => initialParams(), []);
  const [view, setView] = React.useState<View>(params.get("view") === "history" ? "history" : "queue");
  const [query, setQuery] = React.useState(params.get("q") ?? "");
  const [risk, setRisk] = React.useState(params.get("risk") ?? "all");
  const [agent, setAgent] = React.useState(params.get("agent") ?? "all");
  const [sort, setSort] = React.useState<SortKey>((params.get("sort") as SortKey) ?? "attention");
  const [direction, setDirection] = React.useState<"asc" | "desc">("desc");
  const [page, setPage] = React.useState(Number(params.get("page")) || 1);

  React.useEffect(() => {
    const next = new URLSearchParams({ view });
    if (query) next.set("q", query);
    if (risk !== "all") next.set("risk", risk);
    if (agent !== "all") next.set("agent", agent);
    if (sort !== "attention") next.set("sort", sort);
    if (page > 1) next.set("page", String(page));
    window.history.replaceState(null, "", `${window.location.pathname}?${next}`);
  }, [agent, page, query, risk, sort, view]);

  const queue = approvals.filter(isQueueApproval);
  const expiringCount = queue.filter((item) => ["nearing", "imminent"].includes(getExpiryPresentation(item.expiresAt, item.requestedAt).urgency)).length;

  const onSort = (key: SortKey) => {
    if (key === sort) setDirection((d) => (d === "asc" ? "desc" : "asc"));
    else { setSort(key); setDirection(key === "requested" ? "desc" : "asc"); }
  };

  const listed = React.useMemo(() => {
    const dirMul = direction === "asc" ? 1 : -1;
    return approvals
      .filter((item) => (view === "queue" ? isQueueApproval(item) : !isQueueApproval(item)))
      .filter((item) => {
        const text = [item.id, item.agent.id, item.agent.name, item.action, item.target, item.runId, item.policy].join(" ").toLowerCase();
        return (!query || text.includes(query.toLowerCase())) && (risk === "all" || item.risk === risk) && (agent === "all" || item.agent.id === agent);
      })
      .sort((a, b) => {
        if (sort === "risk") return (riskRank(b.risk) - riskRank(a.risk)) * dirMul * -1;
        if (sort === "requested") return (+new Date(b.requestedAt) - +new Date(a.requestedAt)) * dirMul * -1;
        if (sort === "expiry") return (+new Date(a.expiresAt ?? "9999") - +new Date(b.expiresAt ?? "9999")) * dirMul * -1;
        const expiryUrgencyRank = (item: ApprovalRecord) => ({ imminent: 0, nearing: 1, scheduled: 2, none: 3, expired: 4 })[getExpiryPresentation(item.expiresAt, item.requestedAt).urgency];
        return expiryUrgencyRank(a) - expiryUrgencyRank(b) || riskRank(b.risk) - riskRank(a.risk);
      });
  }, [agent, approvals, direction, query, risk, sort, view]);

  const maxPage = Math.max(1, Math.ceil(listed.length / PAGE_SIZE));
  const shown = listed.slice((Math.min(page, maxPage) - 1) * PAGE_SIZE, Math.min(page, maxPage) * PAGE_SIZE);
  const reset = () => { setQuery(""); setRisk("all"); setAgent("all"); setSort("attention"); setPage(1); };
  const agents = Array.from(new Map(approvals.map((item) => [item.agent.id, item.agent.name])).entries());

  return (
    <div className="flex min-w-0 flex-col gap-5">
      <PageHeader eyebrow="Governance" title="Approvals" icon={ShieldAlert} description="Review and authorize proposed actions before an agent may proceed." meta={<span className="rounded-atlas-sm border border-info-border bg-info-bg px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide text-info">Frontend prototype</span>} />

      {presentationState === "loading" ? (
        <div className="grid gap-3"><Skeleton className="h-32 w-full" /><Skeleton className="h-64 w-full" /></div>
      ) : presentationState === "error" ? (
        <StateCard title="Approval data is unavailable" detail="This controlled error state did not contact a real approval service." />
      ) : (
        <section className="grid gap-3" aria-label={view === "queue" ? "Approval Queue" : "Approval History"}>
          <div className="grid overflow-hidden rounded-atlas-md border border-border-default bg-surface-secondary">
            <div className="flex border-b border-border-default" role="tablist" aria-label="Approvals views">
              {(["queue", "history"] as View[]).map((item) => (
                <button
                  key={item}
                  type="button"
                  role="tab"
                  aria-selected={view === item}
                  onClick={() => { setView(item); setPage(1); }}
                  className={cn("relative flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors", view === item ? "text-foreground" : "text-foreground-secondary hover:text-foreground")}
                >
                  {view === item && <span className="absolute inset-x-3 bottom-0 h-0.5 rounded-full bg-brand" aria-hidden="true" />}
                  {item === "queue" ? "Queue" : "History"}
                  {item === "queue" && queue.length > 0 && (
                    <span className="rounded-atlas-sm bg-surface-tertiary px-1.5 py-0.5 font-mono text-[10px] font-semibold text-foreground-secondary">{queue.length}</span>
                  )}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap items-center justify-between gap-2 p-3">
              <p className="text-xs text-foreground-secondary">
                Showing <span className="font-mono font-semibold text-foreground">{listed.length}</span> of {view === "queue" ? queue.length : approvals.length - queue.length} {view} records.
                {view === "queue" && expiringCount > 0 ? ` ${expiringCount} nearing expiry.` : ""}
              </p>
              <div className="flex items-center gap-3">
                <div className="hidden items-center gap-2.5 text-[10px] text-foreground-tertiary sm:flex">
                  <span className="flex items-center gap-1"><Diamond className="size-3 fill-current text-risk-critical" aria-hidden="true" />Critical</span>
                  <span className="flex items-center gap-1"><TriangleAlert className="size-3 text-risk-high" aria-hidden="true" />High</span>
                  <span className="flex items-center gap-1"><Triangle className="size-3 text-risk-medium" aria-hidden="true" />Medium</span>
                  <span className="flex items-center gap-1"><Circle className="size-3 text-risk-low" aria-hidden="true" />Low</span>
                </div>
                <Button variant="ghost" size="sm" onClick={reset}>Clear filters</Button>
              </div>
            </div>
            <div className="grid gap-2.5 p-3 pt-0 md:grid-cols-3">
              <SearchField value={query} onChange={(v) => { setQuery(v); setPage(1); }} placeholder="ID, agent, action, target, or policy" />
              <Select label="Risk" value={risk} onChange={(v) => { setRisk(v); setPage(1); }} options={["all", "Low", "Medium", "High", "Critical"]} />
              <Select label="Agent" value={agent} onChange={(v) => { setAgent(v); setPage(1); }} options={["all", ...agents.map(([id]) => id)]} labels={Object.fromEntries(agents)} />
            </div>
          </div>

          {presentationState === "empty" || (view === "queue" && queue.length === 0) ? (
            <StateCard title="No actions currently require authorization" detail="Fictional approval requests will appear here when available." />
          ) : shown.length === 0 ? (
            <StateCard title="No approvals match the current search or filters" detail="Adjust local controls to return to the fixture set." action={<Button variant="secondary" onClick={reset}>Clear filters</Button>} />
          ) : (
            <>
              <Card className="hidden overflow-hidden md:block">
                <table className="w-full caption-bottom text-sm">
                  <thead className="border-b border-border-subtle">
                    <tr>
                      <th className="h-10 px-4 text-left"><SortHeader label="Approval" sortKey="attention" active={sort === "attention"} direction={direction} onSort={onSort} /></th>
                      <th className="h-10 px-3 text-left"><SortHeader label="Risk" sortKey="risk" active={sort === "risk"} direction={direction} onSort={onSort} /></th>
                      <th className="h-10 px-3 text-left font-mono text-[11px] font-medium uppercase tracking-wider text-foreground-tertiary">Agent</th>
                      <th className="h-10 px-3 text-left"><SortHeader label="Requested" sortKey="requested" active={sort === "requested"} direction={direction} onSort={onSort} /></th>
                      <th className="h-10 px-3 text-left"><SortHeader label="Expiry" sortKey="expiry" active={sort === "expiry"} direction={direction} onSort={onSort} /></th>
                      <th className="h-10 px-4 text-left font-mono text-[11px] font-medium uppercase tracking-wider text-foreground-tertiary">{view === "queue" ? "Review" : "Outcome"}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {shown.map((item) => <Row key={item.id} approval={item} view={view} />)}
                  </tbody>
                </table>
              </Card>
              <div className="grid gap-2.5 md:hidden">
                {shown.map((item) => <ApprovalCard key={item.id} approval={item} view={view} />)}
              </div>
            </>
          )}

          {shown.length > 0 && (
            <div className="flex items-center justify-between">
              <p className="text-xs text-foreground-secondary">Page {Math.min(page, maxPage)} of {maxPage}</p>
              <div className="flex gap-2">
                <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</Button>
                <Button variant="secondary" size="sm" disabled={page >= maxPage} onClick={() => setPage(page + 1)}>Next</Button>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

function Select({ label, value, onChange, options, labels = {} }: { label: string; value: string; onChange: (value: string) => void; options: string[]; labels?: Record<string, string> }) {
  return (
    <select aria-label={label} value={value} onChange={(e) => onChange(e.target.value)} className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm">
      <option value="all">{labels.all ?? `All ${label.toLowerCase()}s`}</option>
      {options.filter((o) => o !== "all").map((o) => <option key={o} value={o}>{labels[o] ?? o}</option>)}
    </select>
  );
}

function Row({ approval, view }: { approval: ApprovalRecord; view: View }) {
  return (
    <tr className="relative border-b border-border-subtle transition-colors last:border-0 hover:bg-surface-hover">
      <td className="px-4 py-3 align-top">
        <Link className="relative z-10 w-fit font-medium text-foreground after:absolute after:inset-0 after:content-[''] hover:text-brand hover:underline" href={`/approvals/${approval.id}?from=${encodeURIComponent(`/approvals?view=${view}`)}`}>{approval.action}</Link>
        <p className="mt-0.5 font-mono text-[11px] text-foreground-tertiary">{approval.id} • {approval.policy}</p>
      </td>
      <td className="px-3 py-3 align-top"><RiskChip risk={approval.risk as RiskLevel} iconOnly /></td>
      <td className="px-3 py-3 align-top text-foreground-secondary">{approval.agent.name}</td>
      <td className="px-3 py-3 align-top text-xs text-foreground-secondary">{relativeTime(approval.requestedAt)}</td>
      <td className="px-3 py-3 align-top"><ExpiryLabel approval={approval} /></td>
      <td className="px-4 py-3 align-top">
        {view === "queue" ? <ReviewProgressTag progress={approval.reviewProgress} /> : (
          <div className="flex flex-col gap-0.5">
            <StateChip state={approval.state} />
            <span className="text-[11px] text-foreground-tertiary">Outcome: {approval.executionOutcome}</span>
          </div>
        )}
      </td>
    </tr>
  );
}

function ApprovalCard({ approval, view }: { approval: ApprovalRecord; view: View }) {
  return (
    <Link href={`/approvals/${approval.id}?from=${encodeURIComponent(`/approvals?view=${view}`)}`} className="block rounded-atlas-md border border-border-default bg-surface p-4">
      <div className="flex items-center justify-between gap-2">
        <RiskChip risk={approval.risk as RiskLevel} iconOnly />
        {view === "queue" ? <ReviewProgressTag progress={approval.reviewProgress} /> : <StateChip state={approval.state} />}
      </div>
      <p className="mt-3 text-sm font-semibold text-foreground">{approval.action}</p>
      <p className="mt-1 text-xs text-foreground-secondary">{approval.agent.name} • {approval.id}</p>
      <div className="mt-2"><ExpiryLabel approval={approval} /></div>
    </Link>
  );
}

function StateCard({ title, detail, action }: { title: string; detail: string; action?: React.ReactNode }) {
  return (
    <Card className="border-dashed">
      <CardContent className="flex flex-col items-start gap-3 p-8">
        <Search className="size-5 text-foreground-tertiary" aria-hidden="true" />
        <div><h3 className="font-semibold text-foreground">{title}</h3><p className="mt-1 text-sm text-foreground-secondary">{detail}</p></div>
        {action}
      </CardContent>
    </Card>
  );
}
