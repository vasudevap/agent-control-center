import type { ApprovalRecord } from "./approval-data";

export type SimulatedDecision = "approve" | "reject" | "request-clarification";

export function requiresSimulatedStepUp(approval: ApprovalRecord) {
  return approval.risk === "Critical" || approval.risk === "High";
}

export function canSimulateDecision(approval: ApprovalRecord, decision: SimulatedDecision) {
  return ["Pending", "Clarification requested", "Blocked"].includes(approval.state) && (decision !== "approve" || approval.evidence.complete);
}

export function applySimulatedDecision(approval: ApprovalRecord, decision: SimulatedDecision, reason: string): ApprovalRecord {
  const state = decision === "approve" ? "Approved" : decision === "reject" ? "Rejected" : "Clarification requested";
  const verb = decision === "request-clarification" ? "requested clarification for" : `${state.toLowerCase()}`;
  return { ...approval, state, decisionReason: reason.trim() || undefined, executionOutcome: decision === "approve" ? "Not started" : "Not applicable", activity: [...approval.activity, { at: "Jul 13, 2026, 1:30 PM", actor: "Prototype reviewer", detail: `Simulated ${verb} this local fixture${reason.trim() ? `. Reason: ${reason.trim()}` : "."}`, simulated: true }] };
}
