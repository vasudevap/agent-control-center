"use client";

import * as React from "react";
import Link from "next/link";
import { FilterX, Package } from "lucide-react";
import {
  ARTIFACT_FIXTURES,
  type ArtifactRecord,
  type ArtifactStatus,
  type ArtifactType,
} from "./artifact-data";
import { StatusBadge } from "@/components/badge/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/state/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SearchField } from "@/components/ui/search-field";
import {
  getAriaSort,
  SortHeader,
  type SortDirection,
} from "@/components/ui/sort-header";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type SortKey =
  | "status"
  | "artifact"
  | "type"
  | "agent"
  | "created"
  | "retention";
const SELECT_CLASS =
  "h-9 rounded-atlas-md border border-border-default bg-surface px-3 text-sm text-foreground outline-none hover:border-border-strong focus:border-brand";
const STATUS_RANK: Record<ArtifactStatus, number> = {
  "review-required": 0,
  available: 1,
  expired: 2,
};

function filterArtifacts(
  artifacts: ArtifactRecord[],
  query: string,
  status: ArtifactStatus | "all",
  type: ArtifactType | "all",
) {
  const q = query.trim().toLowerCase();
  return artifacts.filter(
    (artifact) =>
      (!q ||
        [
          artifact.id,
          artifact.name,
          artifact.description,
          artifact.agent.name,
          artifact.runId,
        ]
          .join(" ")
          .toLowerCase()
          .includes(q)) &&
      (status === "all" || artifact.status === status) &&
      (type === "all" || artifact.type === type),
  );
}
function sortArtifacts(
  artifacts: ArtifactRecord[],
  sort: SortKey,
  direction: SortDirection,
) {
  const mul = direction === "asc" ? 1 : -1;
  return [...artifacts].sort((a, b) => {
    if (sort === "status")
      return (STATUS_RANK[a.status] - STATUS_RANK[b.status]) * mul;
    if (sort === "artifact") return a.name.localeCompare(b.name) * mul;
    if (sort === "type") return a.type.localeCompare(b.type) * mul;
    if (sort === "agent") return a.agent.name.localeCompare(b.agent.name) * mul;
    if (sort === "retention")
      return (
        (+new Date(a.retentionUntil ?? "9999-01-01") -
          +new Date(b.retentionUntil ?? "9999-01-01")) *
        mul
      );
    return (+new Date(a.createdAt) - +new Date(b.createdAt)) * mul;
  });
}
function Pair({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="grid gap-0.5">
      <dt className="font-mono text-[10px] uppercase tracking-wider text-foreground-tertiary">
        {label}
      </dt>
      <dd className="text-sm text-foreground">{children}</dd>
    </div>
  );
}

export function ArtifactsWorkspace({
  artifacts = ARTIFACT_FIXTURES,
}: {
  artifacts?: ArtifactRecord[];
}) {
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState<ArtifactStatus | "all">("all");
  const [type, setType] = React.useState<ArtifactType | "all">("all");
  const [sort, setSort] = React.useState<SortKey>("created");
  const [direction, setDirection] = React.useState<SortDirection>("desc");
  const visible = sortArtifacts(
    filterArtifacts(artifacts, query, status, type),
    sort,
    direction,
  );
  const hasFilters = Boolean(query || status !== "all" || type !== "all");
  const clear = () => {
    setQuery("");
    setStatus("all");
    setType("all");
  };
  const onSort = (next: SortKey) => {
    if (next === sort)
      setDirection((value) => (value === "asc" ? "desc" : "asc"));
    else {
      setSort(next);
      setDirection("asc");
    }
  };

  return (
    <div className="flex flex-col gap-5">
      <PageHeader
        eyebrow="Outputs"
        title="Artifacts"
        description="Review safe metadata and lineage for fictional outputs produced by agent runs."
        icon={Package}
      />
      <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
        <strong>Frontend prototype.</strong> Artifact content and external
        storage are unavailable. No file is downloaded, opened, or persisted.
      </div>
      <div className="flex flex-col gap-3 rounded-atlas-lg border border-border-default bg-surface p-3 sm:flex-row sm:flex-wrap sm:items-center">
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Search artifacts"
          className="w-full sm:max-w-sm"
        />
        <label htmlFor="artifact-status" className="sr-only">
          Status
        </label>
        <select
          id="artifact-status"
          className={SELECT_CLASS}
          value={status}
          onChange={(event) =>
            setStatus(event.target.value as ArtifactStatus | "all")
          }
        >
          <option value="all">All statuses</option>
          <option value="available">Available</option>
          <option value="review-required">Review required</option>
          <option value="expired">Expired</option>
        </select>
        <label htmlFor="artifact-type" className="sr-only">
          Type
        </label>
        <select
          id="artifact-type"
          className={SELECT_CLASS}
          value={type}
          onChange={(event) =>
            setType(event.target.value as ArtifactType | "all")
          }
        >
          <option value="all">All types</option>
          {[...new Set(artifacts.map((artifact) => artifact.type))].map(
            (value) => (
              <option key={value}>{value}</option>
            ),
          )}
        </select>
        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={clear}>
            <FilterX aria-hidden="true" />
            Clear filters
          </Button>
        )}
        <p className="text-xs text-foreground-secondary sm:ml-auto">
          {visible.length} of {artifacts.length} fictional artifacts
        </p>
      </div>
      {visible.length === 0 ? (
        <Card>
          <EmptyState
            icon={Package}
            title={
              hasFilters
                ? "No artifacts match these filters"
                : "No artifacts yet"
            }
            description={
              hasFilters
                ? "Clear filters to restore the fixture catalog."
                : "Artifact metadata will appear when fixtures are added."
            }
            action={
              hasFilters ? (
                <Button variant="secondary" size="sm" onClick={clear}>
                  Clear filters
                </Button>
              ) : undefined
            }
          />
        </Card>
      ) : (
        <>
          <Card className="hidden overflow-hidden md:block">
            <Table>
              <caption className="sr-only">Artifacts inventory</caption>
              <TableHeader>
                <TableRow>
                  <TableHead
                    aria-sort={getAriaSort(sort === "status", direction)}
                  >
                    <SortHeader
                      label="Status"
                      sortKey="status"
                      active={sort === "status"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    aria-sort={getAriaSort(sort === "artifact", direction)}
                  >
                    <SortHeader
                      label="Artifact"
                      sortKey="artifact"
                      active={sort === "artifact"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    aria-sort={getAriaSort(sort === "type", direction)}
                  >
                    <SortHeader
                      label="Type"
                      sortKey="type"
                      active={sort === "type"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    aria-sort={getAriaSort(sort === "agent", direction)}
                    className="hidden lg:table-cell"
                  >
                    <SortHeader
                      label="Agent"
                      sortKey="agent"
                      active={sort === "agent"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    aria-sort={getAriaSort(sort === "created", direction)}
                  >
                    <SortHeader
                      label="Created"
                      sortKey="created"
                      active={sort === "created"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    aria-sort={getAriaSort(sort === "retention", direction)}
                  >
                    <SortHeader
                      label="Retention"
                      sortKey="retention"
                      active={sort === "retention"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {visible.map((artifact) => (
                  <TableRow key={artifact.id} className="relative">
                    <TableCell className="text-xs">
                      <StatusBadge
                        status={artifact.status}
                        plain
                        className="text-xs"
                      />
                    </TableCell>
                    <TableCell className="min-w-[18rem] text-xs">
                      <Link
                        href={`/artifacts/${artifact.id}`}
                        className="relative z-10 block font-medium after:absolute after:inset-0 after:content-[''] hover:text-brand"
                      >
                        <span>{artifact.name}</span>
                        <span className="mt-0.5 block font-mono text-[10px] font-normal text-foreground-tertiary">
                          {artifact.id}
                        </span>
                      </Link>
                    </TableCell>
                    <TableCell className="text-xs text-foreground-secondary">
                      {artifact.type}
                    </TableCell>
                    <TableCell className="hidden text-xs text-foreground-secondary lg:table-cell">
                      {artifact.agent.name}
                    </TableCell>
                    <TableCell className="text-xs text-foreground-secondary">
                      {new Date(artifact.createdAt).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-xs text-foreground-secondary">
                      {artifact.retentionUntil
                        ? new Date(artifact.retentionUntil).toLocaleDateString()
                        : "Not declared"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
          <ul className="grid gap-3 md:hidden">
            {visible.map((artifact) => (
              <li key={artifact.id}>
                <Card className="relative">
                  <CardContent className="grid gap-4 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <Link
                        href={`/artifacts/${artifact.id}`}
                        className="font-medium text-foreground after:absolute after:inset-0 after:content-['']"
                      >
                        {artifact.name}
                        <span className="mt-1 block font-mono text-[10px] text-foreground-tertiary">
                          {artifact.id}
                        </span>
                      </Link>
                      <StatusBadge status={artifact.status} />
                    </div>
                    <p className="text-sm text-foreground-secondary">
                      {artifact.description}
                    </p>
                    <dl className="grid grid-cols-2 gap-3">
                      <Pair label="Type">{artifact.type}</Pair>
                      <Pair label="Sensitivity">
                        <Badge variant="neutral">{artifact.sensitivity}</Badge>
                      </Pair>
                      <Pair label="Agent">{artifact.agent.name}</Pair>
                      <Pair label="Created">
                        {new Date(artifact.createdAt).toLocaleDateString()}
                      </Pair>
                    </dl>
                  </CardContent>
                </Card>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
