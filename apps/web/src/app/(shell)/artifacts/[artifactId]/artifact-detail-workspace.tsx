import Link from "next/link";
import { ArrowLeft, FileWarning, Package, ShieldCheck } from "lucide-react";
import type { ArtifactRecord } from "../artifact-data";
import { StatusBadge } from "@/components/badge/status-badge";
import { Breadcrumb } from "@/components/layout/breadcrumb";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

function Fact({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="grid gap-1 py-2 sm:grid-cols-[9rem_minmax(0,1fr)]">
      <dt className="text-sm text-foreground-secondary">{label}</dt>
      <dd className="break-words text-sm font-medium text-foreground">
        {children}
      </dd>
    </div>
  );
}

export function ArtifactDetailWorkspace({
  artifact,
  requestedId,
}: {
  artifact?: ArtifactRecord;
  requestedId: string;
}) {
  if (!artifact)
    return (
      <div className="grid gap-5">
        <Breadcrumb
          items={[
            { label: "Artifacts", href: "/artifacts" },
            { label: requestedId },
          ]}
        />
        <PageHeader
          eyebrow="Artifact"
          title="Artifact unavailable"
          identifier={requestedId}
          description="This identifier is not represented by the local prototype fixtures."
          icon={Package}
          actions={
            <Button asChild variant="secondary" size="sm">
              <Link href="/artifacts">
                <ArrowLeft aria-hidden="true" />
                Return to artifacts
              </Link>
            </Button>
          }
        />
        <Card>
          <CardContent className="p-8 text-center text-sm text-foreground-secondary">
            No storage lookup occurred. Choose a fixture from the Artifacts
            inventory.
          </CardContent>
        </Card>
      </div>
    );
  const runAvailable = !artifact.runId.startsWith("run-unavailable");
  return (
    <div className="grid gap-5">
      <Breadcrumb
        items={[
          { label: "Artifacts", href: "/artifacts" },
          { label: artifact.id },
        ]}
      />
      <PageHeader
        eyebrow="Artifact"
        title={artifact.name}
        identifier={artifact.id}
        description={artifact.description}
        icon={Package}
        meta={
          <>
            <StatusBadge status={artifact.status} />
            <Badge variant="neutral">{artifact.sensitivity}</Badge>
          </>
        }
        actions={
          <Button asChild variant="ghost" size="sm">
            <Link href="/artifacts">
              <ArrowLeft aria-hidden="true" />
              Back to artifacts
            </Link>
          </Button>
        }
      />
      <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
        <strong>Frontend prototype.</strong> This is metadata-only. Content,
        download, external storage, access control, and persistence are not
        implemented.
      </div>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_20rem]">
        <main className="grid gap-5">
          <Card>
            <CardHeader divided>
              <CardTitle>Safe metadata</CardTitle>
              <CardDescription>
                Fictional output identity and lifecycle context.
              </CardDescription>
            </CardHeader>
            <CardContent className="divide-y divide-border-subtle pt-3 sm:pt-3">
              <dl>
                <Fact label="Type">{artifact.type}</Fact>
                <Fact label="Content type">{artifact.contentType}</Fact>
                <Fact label="Size">{artifact.size}</Fact>
                <Fact label="Created">
                  {new Date(artifact.createdAt).toLocaleString()}
                </Fact>
                <Fact label="Retention">
                  {artifact.retentionUntil
                    ? new Date(artifact.retentionUntil).toLocaleString()
                    : "Not declared"}
                </Fact>
                <Fact label="Checksum">{artifact.checksum}</Fact>
                <Fact label="Storage">{artifact.storage}</Fact>
              </dl>
            </CardContent>
          </Card>
          <Card>
            <CardHeader divided>
              <CardTitle>Preview policy</CardTitle>
              <CardDescription>
                Only non-sensitive fixture summaries are shown.
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-3 sm:pt-3">
              <div className="mb-4 flex gap-3 rounded-atlas-sm border border-warning-border bg-warning-bg p-3">
                <FileWarning
                  className="mt-0.5 size-4 shrink-0 text-warning"
                  aria-hidden="true"
                />
                <p className="text-sm text-foreground">
                  Unsafe inline rendering is disabled. These bullets are
                  authored fixture metadata, not extracted file content.
                </p>
              </div>
              <ul className="grid gap-2">
                {artifact.preview.map((item) => (
                  <li
                    key={item}
                    className="flex gap-2 text-sm text-foreground-secondary"
                  >
                    <ShieldCheck
                      className="mt-0.5 size-4 shrink-0 text-brand"
                      aria-hidden="true"
                    />
                    {item}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </main>
        <aside>
          <div className="sticky top-[calc(var(--statusbar-height)+var(--topbar-height)+1rem)]">
            <Card>
              <CardHeader divided>
                <CardTitle>Lineage</CardTitle>
                <CardDescription>
                  Canonical local relationships only.
                </CardDescription>
              </CardHeader>
              <CardContent className="divide-y divide-border-subtle pt-3 sm:pt-3">
                <dl>
                  <Fact label="Agent">
                    <Link
                      className="text-brand hover:underline"
                      href={`/agents/${artifact.agent.id}`}
                    >
                      {artifact.agent.name}
                    </Link>
                  </Fact>
                  <Fact label="Run">
                    {runAvailable ? (
                      <Link
                        className="text-brand hover:underline"
                        href={`/runs/${artifact.runId}`}
                      >
                        {artifact.runId}
                      </Link>
                    ) : (
                      <>{artifact.runId} (unavailable in prototype)</>
                    )}
                  </Fact>
                  <Fact label="Sensitivity">{artifact.sensitivity}</Fact>
                  <Fact label="Lifecycle">
                    <StatusBadge status={artifact.status} plain />
                  </Fact>
                </dl>
              </CardContent>
            </Card>
          </div>
        </aside>
      </div>
    </div>
  );
}
