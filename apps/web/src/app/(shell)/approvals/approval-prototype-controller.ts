import type { ApprovalRecord } from "./approval-data";

export type SimulatedDecision = "approve" | "reject" | "request-clarification";

export function requiresSimulatedStepUp(approval: ApprovalRecord) {
  return approval.risk === "Critical" || approval.risk === "High";
}

export function canSimulateDecision(approval: ApprovalRecord, decision: SimulatedDecision) {
  if (approval.state !== "Pending") return false;
  if (decision === "approve") return approval.evidence.complete;
  return true;
}

export function isExpiredAt(approval: ApprovalRecord, referenceTime: number) {
  return Boolean(approval.expiresAt && new Date(approval.expiresAt).getTime() <= referenceTime);
}

export function expireDuringSimulatedReview(approval: ApprovalRecord, referenceTime: number): ApprovalRecord {
  const decidedAt = new Date(referenceTime).toISOString();
  const at = new Date(referenceTime).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
  return {
    ...approval,
    state: "Expired",
    executionOutcome: "Not available",
    decidedAt,
    reviewer: "Prototype review clock",
    correlationId: `corr-sim-expiry-${approval.id}`,
    activity: [
      ...approval.activity,
      {
        at,
        actor: "Prototype review clock",
        detail: "Detected expiry before simulated decision confirmation. No decision was applied.",
        simulated: true,
      },
    ],
  };
}

/**
 * Request clarification never changes approval state (it remains
 * Pending) and never extends expiry, per HA-FR-027/028 and
 * architecture/13-human-approvals.md section 8.5. Only review
 * progress moves, to "Awaiting information".
 */
export function applySimulatedDecision(approval: ApprovalRecord, decision: SimulatedDecision, reason: string): ApprovalRecord {
  const decidedAt = new Date().toISOString();
  const now = new Date(decidedAt).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });

  if (decision === "request-clarification") {
    return {
      ...approval,
      reviewProgress: "Awaiting information",
      activity: [...approval.activity, { at: now, actor: "Prototype reviewer", detail: `Simulated a clarification request on this local fixture${reason.trim() ? `. Question: ${reason.trim()}` : "."}`, simulated: true }],
    };
  }

  const state = decision === "approve" ? "Approved" as const : "Rejected" as const;
  return {
    ...approval,
    state,
    reviewProgress: "In review",
    decisionReason: reason.trim() || undefined,
    decidedAt,
    reviewer: "Prototype reviewer",
    correlationId: `corr-sim-${approval.id}`,
    executionOutcome: decision === "approve" ? "Pending" : "Not available",
    activity: [...approval.activity, { at: now, actor: "Prototype reviewer", detail: `Simulated ${state.toLowerCase()} this local fixture${reason.trim() ? `. Reason: ${reason.trim()}` : "."}`, simulated: true }],
  };
}
