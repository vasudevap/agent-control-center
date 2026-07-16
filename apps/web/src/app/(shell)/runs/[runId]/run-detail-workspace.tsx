import Link from "next/link";
import { AlertCircle, ArrowLeft, FileText, Info, Workflow } from "lucide-react";
import type { RunRecord } from "../run-data";
import { StatusBadge } from "@/components/badge/status-badge";
import { Breadcrumb } from "@/components/layout/breadcrumb";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function Fact({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-start justify-between gap-3 py-2 text-sm">
      <dt className="text-foreground-secondary">{label}</dt>
      <dd className="break-all text-right font-medium text-foreground">
        {children}
      </dd>
    </div>
  );
}
function SectionCard({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader divided>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="pt-3 sm:pt-3">{children}</CardContent>
    </Card>
  );
}

export function RunDetailWorkspace({
  run,
  requestedId,
}: {
  run?: RunRecord;
  requestedId: string;
}) {
  if (!run)
    return (
      <div className="grid gap-5">
        <Breadcrumb
          items={[{ label: "Runs", href: "/runs" }, { label: requestedId }]}
        />
        <PageHeader
          eyebrow="Run"
          title="Run unavailable"
          identifier={requestedId}
          icon={Workflow}
          description="This identifier is not represented by the local prototype fixtures."
          actions={
            <Button asChild size="sm" variant="secondary">
              <Link href="/runs">
                <ArrowLeft aria-hidden="true" />
                Return to runs
              </Link>
            </Button>
          }
        />
        <Card>
          <CardContent className="p-8 text-center text-sm text-foreground-secondary">
            No service lookup occurred. Choose a fixture from the Runs
            inventory.
          </CardContent>
        </Card>
      </div>
    );

  return (
    <div className="grid gap-5">
      <Breadcrumb
        items={[{ label: "Runs", href: "/runs" }, { label: run.id }]}
      />
      <PageHeader
        eyebrow="Run"
        title={run.agent.name}
        identifier={run.id}
        description={run.summary}
        icon={Workflow}
        meta={<StatusBadge status={run.status} plain />}
        actions={
          <Button asChild size="sm" variant="ghost">
            <Link href="/runs">
              <ArrowLeft aria-hidden="true" />
              Back to runs
            </Link>
          </Button>
        }
      />
      <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
        <strong>Frontend prototype.</strong> This timeline, its logs, and all
        metadata are fictional. No runtime, retry, cancellation, or persistence
        behavior exists.
      </div>
      <div className="grid gap-5 xl:grid-cols-[20rem_minmax(0,1fr)]">
        <aside>
          <div className="sticky top-[calc(var(--statusbar-height)+var(--topbar-height)+1rem)] grid gap-4">
            <SectionCard
              title="At a glance"
              description="Fixture execution and correlation context."
            >
              <dl className="divide-y divide-border-subtle">
                <Fact label="Status">
                  <StatusBadge status={run.status} plain />
                </Fact>
                <Fact label="Agent">
                  <Link
                    className="text-brand hover:underline"
                    href={`/agents/${run.agent.id}`}
                  >
                    {run.agent.name}
                  </Link>
                </Fact>
                <Fact label="Trigger">{run.trigger}</Fact>
                <Fact label="Started">
                  {new Date(run.startedAt).toLocaleString()}
                </Fact>
                <Fact label="Duration">{run.duration}</Fact>
                <Fact label="Retries">{run.retryCount}</Fact>
                <Fact label="Cost estimate">{run.costEstimate}</Fact>
                <Fact label="Correlation">{run.correlationId}</Fact>
              </dl>
            </SectionCard>
            <SectionCard
              title="Related records"
              description="Canonical links exist only for local fixtures."
            >
              <div className="grid gap-2">
                {run.approvalIds.map((id) => (
                  <Link
                    key={id}
                    href={`/approvals/${id}`}
                    className="rounded-atlas-sm border border-border-default bg-surface-secondary px-3 py-2 text-sm text-brand hover:bg-surface-hover"
                  >
                    Approval {id}
                  </Link>
                ))}
                {run.artifactIds.map((id) => (
                  <Link
                    key={id}
                    href={`/artifacts/${id}`}
                    className="rounded-atlas-sm border border-border-default bg-surface-secondary px-3 py-2 text-sm text-brand hover:bg-surface-hover"
                  >
                    Artifact {id}
                  </Link>
                ))}
                {run.approvalIds.length + run.artifactIds.length === 0 && (
                  <p className="text-sm text-foreground-secondary">
                    No related local fixtures.
                  </p>
                )}
              </div>
            </SectionCard>
          </div>
        </aside>
        <main className="grid gap-5">
          {run.error && (
            <Card className="border-error-border bg-error-bg">
              <CardContent className="flex gap-3 p-4">
                <AlertCircle
                  className="mt-0.5 size-5 shrink-0 text-error"
                  aria-hidden="true"
                />
                <div>
                  <h2 className="font-semibold text-error">
                    Normalized fixture error
                  </h2>
                  <p className="mt-1 text-sm text-foreground">
                    {run.error.summary}
                  </p>
                  <p className="mt-2 font-mono text-xs text-error">
                    {run.error.code} · {run.error.category} ·{" "}
                    {run.error.retryable ? "Retryable" : "Not retryable"}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
          <SectionCard
            title="Execution timeline"
            description="Ordered fixture steps with type, state, duration, and redacted summaries."
          >
            <div className="overflow-hidden rounded-atlas-md border border-border-default">
              <Table>
                <caption className="sr-only">Execution steps</caption>
                <TableHeader>
                  <TableRow>
                    <TableHead>Step</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="hidden sm:table-cell">
                      Duration
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {run.steps.map((step) => (
                    <TableRow key={step.id}>
                      <TableCell className="min-w-[15rem] whitespace-normal text-xs">
                        <span className="font-medium text-foreground">
                          {step.name}
                        </span>
                        <span className="mt-0.5 block text-foreground-secondary">
                          {step.summary}
                        </span>
                      </TableCell>
                      <TableCell className="text-xs text-foreground-secondary">
                        {step.type}
                      </TableCell>
                      <TableCell className="text-xs">
                        <StatusBadge
                          status={step.status}
                          plain
                          className="text-xs"
                        />
                      </TableCell>
                      <TableCell className="hidden text-xs text-foreground-secondary sm:table-cell">
                        {step.duration}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </SectionCard>
          <SectionCard
            title="Operational log excerpts"
            description="Fictional troubleshooting context, distinct from audit history."
          >
            <ol className="grid gap-3">
              {run.logs.map((log) => (
                <li
                  key={log.id}
                  className="grid gap-1 rounded-atlas-sm border border-border-default bg-surface-secondary p-3 sm:grid-cols-[8rem_8rem_minmax(0,1fr)]"
                >
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-foreground">
                    {log.severity === "Error" ? (
                      <AlertCircle
                        className="size-3.5 text-error"
                        aria-hidden="true"
                      />
                    ) : log.severity === "Warning" ? (
                      <FileText
                        className="size-3.5 text-warning"
                        aria-hidden="true"
                      />
                    ) : (
                      <Info className="size-3.5 text-info" aria-hidden="true" />
                    )}
                    {log.severity}
                  </span>
                  <span className="font-mono text-xs text-foreground-secondary">
                    {log.component}
                  </span>
                  <span className="text-xs text-foreground-secondary">
                    {log.message}
                  </span>
                </li>
              ))}
            </ol>
          </SectionCard>
        </main>
      </div>
    </div>
  );
}
