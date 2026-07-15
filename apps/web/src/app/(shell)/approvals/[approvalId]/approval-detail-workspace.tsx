"use client";

import * as React from "react";
import Link from "next/link";
import { AlertTriangle, ArrowLeft, FileWarning, History, ShieldAlert } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { RiskChip, type RiskLevel } from "@/components/risk/risk-indicator";
import { StateChip, ReviewProgressTag, ExpiryLabel } from "../approval-badges";
import { applySimulatedDecision, canSimulateDecision, expireDuringSimulatedReview, isExpiredAt, requiresSimulatedStepUp, type SimulatedDecision } from "../approval-prototype-controller";
import type { ApprovalRecord } from "../approval-data";

const returnPath = () =>
  typeof window === "undefined" ? "/approvals?view=queue" : new URLSearchParams(window.location.search).get("from")?.startsWith("/approvals") ? new URLSearchParams(window.location.search).get("from")! : "/approvals?view=queue";

function Notice() {
  return (
    <Card className="border-info-border bg-info-bg">
      <CardContent className="flex gap-2.5 p-3 text-xs leading-relaxed text-info">
        <AlertTriangle className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
        <p><strong>Frontend prototype.</strong> Any decision is a session-only local simulation. It does not affect a real agent, runtime, service, policy engine, audit system, or persisted record.</p>
      </CardContent>
    </Card>
  );
}

function InfoCard({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader divided><CardTitle>{title}</CardTitle>{description && <CardDescription>{description}</CardDescription>}</CardHeader>
      <CardContent className="pt-3 sm:pt-3">{children}</CardContent>
    </Card>
  );
}

function Details({ items }: { items: Record<string, React.ReactNode> }) {
  return (
    <dl className="grid gap-4 sm:grid-cols-2">
      {Object.entries(items).map(([label, value]) => (
        <div key={label} className="grid gap-1">
          <dt className="font-mono text-[10px] font-semibold uppercase tracking-wide text-foreground-tertiary">{label}</dt>
          <dd className="text-sm leading-relaxed text-foreground">{value}</dd>
        </div>
      ))}
    </dl>
  );
}

export function ApprovalDetailWorkspace({ approval, presentationState = "ready", now = Date.now }: { approval?: ApprovalRecord; presentationState?: "ready" | "loading" | "error"; now?: () => number }) {
  const [current, setCurrent] = React.useState(approval);
  const [decision, setDecision] = React.useState<SimulatedDecision | null>(null);
  const [reason, setReason] = React.useState("");
  const [reasonError, setReasonError] = React.useState("");
  const [stepUp, setStepUp] = React.useState(false);
  const [announcement, setAnnouncement] = React.useState("");
  const back = React.useMemo(() => returnPath(), []);
  const unavailableExplanationId = React.useId();

  if (presentationState === "loading") return <div className="grid gap-4"><Skeleton className="h-16 w-1/2" /><Skeleton className="h-96 w-full" /></div>;
  if (presentationState === "error" || !current) {
    return (
      <Card className="border-error-border bg-error-bg">
        <CardContent className="p-6">
          <h1 className="text-lg font-semibold text-error">Approval unavailable</h1>
          <p className="mt-2 text-sm text-error">This fictional approval cannot be displayed. No real approval service was contacted.</p>
          <Button asChild className="mt-4" variant="secondary"><Link href="/approvals?view=queue">Return to Queue</Link></Button>
        </CardContent>
      </Card>
    );
  }

  const actionable = current.state === "Pending";
  const approveAvailable = canSimulateDecision(current, "approve");
  const stepUpRequired = requiresSimulatedStepUp(current);
  const reasonRequired = decision === "reject" || decision === "request-clarification" || (decision === "approve" && (current.risk === "High" || current.risk === "Critical"));
  const decisionLabel = decision === "approve" ? "approval" : decision === "reject" ? "rejection" : "clarification request";
  const inputLabel = decision === "request-clarification" ? "Clarification question" : "Reason";

  const open = (next: SimulatedDecision) => { setDecision(next); setReasonError(""); setStepUp(false); setReason(""); };
  const confirm = () => {
    if (!decision) return;
    if (isExpiredAt(current, now())) {
      setCurrent(expireDuringSimulatedReview(current, now()));
      setAnnouncement("Prototype state updated: this approval expired before confirmation. No simulated decision was applied.");
      setDecision(null);
      setReason("");
      return;
    }
    if (reasonRequired && !reason.trim()) {
      setReasonError(
        decision === "reject"
          ? "A reason is required to simulate rejection."
          : decision === "request-clarification"
            ? "A clarification question is required."
            : "Explanatory text is required to simulate approval at this risk level."
      );
      return;
    }
    if (stepUpRequired && !stepUp) return;
    setCurrent(applySimulatedDecision(current, decision, reason));
    setAnnouncement(`Prototype state updated: simulated ${decisionLabel}. No real action was recorded or executed.`);
    setDecision(null);
    setReason("");
  };

  const DecisionCard = (
    <Card className="overflow-hidden" role="region" aria-label="Decision controls" aria-describedby={!approveAvailable && actionable ? unavailableExplanationId : undefined}>
      <CardHeader className="border-b border-border-default bg-surface-secondary">
        <CardTitle>Decide</CardTitle>
        <CardDescription>Controls change only this local screen state for the current session.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-2.5 pt-3 sm:pt-3">
        <Button onClick={() => open("approve")} disabled={!actionable || !approveAvailable}>Simulate approval</Button>
        <Button variant="destructive" onClick={() => open("reject")} disabled={!actionable}>Simulate rejection</Button>
        <Button variant="secondary" onClick={() => open("request-clarification")} disabled={!actionable}>Simulate clarification request</Button>
        {!approveAvailable && actionable && (
          <p role="status" className="flex items-start gap-1.5 text-xs text-error">
            <FileWarning className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
            Approval unavailable: required fictional evidence is incomplete.
          </p>
        )}
        {!actionable && (
          <p className="flex items-start gap-1.5 text-xs text-foreground-secondary">
            <History className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
            This approval is historical or no longer actionable in the prototype.
          </p>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className={`flex min-w-0 flex-col gap-5 ${actionable ? "pb-20 xl:pb-0" : ""}`}>
      <PageHeader
        eyebrow="Approval"
        title={current.agent.name}
        identifier={current.id}
        description={current.action}
        icon={ShieldAlert}
        meta={<><RiskChip risk={current.risk as RiskLevel} /><StateChip state={current.state} className="text-xs" />{actionable && <ReviewProgressTag progress={current.reviewProgress} />}</>}
        actions={<Button asChild variant="ghost" size="sm"><Link href={back}><ArrowLeft className="size-4" aria-hidden="true" />Return to Queue</Link></Button>}
      />
      <Notice />
      <p className="sr-only" role="status" aria-live="polite" aria-atomic="true">{announcement}</p>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_20rem]">
        <div className="grid gap-5">
          <InfoCard title="Proposed action" description="The exact fictional action being reviewed.">
            <Details items={{ Action: current.action, Target: current.target, Consequence: current.consequence, "Affected scope": current.scope, Environment: current.environment }} />
          </InfoCard>
          <InfoCard title="Policy and governance rationale" description="Why an operator review is required.">
            <Details items={{ "Governing policy": current.policy, "Review rationale": current.policyReason }} />
          </InfoCard>
          <InfoCard title="Evidence and context" description="External material is separated from system metadata.">
            <div className="grid gap-3">
              <div className="rounded-atlas-sm border border-border-default bg-surface-secondary p-3.5">
                <Details items={{ "Evidence source": current.evidence.source, Provenance: current.evidence.provenance }} />
              </div>
              <div className="rounded-atlas-sm border border-warning-border bg-warning-bg p-3.5">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-warning">Untrusted evidence preview</p>
                <p className="mt-2 text-sm leading-relaxed text-foreground">{current.evidence.preview}</p>
              </div>
              {!current.evidence.complete && (
                <div className="rounded-atlas-sm border border-error-border bg-error-bg p-3.5">
                  <div className="flex gap-2">
                    <FileWarning className="mt-0.5 size-4 shrink-0 text-error" aria-hidden="true" />
                    <div>
                      <h3 className="font-semibold text-error">Approval unavailable</h3>
                      <p id={unavailableExplanationId} className="mt-1 text-sm text-error">Missing fictional evidence: {current.evidence.missing?.join(", ")}.</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </InfoCard>
          <InfoCard title="Activity" description="Local prototype activity is explicitly labeled.">
            <ol className="grid gap-4 border-l border-border-default pl-5">
              {current.activity.map((item, index) => (
                <li key={`${item.at}-${index}`} className="relative">
                  <span className="absolute -left-[1.6rem] top-1.5 size-2 rounded-full border-2 border-surface bg-brand" />
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-medium text-foreground">{item.actor}</p>
                    {item.simulated && <Badge variant="neutral">Simulated</Badge>}
                  </div>
                  <p className="mt-1 text-sm text-foreground-secondary">{item.detail}</p>
                  <time className="text-xs text-foreground-tertiary">{item.at}</time>
                </li>
              ))}
            </ol>
          </InfoCard>

          {/* Mobile/tablet: decision card appears after evidence, in normal reading order. */}
          <div className="xl:hidden">{DecisionCard}</div>
        </div>

        <aside className="hidden xl:grid xl:content-start xl:gap-4">
          <div className="sticky top-[calc(var(--statusbar-height)+var(--topbar-height)+1rem)] grid gap-4">
            {DecisionCard}
            <InfoCard title="Request context">
              <Details items={{ Agent: <Link className="text-brand hover:underline" href={`/agents/${current.agent.id}`}>{current.agent.name}</Link>, Run: `${current.runId} (unavailable in prototype)`, Artifact: current.artifact ? `${current.artifact.name} (${current.artifact.id}; unavailable in prototype)` : "No related artifact in this fixture", Requested: new Date(current.requestedAt).toLocaleString(), Expiry: <ExpiryLabel approval={current} />, "Decision time": current.decidedAt ? new Date(current.decidedAt).toLocaleString() : "Not decided", Reviewer: current.reviewer ?? "Not recorded", "Decision reason": current.decisionReason ?? "Not provided", Correlation: current.correlationId ?? "Not recorded", "Execution outcome": current.executionOutcome }} />
            </InfoCard>
            {current.executionOutcome === "Indeterminate" && (
              <Card className="border-warning-border bg-warning-bg">
                <CardContent className="p-3.5"><h2 className="text-sm font-semibold text-warning">Indeterminate outcome</h2><p className="mt-1 text-xs text-foreground">Unresolved locally. No real reconciliation occurred. Retry is blocked pending investigation.</p></CardContent>
              </Card>
            )}
          </div>
        </aside>

        {/* Context card repeated in normal flow below the mobile decision card. */}
        <div className="xl:hidden">
          <InfoCard title="Request context">
            <Details items={{ Agent: <Link className="text-brand hover:underline" href={`/agents/${current.agent.id}`}>{current.agent.name}</Link>, Run: `${current.runId} (unavailable in prototype)`, Artifact: current.artifact ? `${current.artifact.name} (${current.artifact.id}; unavailable in prototype)` : "No related artifact in this fixture", Requested: new Date(current.requestedAt).toLocaleString(), Expiry: <ExpiryLabel approval={current} />, "Decision time": current.decidedAt ? new Date(current.decidedAt).toLocaleString() : "Not decided", Reviewer: current.reviewer ?? "Not recorded", "Decision reason": current.decisionReason ?? "Not provided", Correlation: current.correlationId ?? "Not recorded", "Execution outcome": current.executionOutcome }} />
          </InfoCard>
        </div>
        {current.executionOutcome === "Indeterminate" && (
          <div className="xl:hidden" role="note" aria-label="Mobile indeterminate guidance">
            <Card className="border-warning-border bg-warning-bg">
              <CardContent className="p-3.5"><h2 className="text-sm font-semibold text-warning">Indeterminate outcome</h2><p className="mt-1 text-xs text-foreground">Unresolved locally. No real reconciliation occurred. Retry is blocked pending investigation.</p></CardContent>
            </Card>
          </div>
        )}
      </section>

      {/* Sticky mobile decision bar: a reachable shortcut to the same dialog logic; the full card above remains the primary, evidence-preceded entry point. */}
      {actionable && (
        <div className="fixed inset-x-0 bottom-0 z-30 flex gap-2 border-t border-border-default bg-surface p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] shadow-atlas-md xl:hidden">
          <Button className="flex-1" variant="destructive" size="sm" onClick={() => open("reject")}>Reject</Button>
          <Button className="flex-1" size="sm" onClick={() => open("approve")} disabled={!approveAvailable}>Approve</Button>
        </div>
      )}

      <Dialog open={decision !== null} onOpenChange={(isOpen) => { if (!isOpen) setDecision(null); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Simulate {decisionLabel}</DialogTitle>
            <DialogDescription>This changes only the local fixture in this browser session. It will not authorize, execute, record, or persist anything.</DialogDescription>
          </DialogHeader>
          {decision && (
            <div className="grid gap-4">
              <div className="grid gap-2 rounded-atlas-sm border border-border-default bg-surface-secondary p-3 text-sm">
                <p className="font-mono text-xs text-foreground-tertiary">{current.id}</p>
                <p className="font-medium text-foreground">{current.action}</p>
                <Details items={{ Target: current.target, Consequence: current.consequence, Risk: <RiskChip risk={current.risk as RiskLevel} />, Expiry: <ExpiryLabel approval={current} /> }} />
              </div>
              <label className="grid gap-1 text-sm font-medium text-foreground">
                {inputLabel} {reasonRequired ? "(required)" : "(optional)"}
                <textarea value={reason} onChange={(e) => { setReason(e.target.value); setReasonError(""); }} aria-invalid={Boolean(reasonError)} className="min-h-24 rounded-atlas-sm border border-border-default bg-surface px-3 py-2 text-sm font-normal" />
              </label>
              {reasonError && <p role="alert" className="text-sm text-error">{reasonError}</p>}
              {stepUpRequired && (
                <label className="flex gap-3 rounded-atlas-sm border border-warning-border bg-warning-bg p-3 text-sm">
                  <input aria-label="Simulated step-up confirmation" type="checkbox" checked={stepUp} onChange={(e) => setStepUp(e.target.checked)} className="mt-1 size-4" />
                  <span><strong>Simulated step-up confirmation.</strong> This does not authenticate you or affect a real system.</span>
                </label>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="secondary" onClick={() => setDecision(null)}>Cancel</Button>
            <Button variant={decision === "reject" ? "destructive" : "primary"} onClick={confirm} disabled={stepUpRequired && !stepUp}>Confirm simulated {decisionLabel}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
