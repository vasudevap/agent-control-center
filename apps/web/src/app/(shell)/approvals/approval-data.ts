export type ApprovalRisk = "Low" | "Medium" | "High" | "Critical";
export type ApprovalState = "Pending" | "Clarification requested" | "Blocked" | "Approved" | "Rejected" | "Expired";
export type ExecutionOutcome = "Not started" | "Completed" | "Indeterminate" | "Not applicable";

export interface ApprovalRecord {
  id: string;
  state: ApprovalState;
  risk: ApprovalRisk;
  action: string;
  target: string;
  consequence: string;
  scope: string;
  agent: { id: string; name: string };
  runId: string;
  requestedAt: string;
  expiresAt?: string;
  policy: string;
  policyReason: string;
  evidence: { source: string; provenance: string; preview: string; complete: boolean; missing?: string[] };
  activity: Array<{ at: string; actor: string; detail: string; simulated?: boolean }>;
  executionOutcome: ExecutionOutcome;
  decisionReason?: string;
}

const evidence = (source: string, complete = true, missing?: string[]) => ({
  source,
  provenance: "Fictional local fixture. It is not an authoritative service record.",
  preview: "A fictional evidence summary describing the exact proposed action and its declared operational context.",
  complete,
  missing,
});

export const APPROVAL_FIXTURES: ApprovalRecord[] = [
  { id: "apr-2026-001", state: "Pending", risk: "Critical", action: "Send a remediation notice to the enterprise billing contact.", target: "billing-operations@northstar.example", consequence: "One external contact would receive the controlled notice.", scope: "One enterprise account; no financial transaction.", agent: { id: "agent-beta", name: "Beta Policy Agent" }, runId: "run-2026-07-12-001", requestedAt: "2026-07-12T14:06:00Z", expiresAt: "2026-07-13T16:00:00Z", policy: "External Communications P-214", policyReason: "Critical-risk external messaging requires human review.", evidence: evidence("Billing remediation evidence packet"), activity: [{ at: "Jul 12, 2026, 10:06 AM", actor: "Beta Policy Agent", detail: "Requested human authorization for the exact external message." }], executionOutcome: "Not started" },
  { id: "apr-2026-002", state: "Clarification requested", risk: "High", action: "Approve an evidence-retention exception for a reviewed policy packet.", target: "Policy packet PP-8842", consequence: "One packet remains outside the standard retention class.", scope: "One evidence packet.", agent: { id: "agent-beta", name: "Beta Policy Agent" }, runId: "run-2026-07-10-019", requestedAt: "2026-07-10T15:24:00Z", expiresAt: "2026-07-15T15:24:00Z", policy: "Evidence Retention P-118", policyReason: "The category is ambiguous and needs an operator decision.", evidence: evidence("Policy classification assessment"), activity: [{ at: "Jul 10, 2026, 11:30 AM", actor: "Prototype reviewer", detail: "Clarification requested from the policy owner.", simulated: true }], executionOutcome: "Not started" },
  { id: "apr-2026-003", state: "Blocked", risk: "High", action: "Re-run the failed connector evidence export for a governed health check.", target: "Connector registry export CR-77", consequence: "A replacement evidence export would be generated.", scope: "One connector health-check artifact.", agent: { id: "agent-gamma", name: "Gamma Connector Agent" }, runId: "run-2026-07-05-011", requestedAt: "2026-07-05T13:00:00Z", expiresAt: "2026-07-13T18:00:00Z", policy: "Connector Evidence P-071", policyReason: "Source provenance must be complete before approval.", evidence: evidence("Connector health report", false, ["Source checksum", "Original connector export"]), activity: [{ at: "Jul 5, 2026, 9:01 AM", actor: "Policy evaluation", detail: "Blocked approval until source provenance is complete." }], executionOutcome: "Not started" },
  { id: "apr-2026-004", state: "Pending", risk: "Medium", action: "Publish a reviewed operations summary to the internal artifact catalog.", target: "Artifact OPS-2026-0712", consequence: "One internal catalog entry would be published.", scope: "One internal artifact.", agent: { id: "agent-alpha", name: "Alpha Support Agent" }, runId: "run-2026-07-12-042", requestedAt: "2026-07-12T16:45:00Z", expiresAt: "2026-07-14T16:45:00Z", policy: "Internal Artifact Publication P-042", policyReason: "The artifact includes an operational recommendation.", evidence: evidence("Reviewed support-operation summary"), activity: [{ at: "Jul 12, 2026, 12:45 PM", actor: "Alpha Support Agent", detail: "Requested publication review." }], executionOutcome: "Not started" },
  { id: "apr-2026-005", state: "Approved", risk: "Low", action: "Add a reviewed categorization note to an internal support record.", target: "Support record SR-2194", consequence: "One internal record would show the note.", scope: "One internal support record.", agent: { id: "agent-alpha", name: "Alpha Support Agent" }, runId: "run-2026-07-09-013", requestedAt: "2026-07-09T13:00:00Z", policy: "Internal Record Updates P-011", policyReason: "The record update was sampled for review.", evidence: evidence("Support categorization evidence"), activity: [{ at: "Jul 9, 2026, 9:04 AM", actor: "Prototype reviewer", detail: "Approved the local fixture action.", simulated: true }], executionOutcome: "Completed", decisionReason: "The note is consistent with the supplied evidence." },
  { id: "apr-2026-006", state: "Rejected", risk: "High", action: "Send a vendor follow-up requesting revised evidence.", target: "vendor-assurance@northstar.example", consequence: "One vendor would receive a request for evidence.", scope: "One external vendor contact.", agent: { id: "agent-beta", name: "Beta Policy Agent" }, runId: "run-2026-07-08-008", requestedAt: "2026-07-08T11:10:00Z", policy: "External Communications P-214", policyReason: "External requests require reviewable evidence.", evidence: evidence("Vendor assurance packet"), activity: [{ at: "Jul 8, 2026, 7:16 AM", actor: "Prototype reviewer", detail: "Rejected because the required contact is missing.", simulated: true }], executionOutcome: "Not applicable", decisionReason: "The required evidence is incomplete." },
  { id: "apr-2026-007", state: "Expired", risk: "Medium", action: "Export a reviewed evidence bundle for a completed connector investigation.", target: "Evidence bundle EB-443", consequence: "A historical evidence bundle would be available internally.", scope: "One completed investigation.", agent: { id: "agent-gamma", name: "Gamma Connector Agent" }, runId: "run-2026-07-01-002", requestedAt: "2026-07-01T08:00:00Z", expiresAt: "2026-07-02T08:00:00Z", policy: "Connector Evidence P-071", policyReason: "Evidence exports expire when source data may have changed.", evidence: evidence("Connector investigation record"), activity: [{ at: "Jul 2, 2026, 4:00 AM", actor: "System", detail: "Approval window expired." }], executionOutcome: "Indeterminate" },
];

export const getApprovalById = (id: string) => APPROVAL_FIXTURES.find((approval) => approval.id === id);
export const isQueueApproval = (approval: ApprovalRecord) => ["Pending", "Clarification requested", "Blocked"].includes(approval.state);
