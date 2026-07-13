"use client";

import * as React from "react";
import Link from "next/link";
import { AlertTriangle, Clock3, Search, ShieldCheck } from "lucide-react";
import { Breadcrumb } from "@/components/layout/breadcrumb";
import { PageHeader } from "@/components/layout/page-header";
import { Badge, type BadgeProps } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SearchField } from "@/components/ui/search-field";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { isQueueApproval, type ApprovalRecord, type ApprovalRisk, type ApprovalState } from "./approval-data";

type View = "queue" | "history";
type Presentation = "ready" | "loading" | "error" | "empty";
const riskOrder: Record<ApprovalRisk, number> = { Critical: 4, High: 3, Medium: 2, Low: 1 };
const PAGE_SIZE = 5;

const stateVariant = (state: ApprovalState): BadgeProps["variant"] => state === "Approved" ? "success" : state === "Rejected" || state === "Expired" ? "error" : state === "Blocked" || state === "Clarification requested" ? "warning" : "brand";
const riskVariant = (risk: ApprovalRisk): BadgeProps["variant"] => risk === "Critical" ? "error" : risk === "High" ? "warning" : risk === "Medium" ? "brand" : "neutral";
const initialParams = () => typeof window === "undefined" ? new URLSearchParams() : new URLSearchParams(window.location.search);

export function ApprovalsWorkspace({ approvals, presentationState = "ready" }: { approvals: ApprovalRecord[]; presentationState?: Presentation }) {
  const params = React.useMemo(() => initialParams(), []);
  const [view, setView] = React.useState<View>(params.get("view") === "history" ? "history" : "queue");
  const [query, setQuery] = React.useState(params.get("q") ?? "");
  const [risk, setRisk] = React.useState(params.get("risk") ?? "all");
  const [agent, setAgent] = React.useState(params.get("agent") ?? "all");
  const [sort, setSort] = React.useState(params.get("sort") ?? "attention");
  const [page, setPage] = React.useState(Number(params.get("page")) || 1);
  React.useEffect(() => { const next = new URLSearchParams({ view }); if (query) next.set("q", query); if (risk !== "all") next.set("risk", risk); if (agent !== "all") next.set("agent", agent); if (sort !== "attention") next.set("sort", sort); if (page > 1) next.set("page", String(page)); window.history.replaceState(null, "", `${window.location.pathname}?${next}`); }, [agent, page, query, risk, sort, view]);

  const queue = approvals.filter(isQueueApproval);
  const listed = React.useMemo(() => approvals.filter((item) => view === "queue" ? isQueueApproval(item) : !isQueueApproval(item)).filter((item) => {
    const text = [item.id, item.agent.id, item.agent.name, item.action, item.target, item.runId, item.policy].join(" ").toLowerCase();
    return (!query || text.includes(query.toLowerCase())) && (risk === "all" || item.risk === risk) && (agent === "all" || item.agent.id === agent);
  }).sort((a, b) => sort === "risk" ? riskOrder[b.risk] - riskOrder[a.risk] : sort === "newest" ? +new Date(b.requestedAt) - +new Date(a.requestedAt) : sort === "oldest" ? +new Date(a.requestedAt) - +new Date(b.requestedAt) : +new Date(a.expiresAt ?? "9999") - +new Date(b.expiresAt ?? "9999") || riskOrder[b.risk] - riskOrder[a.risk]), [agent, approvals, query, risk, sort, view]);
  const maxPage = Math.max(1, Math.ceil(listed.length / PAGE_SIZE));
  const shown = listed.slice((Math.min(page, maxPage) - 1) * PAGE_SIZE, Math.min(page, maxPage) * PAGE_SIZE);
  const reset = () => { setQuery(""); setRisk("all"); setAgent("all"); setSort("attention"); setPage(1); };
  const agents = Array.from(new Map(approvals.map((item) => [item.agent.id, item.agent.name])).entries());

  return <div className="flex min-w-0 flex-col gap-6">
    <Breadcrumb items={[{ label: "Approvals" }]} />
    <PageHeader title="Human Approvals" description="Review fictional approval requests and governance context for the Atlas AI workforce." icon={ShieldCheck} />
    <Notice />
    <div className="flex gap-2 border-b border-border-default" role="tablist" aria-label="Approvals views">{(["queue", "history"] as View[]).map((item) => <button key={item} type="button" role="tab" aria-selected={view === item} onClick={() => { setView(item); setPage(1); }} className={cn("border-b-2 px-4 py-3 text-sm font-medium", view === item ? "border-brand text-brand" : "border-transparent text-foreground-secondary hover:text-foreground")}>{item === "queue" ? `Queue (${queue.length})` : "History"}</button>)}</div>
    {presentationState === "loading" ? <div className="grid gap-4"><Skeleton className="h-40 w-full" /><Skeleton className="h-64 w-full" /></div> : presentationState === "error" ? <StateCard title="Approval data is unavailable" detail="This controlled error state did not contact a real approval service." /> : <section className="grid gap-5" aria-label={view === "queue" ? "Approval Queue" : "Approval History"}>
      <div className="grid gap-4 rounded-atlas-lg border border-border-default bg-surface p-4 shadow-atlas-sm"><div className="flex flex-wrap items-end justify-between gap-3"><div><h2 className="text-lg font-semibold text-foreground">{view === "queue" ? "Approval Queue" : "Approval History"}</h2><p className="text-sm text-foreground-secondary">Showing {listed.length} of {view === "queue" ? queue.length : approvals.length - queue.length} fictional {view} records.</p></div><Button variant="secondary" onClick={reset}>Clear filters</Button></div><div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4"><SearchField value={query} onChange={(value) => { setQuery(value); setPage(1); }} placeholder="ID, agent, action, target, or policy" /><Select label="Risk" value={risk} onChange={(value) => { setRisk(value); setPage(1); }} options={["all", "Low", "Medium", "High", "Critical"]} /><Select label="Agent" value={agent} onChange={(value) => { setAgent(value); setPage(1); }} options={["all", ...agents.map(([id]) => id)]} labels={Object.fromEntries(agents)} /><Select label="Sort" value={sort} onChange={(value) => { setSort(value); setPage(1); }} options={["attention", "risk", "newest", "oldest"]} labels={{ attention: "Attention priority", risk: "Risk highest", newest: "Newest requested", oldest: "Oldest requested" }} /></div></div>
      {presentationState === "empty" || (view === "queue" && queue.length === 0) ? <StateCard title="No approvals are waiting for review" detail="Fictional approval requests will appear here when available." /> : shown.length === 0 ? <StateCard title="No approvals match the current search or filters" detail="Adjust local controls to return to the fixture set." action={<Button variant="secondary" onClick={reset}>Clear filters</Button>} /> : <><div className="hidden overflow-hidden rounded-atlas-lg border border-border-default bg-surface md:block"><Table><TableHeader><TableRow><TableHead>Approval</TableHead><TableHead>Risk</TableHead><TableHead>Agent</TableHead><TableHead>State &amp; outcome</TableHead></TableRow></TableHeader><TableBody>{shown.map((item) => <Row key={item.id} approval={item} />)}</TableBody></Table></div><div className="grid gap-3 md:hidden">{shown.map((item) => <ApprovalCard key={item.id} approval={item} />)}</div></>}
      {shown.length > 0 && <div className="flex items-center justify-between"><p className="text-sm text-foreground-secondary">Page {Math.min(page, maxPage)} of {maxPage}</p><div className="flex gap-2"><Button variant="secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</Button><Button variant="secondary" disabled={page >= maxPage} onClick={() => setPage(page + 1)}>Next</Button></div></div>}
    </section>}
  </div>;
}

function Notice() { return <Card className="border-info-border bg-info-bg"><CardContent className="flex gap-3 p-4 text-sm leading-relaxed text-info"><AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden="true" /><p><strong>Frontend prototype.</strong> Data and actions are local simulations only. Nothing here affects a real agent, runtime, service, policy engine, audit system, or persistent record.</p></CardContent></Card>; }
function Select({ label, value, onChange, options, labels = {} }: { label: string; value: string; onChange: (value: string) => void; options: string[]; labels?: Record<string, string> }) { return <label className="grid gap-1 text-sm font-medium text-foreground">{label}<select aria-label={label} value={value} onChange={(event) => onChange(event.target.value)} className="h-10 rounded-atlas-md border border-border-default bg-surface px-3 text-sm"><option value="all">{labels.all ?? `All ${label.toLowerCase()}s`}</option>{options.filter((item) => item !== "all").map((item) => <option key={item} value={item}>{labels[item] ?? item}</option>)}</select></label>; }
function Row({ approval }: { approval: ApprovalRecord }) { return <TableRow><TableCell className="min-w-0 whitespace-normal"><Link className="font-medium hover:text-brand hover:underline" href={`/approvals/${approval.id}?from=${encodeURIComponent("/approvals?view=queue")}`}>{approval.action}</Link><p className="mt-1 font-mono text-xs text-foreground-tertiary">{approval.id}</p><p className="mt-1 text-xs text-foreground-secondary">{approval.policy}</p></TableCell><TableCell><Badge variant={riskVariant(approval.risk)}>{approval.risk}</Badge></TableCell><TableCell>{approval.agent.name}</TableCell><TableCell><Badge variant={stateVariant(approval.state)}>{approval.state}</Badge><p className="mt-1 text-xs text-foreground-secondary">Outcome: {approval.executionOutcome}</p></TableCell></TableRow>; }
function ApprovalCard({ approval }: { approval: ApprovalRecord }) { return <Link href={`/approvals/${approval.id}?from=${encodeURIComponent("/approvals?view=queue")}`} className="rounded-atlas-lg border border-border-default bg-surface p-4"><div className="flex justify-between gap-2"><Badge variant={riskVariant(approval.risk)}>{approval.risk} risk</Badge><Badge variant={stateVariant(approval.state)}>{approval.state}</Badge></div><p className="mt-4 font-semibold text-foreground">{approval.action}</p><p className="mt-2 text-sm text-foreground-secondary">{approval.agent.name}</p><p className="mt-3 flex items-center gap-1 text-xs text-foreground-tertiary"><Clock3 className="size-3.5" aria-hidden="true" />{approval.id}</p></Link>; }
function StateCard({ title, detail, action }: { title: string; detail: string; action?: React.ReactNode }) { return <Card className="border-dashed"><CardContent className="flex flex-col items-start gap-3 p-8"><Search className="size-5 text-foreground-tertiary" aria-hidden="true" /><div><h3 className="font-semibold text-foreground">{title}</h3><p className="mt-1 text-sm text-foreground-secondary">{detail}</p></div>{action}</CardContent></Card>; }
