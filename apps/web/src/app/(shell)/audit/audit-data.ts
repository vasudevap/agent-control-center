import type { AtlasStatus } from "@/components/badge/status-badge";

export type AuditResult = Extract<
  AtlasStatus,
  "approved" | "rejected" | "succeeded" | "failed"
>;
export type AuditAction = string;
export type AuditResourceType = string;

export interface AuditEvent {
  id: string;
  occurredAt: string;
  actor: string;
  actorType: "Human" | "System fixture" | string;
  action: AuditAction;
  result: AuditResult;
  resourceType: AuditResourceType;
  resourceId: string;
  summary: string;
  reason: string;
  correlationId: string;
  relatedHref?: string;
}

export const AUDIT_FIXTURES: AuditEvent[] = [
  {
    id: "aud-2026-0716-018",
    occurredAt: "2026-07-16T12:41:00.000Z",
    actor: "Maya Chen",
    actorType: "Human",
    action: "Approval decision",
    result: "approved",
    resourceType: "Approval",
    resourceId: "apr-2026-004",
    summary: "Approved a fictional internal operations summary.",
    reason: "Fixture evidence satisfied the declared policy requirements.",
    correlationId: "corr-audit-0716-018",
    relatedHref: "/approvals/apr-2026-004",
  },
  {
    id: "aud-2026-0716-017",
    occurredAt: "2026-07-16T11:02:00.000Z",
    actor: "Policy evaluator fixture",
    actorType: "System fixture",
    action: "Policy evaluation",
    result: "succeeded",
    resourceType: "Policy",
    resourceId: "P-214",
    summary: "Evaluated a fictional step-up confirmation requirement.",
    reason: "The fixture request was categorized as Critical.",
    correlationId: "corr-audit-0716-017",
  },
  {
    id: "aud-2026-0716-016",
    occurredAt: "2026-07-16T09:26:00.000Z",
    actor: "Jon Bell",
    actorType: "Human",
    action: "Agent control",
    result: "succeeded",
    resourceType: "Agent",
    resourceId: "agent-support-drafts",
    summary: "Simulated pausing the Support Draft Agent prototype.",
    reason: "Local demonstration of a governed control boundary.",
    correlationId: "corr-audit-0716-016",
    relatedHref: "/agents/agent-support-drafts",
  },
  {
    id: "aud-2026-0715-044",
    occurredAt: "2026-07-15T20:13:00.000Z",
    actor: "Ari Singh",
    actorType: "Human",
    action: "Approval decision",
    result: "rejected",
    resourceType: "Approval",
    resourceId: "apr-2026-003",
    summary: "Rejected a fictional connector evidence export.",
    reason: "Source provenance was incomplete in the fixture.",
    correlationId: "corr-run-0705-011",
    relatedHref: "/approvals/apr-2026-003",
  },
  {
    id: "aud-2026-0715-041",
    occurredAt: "2026-07-15T18:08:00.000Z",
    actor: "Artifact viewer fixture",
    actorType: "System fixture",
    action: "Fixture access",
    result: "succeeded",
    resourceType: "Artifact",
    resourceId: "art-2026-0712-001",
    summary: "Displayed safe fictional artifact metadata.",
    reason: "Content and external storage remained unavailable.",
    correlationId: "corr-run-0712-001",
    relatedHref: "/artifacts/art-2026-0712-001",
  },
  {
    id: "aud-2026-0714-029",
    occurredAt: "2026-07-14T14:32:00.000Z",
    actor: "Policy evaluator fixture",
    actorType: "System fixture",
    action: "Policy evaluation",
    result: "failed",
    resourceType: "Policy",
    resourceId: "P-118",
    summary: "Could not evaluate a fictional retention rule.",
    reason: "Required fixture provenance was unavailable.",
    correlationId: "corr-audit-0714-029",
  },
];
