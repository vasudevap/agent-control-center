"use client";

import Link from "next/link";
import {
  ShieldAlert,
  Circle,
  Triangle,
  TriangleAlert,
  Diamond,
} from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { EmptyState } from "@/components/state/empty-state";
import {
  RiskChip,
  riskRank,
  type RiskLevel,
} from "@/components/risk/risk-indicator";
import { getExpiryPresentation } from "@/app/(shell)/approvals/approval-presentation";
import {
  isQueueApproval,
  type ApprovalRecord,
} from "@/app/(shell)/approvals/approval-data";
import { MOCK_AGENTS, type AgentHealth } from "@/app/(shell)/agents/agent-data";
import { cn } from "@/lib/utils";
import { mockAlerts } from "../data/mock-data";

function alertToRisk(
  severity: "critical" | "high" | "warning" | "information",
): { risk: RiskLevel; label: string } {
  if (severity === "critical") return { risk: "Critical", label: "Critical" };
  if (severity === "high") return { risk: "High", label: "High" };
  if (severity === "warning") return { risk: "Medium", label: "Warning" };
  return { risk: "Low", label: "Info" };
}

function healthToRisk(health: AgentHealth): { risk: RiskLevel; label: string } {
  return health === "offline"
    ? { risk: "Critical", label: "Offline" }
    : { risk: "Medium", label: "Degraded" };
}

type Severity = 0 | 1 | 2 | 3;
type ItemKind = "Approval" | "Alert" | "Agent health";
type MetaUrgency = "imminent" | "nearing";

interface AttentionItem {
  key: string;
  severity: Severity;
  risk: RiskLevel;
  chipLabel: string;
  title: string;
  kind: ItemKind;
  source: string;
  meta: string;
  metaUrgency?: MetaUrgency;
  href: string;
}

function buildAttentionItems(approvals: ApprovalRecord[]): AttentionItem[] {
  const items: AttentionItem[] = [];

  approvals.filter(isQueueApproval).forEach((approval) => {
    const expiry = getExpiryPresentation(
      approval.expiresAt,
      approval.requestedAt,
    );
    const urgent =
      expiry.urgency === "imminent" || expiry.urgency === "nearing";
    const severity: Severity =
      riskRank(approval.risk) >= 3
        ? 0
        : urgent
          ? (Math.max(0, riskRank(approval.risk) - 1) as Severity)
          : ((3 - riskRank(approval.risk)) as Severity);
    items.push({
      key: `approval-${approval.id}`,
      severity,
      risk: approval.risk as RiskLevel,
      chipLabel: approval.risk,
      title: approval.action,
      kind: "Approval",
      source: approval.agent.name,
      meta: expiry.label,
      metaUrgency:
        expiry.urgency === "imminent" || expiry.urgency === "nearing"
          ? expiry.urgency
          : undefined,
      href: `/approvals/${approval.id}`,
    });
  });

  mockAlerts.forEach((alert) => {
    const severity: Severity =
      alert.severity === "critical"
        ? 0
        : alert.severity === "high"
          ? 1
          : alert.severity === "warning"
            ? 2
            : 3;
    const { risk, label } = alertToRisk(alert.severity);
    items.push({
      key: `alert-${alert.id}`,
      severity,
      risk,
      chipLabel: label,
      title: alert.title,
      kind: "Alert",
      source: alert.source,
      meta: alert.timestamp,
      href: `/alerts?alert=${alert.id}`,
    });
  });

  MOCK_AGENTS.filter(
    (agent) => agent.health === "degraded" || agent.health === "offline",
  ).forEach((agent) => {
    const severity: Severity = agent.health === "offline" ? 0 : 2;
    const { risk, label } = healthToRisk(agent.health);
    items.push({
      key: `agent-${agent.id}`,
      severity,
      risk,
      chipLabel: label,
      title: agent.currentIssue ?? `${agent.name} health is ${agent.health}.`,
      kind: "Agent health",
      source: agent.name,
      meta: agent.lastRun,
      href: `/agents/${agent.id}`,
    });
  });

  return items.sort((a, b) => a.severity - b.severity);
}

/**
 * The baseline Overview presents Pending Approvals, Alerts, and Fleet
 * Health as three separate cards competing for attention, even though
 * the design principles state a primary screen should answer one
 * operational question ("what requires my attention right now?").
 * This merges all three attention-worthy signal types into one ranked
 * feed answering that question directly. Fleet Health remains
 * available as its own denser table below for full-roster scanning;
 * this panel is specifically the triage view.
 *
 * Every entry is a link to its real destination. None decide anything
 * inline: approvals route to canonical Approval Detail, matching the
 * hard product requirement that decisions occur only there.
 *
 * Header is the shaded/"actionable" treatment: every row here routes
 * somewhere, so the card is a queue you act on, not a status you read.
 * The leading icon per row is the severity indicator itself (not a
 * separate "kind" icon) since kind now has its own labeled slot on the
 * trailing edge, mirroring how Agents/Approvals give every fact its
 * own recognizable column rather than folding it into freeform text.
 *
 * This list stays fixed-order by urgency rather than gaining the
 * sortable columns and filters Agents/Approvals have. Those two pages
 * are full inventories of one entity type, where letting the operator
 * pick an order is the point. This panel is a small, already-triaged
 * feed across three unrelated entity types; the ranking is the value
 * it adds, so it is not exposed as a user-controlled sort.
 */
export function AttentionQueue({ approvals }: { approvals: ApprovalRecord[] }) {
  const items = buildAttentionItems(approvals);

  return (
    <Card>
      <CardHeader
        actionable
        className="flex-row items-start justify-between gap-3 space-y-0"
      >
        <div>
          <CardTitle>Attention queue</CardTitle>
          <CardDescription>
            Approvals, alerts, and agent health ranked by urgency
          </CardDescription>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className="font-mono text-[11px] text-foreground-tertiary">
            {items.length} items
          </span>
          <div className="hidden items-center gap-2.5 text-[10px] text-foreground-tertiary sm:flex">
            <span className="flex items-center gap-1">
              <Diamond
                className="size-3 fill-current text-risk-critical"
                aria-hidden="true"
              />
              Critical
            </span>
            <span className="flex items-center gap-1">
              <TriangleAlert
                className="size-3 text-risk-high"
                aria-hidden="true"
              />
              High
            </span>
            <span className="flex items-center gap-1">
              <Triangle
                className="size-3 text-risk-medium"
                aria-hidden="true"
              />
              Medium
            </span>
            <span className="flex items-center gap-1">
              <Circle className="size-3 text-risk-low" aria-hidden="true" />
              Low
            </span>
          </div>
        </div>
      </CardHeader>
      {items.length === 0 ? (
        <EmptyState
          icon={ShieldAlert}
          title="Nothing needs attention"
          description="No pending approvals, active alerts, or degraded agents right now."
          className="py-10"
        />
      ) : (
        <ul className="divide-y divide-border-subtle">
          {items.map((item) => (
            <li key={item.key}>
              <Link
                href={item.href}
                className="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-hover sm:px-6"
              >
                <RiskChip risk={item.risk} label={item.chipLabel} iconOnly />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-foreground">
                    {item.title}
                  </p>
                  <p className="mt-0.5 truncate text-xs text-foreground-secondary">
                    {item.source}
                  </p>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-0.5">
                  <span className="font-mono text-[10px] font-medium uppercase tracking-wide text-foreground-tertiary">
                    {item.kind}
                  </span>
                  <span
                    className={cn(
                      "text-[11px]",
                      item.metaUrgency === "imminent"
                        ? "font-semibold text-error"
                        : item.metaUrgency === "nearing"
                          ? "font-semibold text-warning"
                          : "text-foreground-tertiary",
                    )}
                  >
                    {item.meta}
                  </span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
