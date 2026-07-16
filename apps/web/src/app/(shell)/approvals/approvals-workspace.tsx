"use client";

import * as React from "react";
import Link from "next/link";
import { Circle, Diamond, Search, Triangle, TriangleAlert } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { APPROVALS_ICON } from "@/components/layout/nav-items";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SearchField } from "@/components/ui/search-field";
import { Skeleton } from "@/components/ui/skeleton";
import { getAriaSort, SortHeader, type SortDirection } from "@/components/ui/sort-header";
import { RiskChip, riskRank, type RiskLevel } from "@/components/risk/risk-indicator";
import { cn } from "@/lib/utils";
import { isQueueApproval, type ApprovalRecord } from "./approval-data";
import { getExpiryPresentation, relativeTime } from "./approval-presentation";
import { ExpiryLabel, ReviewProgressTag, StateChip, reviewRank } from "./approval-badges";

type View = "queue" | "history";
type Presentation = "ready" | "loading" | "error" | "empty";
type SortKey = "attention" | "risk" | "agent" | "review" | "requested" | "expiry" | "decided";
const PAGE_SIZE = 8;
const DEFAULT_SORT: Record<View, SortKey> = { queue: "attention", history: "decided" };
const DEFAULT_DIRECTION: Record<SortKey, SortDirection> = {
  attention: "asc",
  risk: "desc",
  agent: "asc",
  review: "asc",
  requested: "desc",
  expiry: "asc",
  decided: "desc",
};

interface CollectionState {
  view: View;
  query: string;
  risk: string;
  review: string;
  approvalState: string;
  sort: SortKey;
  direction: SortDirection;
  page: number;
}

function isSortKey(value: string | null): value is SortKey {
  return ["attention", "risk", "agent", "review", "requested", "expiry", "decided"].includes(value ?? "");
}

function isSortKeyForView(value: string | null, view: View): value is SortKey {
  if (!isSortKey(value)) return false;
  return view === "queue" ? value !== "decided" : value !== "requested" && value !== "review";
}

function collectionParams(state: CollectionState) {
  const next = new URLSearchParams({ view: state.view });
  if (state.query) next.set("q", state.query);
  if (state.risk !== "all") next.set("risk", state.risk);
  if (state.view === "queue" && state.review !== "all") next.set("review", state.review);
  if (state.view === "history" && state.approvalState !== "all") next.set("state", state.approvalState);
  if (state.sort !== DEFAULT_SORT[state.view]) next.set("sort", state.sort);
  if (state.direction !== DEFAULT_DIRECTION[state.sort]) next.set("dir", state.direction);
  if (state.page > 1) next.set("page", String(state.page));
  return next;
}

function stateFromParams(params: URLSearchParams): CollectionState {
  const view: View = params.get("view") === "history" ? "history" : "queue";
  const requestedSort = params.get("sort");
  const sort: SortKey = isSortKeyForView(requestedSort, view) ? requestedSort : DEFAULT_SORT[view];
  const requestedDirection = params.get("dir");
  const requestedPage = Number(params.get("page"));
  return {
    view,
    query: params.get("q") ?? "",
    risk: params.get("risk") ?? "all",
    review: view === "queue" ? params.get("review") ?? "all" : "all",
    approvalState: view === "history" ? params.get("state") ?? "all" : "all",
    sort,
    direction: requestedDirection === "asc" || requestedDirection === "desc"
      ? requestedDirection
      : DEFAULT_DIRECTION[sort],
    page: Number.isInteger(requestedPage) && requestedPage > 0 ? requestedPage : 1,
  };
}

export function ApprovalsWorkspace({ approvals, presentationState = "ready" }: { approvals: ApprovalRecord[]; presentationState?: Presentation }) {
  const initialState = React.useMemo(() => stateFromParams(new URLSearchParams()), []);
  const [view, setView] = React.useState<View>(initialState.view);
  const [query, setQuery] = React.useState(initialState.query);
  const [risk, setRisk] = React.useState(initialState.risk);
  const [review, setReview] = React.useState(initialState.review);
  const [approvalState, setApprovalState] = React.useState(initialState.approvalState);
  const [sort, setSort] = React.useState<SortKey>(initialState.sort);
  const [direction, setDirection] = React.useState<SortDirection>(initialState.direction);
  const [page, setPage] = React.useState(initialState.page);

  React.useEffect(() => {
    const restoreFromLocation = () => {
      const restored = stateFromParams(new URLSearchParams(window.location.search));
      setView(restored.view);
      setQuery(restored.query);
      setRisk(restored.risk);
      setReview(restored.review);
      setApprovalState(restored.approvalState);
      setSort(restored.sort);
      setDirection(restored.direction);
      setPage(restored.page);
    };
    window.addEventListener("popstate", restoreFromLocation);
    restoreFromLocation();
    return () => window.removeEventListener("popstate", restoreFromLocation);
  }, []);

  const currentState = (): CollectionState => ({ view, query, risk, review, approvalState, sort, direction, page });
  const writeLocation = (updates: Partial<CollectionState>, mode: "push" | "replace" = "push") => {
    const next = { ...currentState(), ...updates };
    const url = `${window.location.pathname}?${collectionParams(next)}`;
    window.history[mode === "push" ? "pushState" : "replaceState"](null, "", url);
  };

  const queue = approvals.filter(isQueueApproval);
  const expiringCount = queue.filter((item) => ["nearing", "imminent"].includes(getExpiryPresentation(item.expiresAt, item.requestedAt).urgency)).length;

  const onSort = (key: SortKey) => {
    const nextDirection = key === sort
      ? (direction === "asc" ? "desc" : "asc")
      : DEFAULT_DIRECTION[key];
    setSort(key);
    setDirection(nextDirection);
    setPage(1);
    writeLocation({ sort: key, direction: nextDirection, page: 1 });
  };

  const listed = React.useMemo(() => {
    const dirMul = direction === "asc" ? 1 : -1;
    return approvals
      .filter((item) => (view === "queue" ? isQueueApproval(item) : !isQueueApproval(item)))
      .filter((item) => {
        const text = [item.id, item.agent.id, item.agent.name, item.action, item.target, item.runId, item.policy, item.evidence.source].join(" ").toLowerCase();
        const matchesViewFilter = view === "queue"
          ? review === "all" || item.reviewProgress === review
          : approvalState === "all" || item.state === approvalState;
        return (!query || text.includes(query.toLowerCase())) && (risk === "all" || item.risk === risk) && matchesViewFilter;
      })
      .sort((a, b) => {
        const expiryUrgencyRank = (item: ApprovalRecord) => ({ imminent: 0, nearing: 1, scheduled: 2, none: 3, expired: 4 })[getExpiryPresentation(item.expiresAt, item.requestedAt).urgency];
        const comparison = sort === "risk"
          ? riskRank(a.risk) - riskRank(b.risk)
          : sort === "agent"
            ? a.agent.name.localeCompare(b.agent.name)
            : sort === "review"
              ? reviewRank(a.reviewProgress) - reviewRank(b.reviewProgress)
              : sort === "requested"
                ? +new Date(a.requestedAt) - +new Date(b.requestedAt)
                : sort === "decided"
                  ? +new Date(a.decidedAt ?? 0) - +new Date(b.decidedAt ?? 0)
                : sort === "expiry"
                  ? +new Date(a.expiresAt ?? "9999") - +new Date(b.expiresAt ?? "9999")
                  : expiryUrgencyRank(a) - expiryUrgencyRank(b) || riskRank(b.risk) - riskRank(a.risk);
        return comparison * dirMul;
      });
  }, [approvalState, review, approvals, direction, query, risk, sort, view]);

  const maxPage = Math.max(1, Math.ceil(listed.length / PAGE_SIZE));
  const currentPage = Math.min(page, maxPage);
  const shown = listed.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);
  const reset = () => {
    setQuery("");
    setRisk("all");
    setReview("all");
    setApprovalState("all");
    const defaultSort = DEFAULT_SORT[view];
    setSort(defaultSort);
    setDirection(DEFAULT_DIRECTION[defaultSort]);
    setPage(1);
    writeLocation({ query: "", risk: "all", review: "all", approvalState: "all", sort: defaultSort, direction: DEFAULT_DIRECTION[defaultSort], page: 1 });
  };
  const collectionHref = `/approvals?${collectionParams({ ...currentState(), page: currentPage })}`;

  return (
    <div className="flex min-w-0 flex-col gap-5">
      <PageHeader eyebrow="Governance" title="Approvals" icon={APPROVALS_ICON} description="Review and authorize proposed actions before an agent may proceed." meta={<span className="rounded-atlas-sm border border-info-border bg-info-bg px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide text-info">Frontend prototype</span>} />

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
                  onClick={() => {
                    const defaultSort = DEFAULT_SORT[item];
                    setView(item);
                    setSort(defaultSort);
                    setDirection(DEFAULT_DIRECTION[defaultSort]);
                    setPage(1);
                    writeLocation({ view: item, sort: defaultSort, direction: DEFAULT_DIRECTION[defaultSort], page: 1 });
                  }}
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
              <SearchField value={query} onChange={(v) => { setQuery(v); setPage(1); writeLocation({ query: v, page: 1 }, "replace"); }} placeholder="ID, agent, action, target, evidence source, or policy" />
              <Select label="Risk" value={risk} onChange={(v) => { setRisk(v); setPage(1); writeLocation({ risk: v, page: 1 }); }} options={["all", "Low", "Medium", "High", "Critical"]} />
              {view === "queue" ? (
                <Select label="Review" value={review} onChange={(v) => { setReview(v); setPage(1); writeLocation({ review: v, page: 1 }); }} options={["all", "Unopened", "In review", "Awaiting information", "Blocked"]} />
              ) : (
                <Select label="State" value={approvalState} onChange={(v) => { setApprovalState(v); setPage(1); writeLocation({ approvalState: v, page: 1 }); }} options={["all", "Approved", "Rejected", "Expired", "Cancelled"]} />
              )}
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
                  <caption className="sr-only">{view === "queue" ? "Approval Queue" : "Approval History"}</caption>
                  <thead className="border-b border-border-subtle">
                    <tr>
                      <th aria-sort={getAriaSort(sort === "risk", direction)} className="h-10 px-4 text-left"><SortHeader label="Risk" sortKey="risk" active={sort === "risk"} direction={direction} onSort={onSort} /></th>
                      <th aria-sort={getAriaSort(sort === "attention", direction)} className="h-10 px-3 text-left"><SortHeader label="Approval" sortKey="attention" active={sort === "attention"} direction={direction} onSort={onSort} /></th>
                      <th aria-sort={getAriaSort(sort === "agent", direction)} className="h-10 px-3 text-left"><SortHeader label="Agent" sortKey="agent" active={sort === "agent"} direction={direction} onSort={onSort} /></th>
                      <th aria-sort={getAriaSort(sort === (view === "queue" ? "requested" : "decided"), direction)} className="h-10 px-3 text-left">
                        <SortHeader label={view === "queue" ? "Requested" : "Decided"} sortKey={view === "queue" ? "requested" : "decided"} active={sort === (view === "queue" ? "requested" : "decided")} direction={direction} onSort={onSort} />
                      </th>
                      <th aria-sort={getAriaSort(sort === "expiry", direction)} className="h-10 px-3 text-left"><SortHeader label="Expiry" sortKey="expiry" active={sort === "expiry"} direction={direction} onSort={onSort} /></th>
                      <th aria-sort={view === "queue" ? getAriaSort(sort === "review", direction) : undefined} className="h-10 px-4 text-left">
                        {view === "queue" ? (
                          <SortHeader label="Review" sortKey="review" active={sort === "review"} direction={direction} onSort={onSort} />
                        ) : (
                          <span className="font-mono text-[11px] font-medium uppercase tracking-wider text-foreground-tertiary">Outcome</span>
                        )}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {shown.map((item) => <Row key={item.id} approval={item} view={view} from={collectionHref} />)}
                  </tbody>
                </table>
              </Card>
              <ul className="grid gap-2.5 md:hidden" aria-label={view === "queue" ? "Approval Queue mobile list" : "Approval History mobile list"}>
                {shown.map((item) => <ApprovalCard key={item.id} approval={item} view={view} from={collectionHref} />)}
              </ul>
            </>
          )}

          {shown.length > 0 && (
            <div className="flex items-center justify-between">
              <p className="text-xs text-foreground-secondary">Page {currentPage} of {maxPage}</p>
              <div className="flex gap-2">
                <Button variant="secondary" size="sm" disabled={currentPage <= 1} onClick={() => { const nextPage = currentPage - 1; setPage(nextPage); writeLocation({ page: nextPage }); }}>Previous</Button>
                <Button variant="secondary" size="sm" disabled={currentPage >= maxPage} onClick={() => { const nextPage = currentPage + 1; setPage(nextPage); writeLocation({ page: nextPage }); }}>Next</Button>
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

function Row({ approval, view, from }: { approval: ApprovalRecord; view: View; from: string }) {
  return (
    <tr className="relative border-b border-border-subtle transition-colors last:border-0 hover:bg-surface-hover">
      <td className="px-4 py-3 align-top"><RiskChip risk={approval.risk as RiskLevel} iconOnly /></td>
      <td className="px-3 py-3 align-top">
        <Link className="relative z-10 w-fit break-words font-medium text-foreground after:absolute after:inset-0 after:content-[''] hover:text-brand hover:underline" href={`/approvals/${approval.id}?from=${encodeURIComponent(from)}`}>{approval.action}</Link>
        <p className="mt-0.5 break-words font-mono text-[11px] text-foreground-tertiary">{approval.id} • {approval.policy}</p>
        {view === "history" && <p className="mt-1 text-[11px] text-foreground-secondary">Reason: {approval.decisionReason ?? "Not provided"}</p>}
      </td>
      <td className="break-words px-3 py-3 align-top text-xs text-foreground-secondary">
        {approval.agent.name}
        {view === "history" && <span className="mt-0.5 block text-[11px] text-foreground-tertiary">Reviewer: {approval.reviewer ?? "Not recorded"}</span>}
      </td>
      <td className="px-3 py-3 align-top text-xs text-foreground-secondary">
        <time dateTime={view === "queue" ? approval.requestedAt : approval.decidedAt} title={new Date(view === "queue" ? approval.requestedAt : approval.decidedAt ?? approval.requestedAt).toLocaleString()}>
          {relativeTime(view === "queue" ? approval.requestedAt : approval.decidedAt ?? approval.requestedAt)}
        </time>
      </td>
      <td className="px-3 py-3 align-top text-xs"><ExpiryLabel approval={approval} /></td>
      <td className="px-4 py-3 align-top text-xs">
        {view === "queue" ? <ReviewProgressTag progress={approval.reviewProgress} /> : (
          <div className="flex flex-col gap-0.5">
            <StateChip state={approval.state} className="text-xs" />
            <span className="text-[11px] text-foreground-tertiary">Outcome: {approval.executionOutcome}</span>
            <span className="font-mono text-[10px] text-foreground-tertiary">{approval.correlationId ?? "No correlation reference"}</span>
          </div>
        )}
      </td>
    </tr>
  );
}

function ApprovalCard({ approval, view, from }: { approval: ApprovalRecord; view: View; from: string }) {
  return (
    <li>
      <Link href={`/approvals/${approval.id}?from=${encodeURIComponent(from)}`} className="block rounded-atlas-md border border-border-default bg-surface p-4">
        <div className="flex items-center justify-between gap-2">
          <RiskChip risk={approval.risk as RiskLevel} iconOnly />
          <StateChip state={approval.state} className="text-xs" />
        </div>
        <p className="mt-3 break-words text-sm font-semibold text-foreground">{approval.action}</p>
        <p className="mt-1 break-words text-xs text-foreground-secondary">
          <span className="font-medium text-foreground">Target:</span> {approval.target}
        </p>
        <p className="mt-2 break-words text-xs text-foreground-secondary">{approval.agent.name} • <span className="break-all font-mono">{approval.id}</span></p>
        <dl className="mt-3 grid grid-cols-2 gap-3 border-t border-border-subtle pt-3 text-xs">
          <div>
            <dt className="font-mono text-[10px] uppercase tracking-wide text-foreground-tertiary">{view === "queue" ? "Requested" : "Decided"}</dt>
            <dd className="mt-0.5 text-foreground-secondary">{relativeTime(view === "queue" ? approval.requestedAt : approval.decidedAt ?? approval.requestedAt)}</dd>
          </div>
          <div>
            <dt className="font-mono text-[10px] uppercase tracking-wide text-foreground-tertiary">Expires</dt>
            <dd className="mt-0.5"><ExpiryLabel approval={approval} /></dd>
          </div>
        </dl>
        <div className="mt-3 flex items-center justify-between gap-2 border-t border-border-subtle pt-3">
          <span className="font-mono text-[10px] uppercase tracking-wide text-foreground-tertiary">{view === "queue" ? "Review" : "Outcome"}</span>
          {view === "queue" ? <ReviewProgressTag progress={approval.reviewProgress} /> : <span className="text-xs text-foreground-secondary">{approval.executionOutcome}</span>}
        </div>
        {view === "history" && (
          <dl className="mt-3 grid gap-2 border-t border-border-subtle pt-3 text-xs">
            <div><dt className="font-mono text-[10px] uppercase tracking-wide text-foreground-tertiary">Reviewer</dt><dd className="mt-0.5 text-foreground-secondary">{approval.reviewer ?? "Not recorded"}</dd></div>
            <div><dt className="font-mono text-[10px] uppercase tracking-wide text-foreground-tertiary">Reason</dt><dd className="mt-0.5 text-foreground-secondary">{approval.decisionReason ?? "Not provided"}</dd></div>
            <div><dt className="font-mono text-[10px] uppercase tracking-wide text-foreground-tertiary">Correlation</dt><dd className="mt-0.5 break-all font-mono text-foreground-secondary">{approval.correlationId ?? "Not recorded"}</dd></div>
          </dl>
        )}
      </Link>
    </li>
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
