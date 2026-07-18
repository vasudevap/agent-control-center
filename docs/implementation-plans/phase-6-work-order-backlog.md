# Phase 6 Work Order Backlog

**Status:** Accepted - Phase 6 Execution Authorized
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Engineering Specification:** `docs/engineering-specifications/ES-006-gmail-agent-mvp-candidate.md`
**ADR Assessment:** `docs/implementation-plans/phase-6-adr-assessment.md`
**Implementation Authorization:** Granted for WO-036 through WO-044 under ADP-003

---

## 1. Purpose

Define the accepted Work Order sequence for Phase 6 Gmail Agent MVP Candidate.

This backlog records the accepted Phase 6 execution sequence. Each Work Order remains the bounded implementation authority for its
own scope, exclusions, validation, rollback expectations, and stop-and-ask
triggers.

## 2. Work Order Map

| Work Order | Name | Depends On | Parallelizable | Status |
| --- | --- | --- | --- | --- |
| WO-036 | Gmail OAuth, Scopes, and Connector Boundary | ES-006 accepted, Phase 5 closeout | Limited | Implemented - Pending PR Review |
| WO-037 | Gmail Message Eligibility, Retrieval, and Classification | WO-036 | Limited | Accepted |
| WO-038 | Clinical and PHI Suppression Guardrail | WO-037 contract shape | No | Accepted |
| WO-039 | Low-Risk Mailbox Actions and Attachment Saving | WO-036, WO-037, WO-038 | Yes, after suppression gate | Accepted |
| WO-040 | Ask-Instead-of-Guess and Governed Fact Use | WO-037, WO-038, Phase 5 knowledge contracts | Yes, after suppression gate | Accepted |
| WO-041 | Draft Generation and Facts-Used Evidence | WO-038, WO-040 | No | Accepted |
| WO-042 | Approval Gates, Edit-Then-Approve, and Send Continuation | WO-041, Phase 5 approval contracts | No | Accepted |
| WO-043 | Gmail Agent Operational Reconciliation | WO-039, WO-040, WO-042 | Limited | Accepted |
| WO-044 | Controlled-Account Verification and MVP Candidate Closeout | WO-036 through WO-043 | No | Accepted |

## 3. Dependency Waves

| Wave | Work Orders | Purpose | Parallel posture |
| --- | --- | --- | --- |
| Wave 0 | ES-006, ADR assessment, WO acceptance | Governance readiness | Documentation review can happen in parallel; implementation waits |
| Wave 1 | WO-036 | Establish Gmail/Drive OAuth and connector boundary | Serial because all provider behavior depends on exact scopes |
| Wave 2 | WO-037, WO-038 | Retrieve, classify, and suppress before downstream use | WO-038 can design against WO-037 contracts, but implementation must block downstream drafting until suppression is enforced |
| Wave 3 | WO-039, WO-040 | Safe low-risk actions and governed knowledge use | Parallel after suppression gate is implemented |
| Wave 4 | WO-041, WO-042 | Draft, approval, and approved send continuation | Serial because approval evidence depends on exact draft and facts-used binding |
| Wave 5 | WO-043 | Reconciliation, webhook, audit, run, and dashboard contract alignment | Limited after action and continuation flows exist |
| Wave 6 | WO-044 | Controlled-account evidence and MVP candidate closeout | Serial closeout |

## 4. Accepted Work Orders

### WO-036 - Gmail OAuth, Scopes, and Connector Boundary

Work Order:

- `docs/work-orders/036-gmail-oauth-scopes-and-connector-boundary.md`

Objective:

- Implement Gmail and Drive connector registration, OAuth connection lifecycle,
  exact scope enforcement, fake-provider contract, credential reference
  handling, health, revocation, and audit foundations.

Likely scope:

- accepted Google OAuth scope set;
- credential reference persistence through the connector boundary;
- no token logging or token API exposure;
- fake Gmail and Drive clients for all automated tests;
- connector health, reconnect, revoke, and denied-access behavior.

### WO-037 - Gmail Message Eligibility, Retrieval, and Classification

Work Order:

- `docs/work-orders/037-gmail-message-eligibility-retrieval-and-classification.md`

Objective:

- Retrieve only eligible Gmail messages through the connector, normalize minimum
  message data, classify messages with schema-validated output, and fail closed
  to review/manual handling.

Likely scope:

- eligibility query/config contract;
- selected metadata/content retrieval;
- provider references and integrity identities;
- classification categories and confidence rules;
- no drafting, question creation, send, or learning.

### WO-038 - Clinical and PHI Suppression Guardrail

Work Order:

- `docs/work-orders/038-clinical-and-phi-suppression-guardrail.md`

Objective:

- Enforce clinical and protected-health-information suppression before
  knowledge retrieval, questions, draft generation, approvals, low-risk actions,
  or learning.

Likely scope:

- suppression detector contract;
- minimized manual-handling records;
- webhook/audit events with reason codes only;
- negative tests proving no draft, approval, question, action, or learned fact
  can be produced from suppressed sources.

### WO-039 - Low-Risk Mailbox Actions and Attachment Saving

Work Order:

- `docs/work-orders/039-low-risk-mailbox-actions-and-attachment-saving.md`

Objective:

- Implement approved low-risk Gmail and Drive side effects through idempotent
  connector operations after eligibility and suppression checks pass.

Likely scope:

- labels;
- approved archive behavior;
- approved attachment save to Drive using `drive.file`;
- operation idempotency, retries, normalized outcomes, and audit;
- no send, delete, forward, unsubscribe, or external sharing.

### WO-040 - Ask-Instead-of-Guess and Governed Fact Use

Work Order:

- `docs/work-orders/040-ask-instead-of-guess-and-governed-fact-use.md`

Objective:

- Connect Gmail drafting prerequisites to Phase 5 governed knowledge so missing
  or stale required facts create questions instead of generic drafts.

Likely scope:

- required-fact mapping for Gmail draft scenarios;
- fresh governed fact retrieval;
- question creation for missing/stale facts;
- answer validation and fact revision creation;
- exclusion of suppressed and prohibited sources from knowledge.

### WO-041 - Draft Generation and Facts-Used Evidence

Work Order:

- `docs/work-orders/041-draft-generation-and-facts-used-evidence.md`

Objective:

- Generate and create Gmail drafts only when policy, suppression, knowledge,
  and validation gates pass, with exact `facts_used` evidence bound to the
  decision-context manifest.

Likely scope:

- draft input assembly with minimum necessary message context;
- LLM output schema validation and prohibited-content checks;
- Gmail draft creation through connector;
- draft provider references and hashes;
- approval evidence preparation without sending.

### WO-042 - Approval Gates, Edit-Then-Approve, and Send Continuation

Work Order:

- `docs/work-orders/042-approval-gates-edit-then-approve-and-send-continuation.md`

Objective:

- Require governed approval before high-risk Gmail actions and continue only
  exact, revalidated sends with explicit `Sent`, `Failed`, or `Indeterminate`
  outcomes.

Likely scope:

- approval request creation for send and other high-risk actions;
- exact action/content/source/facts binding;
- edit-then-approve supersession workflow;
- source, draft, connector, and facts-used revalidation;
- send outcome classification and audit.

### WO-043 - Gmail Agent Operational Reconciliation

Work Order:

- `docs/work-orders/043-gmail-agent-operational-reconciliation.md`

Objective:

- Wire Gmail agent registration, manual and scheduled runs, webhook events,
  audit events, status summaries, and dashboard/external-client reconciliation
  around the implemented Gmail behavior.

Likely scope:

- Gmail agent descriptor and runtime execution packet;
- run-step summaries and state transitions;
- webhook event producers for pending approvals, held messages, send outcomes,
  questions, and run state;
- API/dashboard compatibility documentation;
- no broad dashboard productization beyond contract compatibility.

### WO-044 - Controlled-Account Verification and MVP Candidate Closeout

Work Order:

- `docs/work-orders/044-controlled-account-verification-and-mvp-candidate-closeout.md`

Objective:

- Verify the Phase 6 Gmail Agent MVP Candidate with fake-provider automation and
  explicitly authorized controlled-account evidence, then produce closeout,
  residual-risk, and release-readiness records.

Likely scope:

- deterministic fake-provider end-to-end tests;
- controlled Gmail account test plan and evidence if separately authorized;
- no personal mailbox, production mailbox, or unbounded live data;
- privacy/security negative tests;
- closeout report and MVP candidate acceptance checklist.

## 5. Stop-and-Ask Triggers

Stop before implementation if:

- ES-006 is not accepted;
- a Work Order is not accepted;
- exact Gmail and Drive OAuth scopes are not accepted;
- live credentials, a real mailbox, or a controlled test account are required
  beyond an accepted Work Order boundary;
- provider limitations require broader scopes or changed behavior;
- implementation would store full email bodies, OAuth tokens, secrets,
  clinical content, PHI, or unrestricted attachment copies;
- implementation would create a draft, approval, question, action, send, or
  learned fact from a suppressed clinical or PHI message;
- implementation would weaken approval, audit, authorization, webhook
  minimization, or fail-closed behavior;
- implementation requires multi-user, RBAC, tenancy, delegation, quorum,
  multiple reviewers, or multiple external clients;
- implementation requires a new architecture, security, data, deployment,
  framework, or release decision.
