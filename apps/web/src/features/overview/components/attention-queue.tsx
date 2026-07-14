"use client";

import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import { CircleAlert, ServerCog, ShieldAlert, TriangleAlert, Circle, Triangle, Diamond } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { EmptyState } from "@/components/state/empty-state";
import { RiskChip, riskRank, type RiskLevel } from "@/components/risk/risk-indicator";
import { getExpiryPresentation } from "@/app/(shell)/approvals/approval-presentation";
import { APPROVAL_FIXTURES, isQueueApproval } from "@/app/(shell)/approvals/approval-data";
import { MOCK_AGENTS, type AgentHealth } from "@/app/(shell)/agents/agent-data";
import { mockAlerts } from "../data/mock-data";

function alertToRisk(severity: "critical" | "warning" | "information"): { risk: RiskLevel; label: string } {
  if (severity === "critical") return { risk: "Critical", label: "Critical" };
  if (severity === "warning") return { risk: "Medium", label: "Warning" };
  return { risk: "Low", label: "Info" };
}

function healthToRisk(health: AgentHealth): { risk: RiskLevel; label: string } {
  return health === "offline" ? { risk: "Critical", label: "Offline" } : { risk: "Medium", label: "Degraded" };
}

type Severity = 0 | 1 | 2 | 3;

interface AttentionItem {
  key: string;
  severity: Severity;
  kind: "approval" | "alert" | "agent";
  icon: LucideIcon;
  title: string;
  subtitle: string;
  meta: string;
  href: string;
  chip: React.ReactNode;
}

function buildAttentionItems(): AttentionItem[] {
  const items: AttentionItem[] = [];

  APPROVAL_FIXTURES.filter(isQueueApproval).forEach((approval) => {
    const expiry = getExpiryPresentation(approval.expiresAt, approval.requestedAt);
    const urgent = expiry.urgency === "imminent" || expiry.urgency === "nearing";
    const severity: Severity = riskRank(approval.risk) >= 3 ? 0 : urgent ? Math.max(0, riskRank(approval.risk) - 1) as Severity : (3 - riskRank(approval.risk)) as Severity;
    items.push({
      key: `approval-${approval.id}`,
      severity,
      kind: "approval",
      icon: ShieldAlert,
      title: approval.action,
      subtitle: `${approval.agent.name} • Approval required`,
      meta: expiry.label,
      href: `/approvals/${approval.id}`,
      chip: <RiskChip risk={approval.risk as RiskLevel} />,
    });
  });

  mockAlerts.forEach((alert) => {
    const severity: Severity = alert.severity === "critical" ? 0 : alert.severity === "warning" ? 2 : 3;
    items.push({
      key: `alert-${alert.id}`,
      severity,
      kind: "alert",
      icon: alert.severity === "critical" ? CircleAlert : TriangleAlert,
      title: alert.title,
      subtitle: `${alert.source} • Alert`,
      meta: alert.timestamp,
      href: alert.sourceAgentId ? `/agents/${alert.sourceAgentId}` : "/alerts",
      chip: <RiskChip {...alertToRisk(alert.severity)} />,
    });
  });

  MOCK_AGENTS.filter((agent) => agent.health === "degraded" || agent.health === "offline").forEach((agent) => {
    const severity: Severity = agent.health === "offline" ? 0 : 2;
    items.push({
      key: `agent-${agent.id}`,
      severity,
      kind: "agent",
      icon: ServerCog,
      title: agent.currentIssue ?? `${agent.name} health is ${agent.health}.`,
      subtitle: `${agent.name} • Agent health`,
      meta: agent.lastRun,
      href: `/agents/${agent.id}`,
      chip: <RiskChip {...healthToRisk(agent.health)} />,
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
 */
export function AttentionQueue() {
  const items = buildAttentionItems();

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between gap-3 space-y-0">
        <div>
          <CardTitle>Attention queue</CardTitle>
          <CardDescription>Approvals, alerts, and agent health ranked by urgency</CardDescription>
        </div>
        <div className="hidden items-center gap-3 text-[11px] text-foreground-tertiary sm:flex">
          <span className="flex items-center gap-1"><Diamond className="size-3 fill-current text-risk-critical" aria-hidden="true" />Critical</span>
          <span className="flex items-center gap-1"><TriangleAlert className="size-3 text-risk-high" aria-hidden="true" />High</span>
          <span className="flex items-center gap-1"><Triangle className="size-3 text-risk-medium" aria-hidden="true" />Medium</span>
          <span className="flex items-center gap-1"><Circle className="size-3 text-risk-low" aria-hidden="true" />Low</span>
        </div>
        <span className="font-mono text-[11px] text-foreground-tertiary">{items.length} items</span>
      </CardHeader>
      {items.length === 0 ? (
        <EmptyState icon={ShieldAlert} title="Nothing needs attention" description="No pending approvals, active alerts, or degraded agents right now." className="py-10" />
      ) : (
        <ul className="divide-y divide-border-subtle">
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.key}>
                <Link href={item.href} className="flex items-start gap-3 px-4 py-3 transition-colors hover:bg-surface-hover sm:px-6">
                  <Icon className="mt-0.5 size-4 shrink-0 text-foreground-tertiary" aria-hidden="true" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-foreground">{item.title}</p>
                    <p className="mt-0.5 truncate text-xs text-foreground-secondary">{item.subtitle}</p>
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-1">
                    {item.chip}
                    <span className="text-[11px] text-foreground-tertiary">{item.meta}</span>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}
