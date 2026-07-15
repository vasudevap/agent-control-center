/**
 * Alternate-exploration approval fixtures.
 *
 * Adapted from the baseline's approval-data.ts shape. Two structural
 * corrections were made while adapting, both required by the approved
 * Human Approvals Functional Specification and Architecture (not
 * cosmetic choices):
 *
 * 1. Canonical approval state is one of exactly five values (Pending,
 *    Approved, Rejected, Expired, Cancelled). "Blocked" and
 *    "Clarification requested" are review-progress facets, not
 *    states, per architecture/13-human-approvals.md section 9.2 and
 *    ES-003 section 8.3. They are represented here as `reviewProgress`.
 * 2. Timestamps are generated relative to load time (hoursFromNow /
 *    hoursAgo) rather than fixed calendar dates, so queue urgency
 *    never silently drifts into a contradictory "Expired but Pending"
 *    state as real time passes.
 *
 * Agent references use the same six canonical agents defined in
 * agents/agent-data.ts so the Approvals experience, Agent Detail, and
 * Overview always describe one consistent fictional fleet.
 */

export type ApprovalRisk = "Low" | "Medium" | "High" | "Critical";
export type ApprovalState = "Pending" | "Approved" | "Rejected" | "Expired" | "Cancelled";
export type ReviewProgress = "Unopened" | "In review" | "Awaiting information" | "Blocked";
export type ExecutionOutcome = "Not available" | "Pending" | "Succeeded" | "Partially succeeded" | "Failed" | "Indeterminate";

export interface ApprovalRecord {
  id: string;
  state: ApprovalState;
  reviewProgress: ReviewProgress;
  risk: ApprovalRisk;
  action: string;
  target: string;
  consequence: string;
  scope: string;
  agent: { id: string; name: string };
  runId: string;
  artifact?: { id: string; name: string };
  requestedAt: string;
  expiresAt?: string;
  policy: string;
  policyReason: string;
  environment: string;
  evidence: { source: string; provenance: string; preview: string; complete: boolean; missing?: string[] };
  activity: Array<{ at: string; actor: string; detail: string; simulated?: boolean }>;
  executionOutcome: ExecutionOutcome;
  decisionReason?: string;
  decidedAt?: string;
  reviewer?: string;
  correlationId?: string;
}

const HOUR = 60 * 60 * 1000;
const now = () => Date.now();
const hoursFromNow = (h: number) => new Date(now() + h * HOUR).toISOString();
const hoursAgo = (h: number) => new Date(now() - h * HOUR).toISOString();

const evidence = (source: string, complete = true, missing?: string[]) => ({
  source,
  provenance: "Fictional local fixture. It is not an authoritative service record.",
  preview: "A fictional evidence summary describing the exact proposed action and its declared operational context.",
  complete,
  missing,
});

export const APPROVAL_FIXTURES: ApprovalRecord[] = [
  {
    id: "apr-2026-001",
    state: "Pending",
    reviewProgress: "Unopened",
    risk: "Critical",
    action: "Send a remediation notice to the enterprise billing contact.",
    target: "billing-operations@northstar.example",
    consequence: "One external contact would receive the controlled notice.",
    scope: "One enterprise account; no financial transaction.",
    agent: { id: "agent-policy-digest", name: "Policy Digest Agent" },
    runId: "run-2026-07-12-001",
    artifact: { id: "art-2026-0712-001", name: "Billing remediation evidence packet" },
    requestedAt: hoursAgo(3),
    expiresAt: hoursFromNow(1.5),
    policy: "External Communications P-214",
    policyReason: "Critical-risk external messaging requires human review.",
    environment: "Production",
    evidence: evidence("Billing remediation evidence packet"),
    activity: [{ at: hoursAgo(3), actor: "Policy Digest Agent", detail: "Requested human authorization for the exact external message." }],
    executionOutcome: "Not available",
  },
  {
    id: "apr-2026-002",
    state: "Pending",
    reviewProgress: "Awaiting information",
    risk: "High",
    action: "Approve an evidence-retention exception for a reviewed policy packet.",
    target: "Policy packet PP-8842",
    consequence: "One packet remains outside the standard retention class.",
    scope: "One evidence packet.",
    agent: { id: "agent-policy-digest", name: "Policy Digest Agent" },
    runId: "run-2026-07-10-019",
    requestedAt: hoursAgo(30),
    expiresAt: hoursFromNow(28),
    policy: "Evidence Retention P-118",
    policyReason: "The category is ambiguous and needs an operator decision.",
    environment: "Production",
    evidence: evidence("Policy classification assessment"),
    activity: [
      { at: hoursAgo(30), actor: "Policy Digest Agent", detail: "Requested human authorization." },
      { at: hoursAgo(26), actor: "Prototype reviewer", detail: "Requested clarification from the policy owner.", simulated: true },
    ],
    executionOutcome: "Not available",
  },
  {
    id: "apr-2026-003",
    state: "Pending",
    reviewProgress: "Blocked",
    risk: "High",
    action: "Re-run the failed connector evidence export for a governed health check.",
    target: "Connector registry export CR-77",
    consequence: "A replacement evidence export would be generated.",
    scope: "One connector health-check artifact.",
    agent: { id: "agent-connectors-health", name: "Connector Health Sentinel" },
    runId: "run-2026-07-05-011",
    requestedAt: hoursAgo(200),
    expiresAt: hoursFromNow(190),
    policy: "Connector Evidence P-071",
    policyReason: "Source provenance must be complete before approval.",
    environment: "Production",
    evidence: evidence("Connector health report", false, ["Source checksum", "Original connector export"]),
    activity: [{ at: hoursAgo(200), actor: "Policy evaluation", detail: "Blocked approval until source provenance is complete." }],
    executionOutcome: "Not available",
  },
  {
    id: "apr-2026-004",
    state: "Pending",
    reviewProgress: "In review",
    risk: "Medium",
    action: "Publish a reviewed operations summary to the internal artifact catalog.",
    target: "Artifact OPS-2026-0712",
    consequence: "One internal catalog entry would be published.",
    scope: "One internal artifact.",
    agent: { id: "agent-support-drafts", name: "Support Draft Agent" },
    runId: "run-2026-07-12-042",
    requestedAt: hoursAgo(5),
    expiresAt: hoursFromNow(43),
    policy: "Internal Artifact Publication P-042",
    policyReason: "The artifact includes an operational recommendation.",
    environment: "Staging",
    evidence: evidence("Reviewed support-operation summary"),
    activity: [{ at: hoursAgo(5), actor: "Support Draft Agent", detail: "Requested publication review." }],
    executionOutcome: "Not available",
  },
  {
    id: "apr-2026-008",
    state: "Pending",
    reviewProgress: "Unopened",
    risk: "Low",
    action: "Tag a completed intake batch as reviewed in the recruiter queue.",
    target: "Intake batch RB-2026-0713",
    consequence: "One internal batch record changes status.",
    scope: "One recruiting intake batch.",
    agent: { id: "agent-recruiting-triage", name: "Recruiting Triage Agent" },
    runId: "run-2026-07-13-006",
    requestedAt: hoursAgo(1),
    expiresAt: hoursFromNow(71),
    policy: "Recruiting Intake Handling P-030",
    policyReason: "Low-risk status changes are sampled for review.",
    environment: "Production",
    evidence: evidence("Recruiting batch summary"),
    activity: [{ at: hoursAgo(1), actor: "Recruiting Triage Agent", detail: "Requested review of the batch status change." }],
    executionOutcome: "Not available",
  },
  {
    id: "apr-2026-005",
    state: "Approved",
    reviewProgress: "In review",
    risk: "Low",
    action: "Add a reviewed categorization note to an internal support record.",
    target: "Support record SR-2194",
    consequence: "One internal record would show the note.",
    scope: "One internal support record.",
    agent: { id: "agent-support-drafts", name: "Support Draft Agent" },
    runId: "run-2026-07-09-013",
    requestedAt: hoursAgo(120),
    policy: "Internal Record Updates P-011",
    policyReason: "The record update was sampled for review.",
    environment: "Production",
    evidence: evidence("Support categorization evidence"),
    activity: [
      { at: hoursAgo(120), actor: "Support Draft Agent", detail: "Requested review." },
      { at: hoursAgo(118), actor: "Prototype reviewer", detail: "Approved the local fixture action.", simulated: true },
    ],
    executionOutcome: "Succeeded",
    decisionReason: "The note is consistent with the supplied evidence.",
    decidedAt: hoursAgo(118),
    reviewer: "Prototype reviewer",
    correlationId: "corr-apr-2026-005",
  },
  {
    id: "apr-2026-006",
    state: "Rejected",
    reviewProgress: "In review",
    risk: "High",
    action: "Send a vendor follow-up requesting revised evidence.",
    target: "vendor-assurance@northstar.example",
    consequence: "One vendor would receive a request for evidence.",
    scope: "One external vendor contact.",
    agent: { id: "agent-policy-digest", name: "Policy Digest Agent" },
    runId: "run-2026-07-08-008",
    requestedAt: hoursAgo(150),
    policy: "External Communications P-214",
    policyReason: "External requests require reviewable evidence.",
    environment: "Production",
    evidence: evidence("Vendor assurance packet"),
    activity: [
      { at: hoursAgo(150), actor: "Policy Digest Agent", detail: "Requested review." },
      { at: hoursAgo(147), actor: "Prototype reviewer", detail: "Rejected because the required contact is missing.", simulated: true },
    ],
    executionOutcome: "Not available",
    decisionReason: "The required evidence is incomplete.",
    decidedAt: hoursAgo(147),
    reviewer: "Prototype reviewer",
    correlationId: "corr-apr-2026-006",
  },
  {
    id: "apr-2026-007",
    state: "Expired",
    reviewProgress: "In review",
    risk: "Medium",
    action: "Export a reviewed evidence bundle for a completed connector investigation.",
    target: "Evidence bundle EB-443",
    consequence: "A historical evidence bundle would be available internally.",
    scope: "One completed investigation.",
    agent: { id: "agent-connectors-health", name: "Connector Health Sentinel" },
    runId: "run-2026-07-01-002",
    requestedAt: hoursAgo(320),
    expiresAt: hoursAgo(296),
    policy: "Connector Evidence P-071",
    policyReason: "Evidence exports expire when source data may have changed.",
    environment: "Production",
    evidence: evidence("Connector investigation record"),
    activity: [{ at: hoursAgo(296), actor: "System", detail: "Approval window expired." }],
    executionOutcome: "Indeterminate",
    decidedAt: hoursAgo(296),
    reviewer: "System",
    correlationId: "corr-apr-2026-007",
  },
  {
    id: "apr-2026-009",
    state: "Cancelled",
    reviewProgress: "In review",
    risk: "Medium",
    action: "Archive a superseded calendar-briefing template.",
    target: "Briefing template BT-118",
    consequence: "One internal template would be archived.",
    scope: "One briefing template.",
    agent: { id: "agent-calendar-briefing", name: "Calendar Briefing Agent" },
    runId: "run-2026-07-06-004",
    requestedAt: hoursAgo(200),
    policy: "Template Lifecycle P-090",
    policyReason: "Template retirement is sampled for review.",
    environment: "Production",
    evidence: evidence("Template usage report"),
    activity: [
      { at: hoursAgo(200), actor: "Calendar Briefing Agent", detail: "Requested archival review." },
      { at: hoursAgo(180), actor: "System", detail: "Cancelled because the requesting workflow withdrew the request." },
    ],
    executionOutcome: "Not available",
    decidedAt: hoursAgo(180),
    reviewer: "System",
    correlationId: "corr-apr-2026-009",
  },
];

export const getApprovalById = (id: string) => APPROVAL_FIXTURES.find((approval) => approval.id === id);
export const isQueueApproval = (approval: ApprovalRecord) => approval.state === "Pending";
