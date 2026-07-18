# ES-006 - Gmail Agent MVP Candidate

**Status:** Proposed - Blocked Pending Phase 5 Completion
**Owner:** Repository Maintainer
**Review Owner:** Repository Maintainer
**Date:** 2026-07-18
**Version:** 0.1
**Accepted:** Not Accepted
**Implementation Authorization:** Not Granted
**Target Release:** MVP candidate
**Related Phase:** Phase 6 - Gmail Agent
**Prerequisite Engineering Specification:** `docs/engineering-specifications/ES-005-agent-framework-and-governance-contracts.md`
**Related Work Orders:** TBD after ES-006 acceptance
**Related ADRs:** `docs/decisions/ADR-002-human-approvals-decision-integrity.md`, `docs/decisions/ADR-003-governed-external-approval-decision-channel.md`, `docs/decisions/ADR-004-governed-external-product-client-contract.md`, `docs/decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md`

---

## 1. Purpose

Define the first production agent for the Atlas MVP: a Gmail Agent that can
triage eligible messages, classify them, perform approved low-risk mailbox
actions, create governed draft replies, route high-risk sends through approval,
ask instead of guessing when required business facts are missing, and suppress
clinical or protected-health-information messages before drafting or learning.

ES-006 is the Gmail-specific consumer of the generic Phase 5 contracts. It does
not authorize implementation until Phase 5 agent, run, approval, knowledge,
webhook, audit, and `facts_used` contracts are complete and accepted.

## 2. Agent Definition

| Field | MVP value |
| --- | --- |
| Agent name | Gmail Agent |
| Initial product role | First MVP agent |
| Primary job | Triage eligible Gmail messages and prepare safe, governed responses |
| Runtime type | Python agent running through the Atlas Agent Runtime |
| Owner model | Single configured owner |
| Reviewer model | Single configured human reviewer |
| External client model | One governed external product client acting for the owner |
| Provider | Gmail through the Connector Runtime |
| Supporting provider | Google Drive for approved attachment saving |
| Operating mode | Manual run and scheduled run |
| Data posture | Minimum necessary message data; no unrestricted mailbox copy |

## 3. Intended Outcome

After ES-006 is implemented and accepted as an MVP candidate:

- the owner can connect Gmail with approved OAuth scopes;
- the agent can run manually or on schedule through the generic runtime;
- eligible messages are retrieved through the Gmail connector, normalized, and
  classified;
- low-risk configured actions such as labels, approved newsletter archiving, and
  approved attachment saving can execute idempotently;
- draft replies can be created only after policy, knowledge, and sensitivity
  checks pass;
- high-risk sends require approval before dispatch;
- approved sends record explicit `Sent`, `Failed`, or `Indeterminate` outcomes;
- ask-instead-of-guess questions are created when required facts are missing or
  stale;
- validated answers and eligible approved sends can produce governed knowledge
  candidates with provenance;
- clinical and protected-health-information messages are held for manual
  handling with no draft, approval, question, or learned fact;
- the dashboard and external product client can reconcile status, approvals,
  held messages, and outcomes through the governed API and webhooks.

## 4. Governing References

ES-006 is governed by:

- `AGENTS.md`
- `PROJECT.md`
- `ROADMAP.md`
- `docs/specifications/product-requirements.md`
- `docs/architecture/05-component-architecture.md`
- `docs/architecture/07-security-architecture.md`
- `docs/architecture/08-data-architecture.md`
- `docs/architecture/09-agent-runtime.md`
- `docs/architecture/10-connector-framework.md`
- `docs/architecture/11-observability.md`
- `docs/architecture/13-human-approvals.md`
- `docs/decisions/ADR-002-human-approvals-decision-integrity.md`
- `docs/decisions/ADR-003-governed-external-approval-decision-channel.md`
- `docs/decisions/ADR-004-governed-external-product-client-contract.md`
- `docs/decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md`
- `docs/implementation-plans/mvp-release-boundary-and-phase-gates.md`
- canonical engineering governance under `docs/governance/`

If implementation pressure conflicts with these references, the Work Order must
be corrected or a new ADR must be accepted before code proceeds.

## 5. Approved Scope if Accepted

### 5.1 Gmail OAuth and connector setup

- Implement Gmail OAuth using approved, least-privilege scopes.
- Store OAuth credentials through the approved connector credential boundary.
- Support connection status, health, reconnection, and revocation behavior.
- Prevent the agent from using Gmail unless the connector is approved and
  healthy.
- Record connector lifecycle and credential access audit events without logging
  token values.

### 5.2 Message eligibility and retrieval

- Retrieve only eligible messages according to configured criteria.
- Read sender, subject, selected content, thread metadata, attachment metadata,
  and provider references required for classification and approved actions.
- Avoid unrestricted mailbox scans and full mailbox persistence.
- Normalize provider errors and rate limits through the Connector Runtime.
- Preserve source references and integrity identities needed for audit and
  approval evidence.

### 5.3 Classification

- Classify messages into the initial MVP categories:
  `Family`, `Friends`, `Work`, `Recruiters`, `Shopping`, `Subscriptions`,
  `Receipts`, `Travel`, `Personal Administration`, `Needs Reply`,
  `Review Required`, `Unknown`, `Clinical`, and
  `Protected Health Information`.
- Treat `Clinical` and `Protected Health Information` as safety
  classifications, not ordinary routing labels.
- Validate LLM or model output against a strict schema before use.
- Fail closed to `Review Required` or manual handling when classification is
  uncertain beyond accepted thresholds.

### 5.4 Clinical and protected-health-information suppression

- Apply the clinical and protected-health-information filter before knowledge
  retrieval, question creation, draft generation, approval creation,
  history-learning input assembly, or fact persistence.
- Hold suppressed messages for manual handling.
- Emit only minimized manual-handling metadata through API, audit, and webhook
  contracts.
- Do not create a draft, proposed send, approval request, knowledge question,
  or learned fact for suppressed messages.
- Do not permit human approval to override suppression.

### 5.5 Low-risk mailbox actions

- Apply approved Gmail labels.
- Archive only approved low-risk categories, such as configured newsletters or
  subscriptions.
- Save approved attachments to the approved Google Drive folder hierarchy.
- Require idempotency records for side-effecting operations.
- Record all actions, denied actions, provider outcomes, and retries.

### 5.6 Draft reply generation

- Create draft replies only for eligible messages that pass sensitivity,
  policy, connector, and governed-knowledge checks.
- Use only governed facts that pass freshness and policy checks.
- Include exact fact revisions used in approval evidence through `facts_used`.
- Store minimum necessary draft metadata and provider references.
- Validate generated draft content before creating a Gmail draft.
- Never send automatically as part of draft creation.

### 5.7 Ask-instead-of-guess behavior

- Create a governed knowledge question when a required fact is missing or a
  volatile fact requires re-confirmation.
- Do not create a generic draft as a substitute for a missing required fact.
- Treat answers as untrusted input.
- Persist a fact or fact revision only after validation and policy checks pass.
- Keep questions and answers separate from approvals and approval
  clarification.

### 5.8 Approval and send continuation

- Require approval before sending an email, deleting an email, forwarding an
  email, unsubscribing, sharing externally, or performing an unfamiliar action.
- Bind send approval to exact action, recipient, content, source message,
  draft, evidence, fact revisions, and decision-context manifest.
- Support internal and external approval channels through the Phase 5 Approval
  Service contracts.
- Revalidate source message, draft content, and `facts_used` before send
  continuation.
- Record send outcome as `Sent`, `Failed`, or `Indeterminate`.
- Use the edit-then-approve workflow when the human edits draft content before
  approving send.

### 5.9 Learning from approved sources

- Learn candidate facts from validated human answers when policy permits.
- Learn candidate facts from historical Gmail sends only when the source send
  was approved and has a confirmed `Sent` outcome.
- Preserve source provenance for all learned candidates.
- Do not learn from failed, indeterminate, rejected, unapproved, draft-only, or
  suppressed clinical/protected-health-information sources.
- Treat learned candidates as untrusted until validated and accepted into the
  governed knowledge store.

### 5.10 Dashboard, external API, webhooks, and audit

- Surface Gmail agent status, run status, connector health, classification
  outputs, pending approvals, held messages, and execution outcomes through the
  governed API contracts.
- Emit authenticated webhook notifications for pending approvals, send
  outcomes, held manual-handling items, relevant question/answer lifecycle
  events, and run state changes.
- Treat webhooks as notifications only.
- Record durable audit events for connector access, classification, policy
  decisions, mailbox actions, draft creation, approval creation, send
  continuation, send outcomes, holds, knowledge questions, answer validation,
  and learned facts.

## 6. Explicitly Out of Scope

ES-006 does not authorize:

- multi-user, RBAC, multi-tenant, delegation, quorum, multiple reviewers, or
  multiple external product clients;
- unrestricted mailbox scanning or full mailbox replication;
- automatic send, delete, forward, unsubscribe, or external sharing without
  approval;
- bypassing the Connector Runtime, Policy Engine, Approval Service, governed
  knowledge contracts, Audit Writer, or Tool Registry;
- storing OAuth tokens, secrets, full email bodies, clinical content, or
  protected health information in logs, webhooks, approval payloads, or the
  knowledge store;
- broad Google Drive behavior outside approved attachment saving;
- production release authority;
- Temporal, LangGraph, or a new orchestration framework;
- Gmail-specific changes to the generic Phase 5 contracts.

## 7. OAuth and Connector Requirements

Implementation Work Orders must define the exact OAuth scopes before code
begins. The scope set must be least-privilege and must map to the accepted MVP
operations:

- read eligible message metadata and selected content;
- apply labels and archive messages where policy permits;
- create drafts;
- send only after approval continuation;
- retrieve approved attachment content for approved saving;
- avoid scopes that grant broader access than the MVP needs unless a security
  review accepts the residual risk.

OAuth tokens must be encrypted or stored through the approved credential
boundary. Token values must never be returned through API responses, logged,
included in webhooks, persisted in audit metadata, or committed in tests.

## 8. Data Requirements

Implementation must satisfy these data constraints:

- PostgreSQL remains the Atlas runtime system of record.
- Gmail remains the provider system of record for mailbox messages and drafts.
- Store provider references, normalized metadata, classification outputs,
  action outcomes, and audit records.
- Avoid storing full message bodies unless a later accepted security and
  retention decision explicitly permits a minimized snapshot.
- Store attachment references and Drive output references, not unrestricted
  attachment copies inside Atlas.
- Persist idempotency keys for side-effecting Gmail and Drive operations.
- Preserve enough source version or integrity metadata to support approval
  evidence and send revalidation.

## 9. Security and Privacy Requirements

Implementation must satisfy these controls:

- Authentication required by default.
- Authorization denied by default.
- Connector access is limited to the approved owner and approved agent
  capability set.
- LLM/model outputs are untrusted and schema-validated.
- Prohibited content is rejected or held before downstream use.
- Clinical and protected-health-information suppression happens before
  knowledge, question, draft, approval, or learning flows.
- Approval decisions fail closed when source, draft, evidence, fact, actor,
  channel, expiry, audit, or connector state is invalid.
- Logs, webhooks, audit metadata, API responses, and test fixtures must not
  expose secrets, credentials, OAuth tokens, full email bodies, or prohibited
  content.

## 10. Validation Requirements

Each implementing Work Order must define focused validation. The Gmail MVP
candidate as a whole must pass:

- Gmail connector unit and fake-provider integration tests;
- OAuth callback, token storage, revocation, and health tests using fake tokens;
- classification schema and uncertainty tests;
- clinical/protected-health-information suppression tests;
- idempotency tests for labels, archive, draft creation, send continuation, and
  attachment saving;
- ask-instead-of-guess tests for missing and stale facts;
- facts-used evidence and revalidation tests;
- approval and edit-then-approve tests;
- send outcome tests for `Sent`, `Failed`, and `Indeterminate`;
- webhook minimized-payload and fake-delivery tests;
- audit and redaction tests;
- end-to-end controlled-data workflow verification;
- `ruff`, `mypy`, frontend checks if dashboard files are touched, repository
  formatting checks, and GitHub CI.

## 11. MVP Candidate Acceptance Criteria

The Gmail Agent reaches MVP candidate status when:

- Phase 5 generic contracts are implemented and merged;
- Gmail OAuth and connector behavior works against fake or controlled provider
  evidence;
- manual and scheduled runs process controlled eligible messages end to end;
- labels, approved archives, approved attachment saves, and draft creation are
  idempotent and auditable;
- high-risk sends require approval and record explicit send outcomes;
- ask-instead-of-guess prevents generic drafts when required facts are missing;
- clinical/protected-health-information messages are held with no draft,
  approval, question, or learned fact;
- dashboard and external client contracts can reconcile status, pending
  approvals, held items, and outcomes;
- no unresolved safety, credential, audit, or authorization blocker remains.

## 12. Stop-and-Ask Triggers

Stop and request Repository Maintainer direction before proceeding if:

- Phase 5 contracts are incomplete or unaccepted;
- exact Gmail OAuth scopes are not accepted;
- live Gmail credentials or a real account are needed beyond the accepted test
  boundary;
- implementation would store full email bodies, OAuth tokens, secrets,
  clinical content, or protected health information;
- the agent would draft, ask, approve, learn from, or send based on a suppressed
  clinical/protected-health-information message;
- a provider API limitation requires broader scopes or a behavior change;
- send continuation cannot distinguish `Sent`, `Failed`, and `Indeterminate`;
- implementation needs multi-user, RBAC, tenancy, multiple reviewers, or
  multiple external clients;
- a new architecture, security, data, deployment, framework, or release
  decision is required.

## 13. Review Notes

This specification is proposed planning authority only. It captures the Gmail
Agent MVP candidate scope and should be reviewed before any Phase 6 Work Orders
are drafted or accepted.
