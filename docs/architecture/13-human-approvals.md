# Atlas Human Approvals Architecture

**Status:** Approved
**Version:** 1.1
**Date:** 2026-07-17
**Capability:** Human Approvals
**Product:** Atlas
**Governing Decision:** ADR-004 is accepted; implementation still requires approved Phase 3 and Phase 5 artifacts
**Proposed Extension:** ADR-005 records R8 draft-support knowledge and ask-instead-of-guess behavior and requires acceptance before implementation planning

---

## 1. Purpose

This document defines the architecture for the Atlas Human Approvals
capability.

Human Approvals provides the control-plane boundary through which an exact
agent-proposed action is held for human authorization, reviewed with evidence,
approved or rejected, and connected to subsequent execution and audit outcomes.

This specification translates the approved Human Approvals Functional
Specification into component responsibilities, trust boundaries, lifecycle
rules, logical information requirements, security controls, observability, and
failure behavior.

This document does not authorize implementation. Detailed API contracts,
database schemas, infrastructure configuration, authentication implementation,
authorization rules, and implementation work orders require separate approval.

---

## 2. Architectural Position

Human Approvals is a first-class governance capability in the Atlas control
plane.

It is not:

- A notification inbox.
- A task-management subsystem.
- A workflow-authoring tool.
- A replacement for the Policy Engine.
- A mechanism through which an agent authorizes its own action.
- Evidence that an approved action executed successfully.

The architecture preserves the existing Atlas separation between:

- Agent proposal.
- Policy evaluation.
- Human authorization.
- Action revalidation.
- Action execution.
- Execution outcome.
- Audit evidence.

---

## 3. Authoritative Inputs

This architecture is governed by the existing Atlas architecture baseline and
the approved Human Approvals Functional Specification.

The following existing architectural decisions remain unchanged:

- Atlas separates the control plane from agent execution.
- The Policy Engine, not an LLM, determines whether approval is required.
- The Approval Service captures human authorization.
- A run may enter `WaitingForApproval` while an approval remains pending.
- Approval binds to one exact action, target, content or payload identity,
  agent, run, expiry, and reviewer.
- The action is revalidated before execution after approval.
- Atlas records one authorized action intent, suppresses duplicate dispatch,
  uses provider idempotency where available, and represents uncertain external
  outcomes explicitly.
- Material activity produces append-oriented audit events.
- Approval decision state and execution outcome remain separate.
- PostgreSQL remains the planned runtime system of record.

No new framework, deployment boundary, or infrastructure component is
introduced by this specification.

---

## 4. Architecture Goals

The Human Approvals architecture must:

1. Preserve human authority over governed agent actions.
2. Prevent an approval from authorizing a different action or target.
3. Prevent stale, expired, cancelled, or previously decided requests from being decided again.
4. Preserve the exact decision context presented to the reviewer.
5. Require sufficient evidence before approval is accepted.
6. Keep rejection and clarification available when approval evidence is incomplete.
7. Record reviewer identity, time, reason, and decision provenance.
8. Separate approval from execution and execution outcome.
9. Support safe workflow continuation after approval.
10. Fail closed when state, evidence, authorization, or action identity is uncertain.
11. Preserve complete operational and audit visibility.
12. Treat internal and governed external decision channels as first-class service
    boundaries from the initial Approval Service design.
13. Enforce a single-reviewer model with one human decision authority.

---

## 5. Architecture Scope

### 5.1 In Scope

- Approval-request creation.
- Pending-approval retrieval and investigation.
- Evidence association and completeness evaluation.
- Individual approve and reject decisions.
- Request clarification lifecycle.
- Expiry and cancellation.
- Decision reasons.
- Reviewer and decision provenance.
- Approval history.
- Runtime waiting and continuation boundary.
- Action revalidation after approval.
- Execution-outcome association.
- Audit events.
- Operational metrics and alerts.
- Failure, concurrency, and duplicate-decision behavior.

### 5.2 Deferred

- Bulk decisions.
- Bulk assignment.
- Approval revocation.
- Reopening completed approvals.

### 5.3 Out of Scope

- Exact API endpoint definitions.
- Physical database schema.
- Authentication provider selection.
- Role and permission implementation.
- Reauthentication implementation.
- Queue technology selection.
- Notification transport selection.
- User-interface implementation.
- Connector-specific execution logic.
- Deployment topology changes.

The following are prohibited by the single-reviewer constraint, not deferred:

- Multi-user approval.
- Role-based access control for approval decisions.
- Multi-tenant approval.
- Reviewer assignment, delegation, escalation, or reviewer groups.
- Multiple reviewers, sequential or parallel review, and quorum decisions.

### 5.4 Planned Later-Phase Backend Scope

The following backend capabilities are architecturally recognized but are not
authorized for implementation by this document:

- An authenticated API that exposes the pending-approval queue and governed
  evidence to a trusted external client.
- An authenticated API that accepts approve or reject decisions from a trusted
  external client.
- Webhook events for approval pending and for send outcomes of `Sent`, `Failed`,
  or `Indeterminate`.
- An authentication model for a trusted external control plane acting for one
  human.
- Decision audit provenance that identifies the channel as `Internal` or
  `External`.
- An R0 edit-then-approve interface operation that creates a superseding new
  approval for the exact edited content and continues directly to send as one
  continuous user action.
- A minimized non-approval event that surfaces a clinical or
  protected-health-information hold for manual handling without creating a
  draft, proposed action, or approval.
- A governed knowledge-fact API with create, read, update, delete, confirmation,
  volatility, and re-confirmation operations.
- First-class ask-instead-of-guess question and answer records delivered through
  the authenticated external API and webhook channel.
- A typed approval evidence `facts_used` collection that binds a draft to the
  exact fact revisions it used.

This scope follows the roadmap phase boundaries:

- Phase 3 establishes the authenticated external API, client-authentication,
  webhook-delivery, and knowledge-persistence foundations.
- Phase 5 establishes the generic external approval and non-approval
  manual-handling contracts plus the governed fact, question, answer,
  re-confirmation, and `facts_used` evidence contracts.
- Phase 6 supplies Gmail-specific evidence, classification, hold creation,
  ask-instead-of-guess, governed learning, and send execution for the first
  end-to-end workflow.

Each phase requires the applicable accepted ADRs, architecture review, approved
Engineering Specification and Work Order, and confirmation of Definition of
Ready. This document authorizes no implementation.

---

## 6. System Context

```text
Agent Runtime
    |
    | proposes action
    v
Action Validator
    |
    | validated proposal
    v
Policy Engine
    |
    | require approval
    v
Approval Service <------ Atlas Web / Operator
    ^                         |
    |                         | inspect evidence and decide
    |
    +---------------- Trusted External Control Plane / Operator
    |                         |
    |                         | inspect evidence and decide
    v                         v
Audit Writer <---------- decision channel provenance
    |
    | approved continuation
    v
Agent Runtime
    |
    | revalidate exact action
    v
Connector Runtime / Tool
    |
    | execution outcome
    v
Approval Service + Run Service + Audit Writer
```

The Atlas Web interface is an untrusted presentation client. It may present and
submit decisions, but it is not authoritative for approval state, evidence
completeness, expiry, reviewer authorization, or execution eligibility.

A trusted external control plane, initially MushingMule, may act as a separate
customer-facing presentation and decision client for the same single human
reviewer. Trust in that client is limited to its authenticated channel and
delegated ability to act for that human. The Approval Service remains
authoritative and applies the same evidence, state, expiry, action-binding,
concurrency, reauthentication, and audit controls to both channels.

---

## 7. Component Responsibilities

### 7.1 Atlas Web

Atlas Web is responsible for:

- Presenting the approval queue and history.
- Presenting exact action scope and evidence.
- Presenting approval and execution states separately.
- Collecting decision reasons.
- Presenting clarification activity.
- Preventing obviously invalid interaction in the user experience.
- Refreshing stale state before or during a decision interaction.
- Displaying structured errors without implying success.

Atlas Web must not be trusted to enforce approval validity.

### 7.2 Approval Service

The existing Approval Service owns the approval lifecycle.

It is responsible for:

- Creating approval requests from validated policy outcomes.
- Maintaining canonical approval state.
- Binding a request to the exact proposed action.
- Associating evidence and evidence requirements.
- Evaluating whether required approval evidence is complete.
- Recording approve and reject decisions.
- Recording request-clarification activity.
- Enforcing expiry and cancellation.
- Rejecting stale, duplicate, conflicting, or invalid decisions.
- Recording reviewer and decision provenance.
- Recording whether each accepted decision arrived through the internal or
  external channel.
- Emitting approval lifecycle events.
- Making approved continuation available to the runtime boundary.
- Associating execution outcomes without rewriting the approval decision.

The Approval Service must not execute connector or tool actions directly.

### 7.3 Policy Engine

The existing Policy Engine remains responsible for:

- Determining that human approval is required.
- Providing policy and risk context.
- Providing or identifying required evidence classes when policy-defined.
- Denying actions that may not proceed even with approval.
- Re-evaluating applicable policy before execution when required.

Approval must not override a policy denial.

For the Phase 6 Gmail agent, an inbound message classified as clinical or as
containing protected health information is suppressed from automatic drafting
and routed to a hold or manual-handling outcome. It must not produce a draft,
proposed send action, or approval request. This is a Policy Engine boundary,
not an approval path, and human approval cannot override it.

### 7.3.1 External Surfacing of a Suppressed Message

A clinical or protected-health-information hold must be surfaced to the
governed external product client through a non-approval event named
`message.held_for_manual_handling`.

The event exists so the single human owner can discover that a message requires
manual handling. It must not:

- Create an approval request or approval record.
- Contain a draft or proposed send action.
- Confer authorization.
- Permit automatic drafting, sending, or policy override.
- Provide a path around the clinical or protected-health-information
  suppression rule.

The event identifies the held message through a governed source reference and
includes the reason category required for routing, such as `Clinical` or
`ProtectedHealthInformation`. It may include the hold identifier, agent and run
references, sensitivity classification, correlation identity, and held
timestamp. It must not copy message content, sender details, subject text, or
other evidence unless a later approved contract establishes that the field is
necessary and permitted.

The external product client presents the item as `Needs manual handling`. It
must not present the item as pending approval or expose approve or reject
controls for it.

The hold outcome, external delivery attempt, reason category, policy and
classification provenance, authenticated external client, correlation identity,
and timestamp are auditable. Channel provenance uses the same `Internal` or
`External` vocabulary as decision-channel audit records, but no reviewer,
decision, or approval identity is recorded because no decision occurred.

The Backend API and webhook foundations belong to Phase 3. The generic
manual-handling event contract belongs to Phase 5. The Gmail-specific
classification and hold source remains a Phase 6 dependency. No implementation
is authorized by this architecture requirement.

### 7.4 Action Validator

The Action Validator remains responsible for treating agent and model output as
untrusted input.

It validates:

- Action schema.
- Target identity.
- Content or payload structure.
- Required connector and permission context.
- Data sensitivity.
- Risk inputs.
- Action identity used by the approval binding.

### 7.5 Agent Runtime

The Agent Runtime is responsible for:

- Suspending or ending active work safely when approval is required.
- Setting the related run or step to a waiting-for-approval condition.
- Preserving sufficient continuation context.
- Receiving an approved continuation signal or discovering an approved state.
- Revalidating the exact action before execution.
- Preventing duplicate local dispatch of the approved action intent.
- Applying provider idempotency where available.
- Recording an indeterminate outcome when external execution cannot be proven.
- Recording execution outcome through the appropriate services.

The runtime must not remain dependent on one continuously running worker while
waiting for human action.

### 7.6 Run Service

The Run Service is responsible for:

- Reflecting the relationship between the run and approval.
- Presenting `WaitingForApproval` independently of approval review facets.
- Recording run or step progression after the approval reaches a terminal state.
- Preserving run history when an approval expires, is rejected, or is cancelled.

### 7.7 Audit Writer

The Audit Writer records append-oriented events for all material approval
activity and for the non-approval manual-handling hold notifications defined by
this architecture.

It must preserve traceability without allowing later state changes to rewrite
earlier events.

### 7.8 Notification Capability

A future notification capability may notify an operator about pending,
near-expiry, clarification, completed approvals, or a message held for manual
handling.

Notification delivery does not itself authorize an action. A notification may
deep-link to Atlas or to the governed external approval surface, but an
authorization result is accepted only through an authenticated decision API
owned by the Approval Service.

### 7.9 Trusted External Control Plane

The trusted external control plane is responsible for:

- Authenticating to Atlas through the approved external-channel mechanism.
- Acting only for the one configured human reviewer.
- Presenting the pending queue and evidence without becoming authoritative for
  approval validity.
- Presenting a held message as needing manual handling without representing it
  as an approval or authorization path.
- Presenting knowledge facts, stale volatile facts, and ask-instead-of-guess
  questions without representing them as approval state.
- Submitting the one human owner's fact confirmations and knowledge answers
  through the governed knowledge API.
- Submitting approve or reject decisions through the Approval Service.
- Preserving correlation and decision identities required for audit and
  concurrency control.
- Treating webhook delivery as an event signal, not as authorization or proof
  of send outcome or manual resolution.

The external control plane must not execute the approved action, impersonate a
second reviewer, introduce roles, or become a second approval system of record.

---

## 8. Approval Lifecycle

### 8.1 Request Creation

An approval request may be created only after:

1. An agent or workflow proposes an action.
2. The action is structurally validated.
3. The Policy Engine determines that human approval is required.
4. The exact action identity and required context are available.
5. The request can bind to an agent, run, and run step where applicable.

Creation produces a canonical `Pending` approval and an audit event.

### 8.2 Review

Reviewing a request does not change its approval state.

Review progress may be represented as:

- `Unopened`.
- `InReview`.
- `AwaitingInformation`.

These values are review facets and must not replace the canonical approval
state.

### 8.3 Approve

An approve decision is accepted only when:

- The approval is `Pending`.
- The approval has not expired.
- The approval has not been cancelled.
- No conflicting decision exists.
- The reviewer is permitted to decide the request.
- Reviewer eligibility has been evaluated at decision time using the current
  workspace, environment, action, and risk context.
- Required step-up authentication has been satisfied.
- Required evidence is complete.
- The submitted decision references the current approval revision or equivalent
  concurrency identity.
- The exact bound action remains the action under review.
- The required decision reason is present.

An accepted decision changes approval state to `Approved`, records provenance,
and emits audit and continuation events.

Approval does not directly change the execution outcome to succeeded.

### 8.3.1 External Edit-Then-Approve

The external channel must provide edit-then-approve as an R0 interface
requirement. The human performs one continuous action that edits the draft,
approves the exact edited content, and continues directly to dispatch for
sending.

Because edited content changes the approval binding, the original approval
cannot authorize it. The Approval Service must create a superseding new
approval bound to the edited content, accept the decision against that new
approval, and create the send continuation through one governed workflow. The
external interface must not show a rejection followed by a fresh message, and
the original approval must not be recorded as human-rejected.

The original and superseding approvals remain linked in canonical history and
audit evidence. The future Engineering Specification must define atomicity or
recoverability, concurrency, idempotency, lineage, failure behavior, and the
external interface contract. Approval remains distinct from send outcome,
which is recorded as `Sent`, `Failed`, or `Indeterminate`.

### 8.4 Reject

A reject decision is accepted only when the request remains actionable and the
required explanatory reason is present.

An accepted rejection changes approval state to `Rejected`, records
provenance, emits an audit event, and informs the related run lifecycle.

Rejection remains available when approval evidence is incomplete.

### 8.5 Request Clarification

Request clarification:

- Leaves approval state as `Pending`.
- Changes review progress to `AwaitingInformation`.
- Records the question, initiating reviewer, destination when meaningful, and
  timestamp.
- Does not extend or replace the original expiry.
- Emits an activity and audit event.

Clarification supplied before expiry returns review progress to `InReview` and
becomes part of the evidence set.

The initial capability accepts clarification only from an authenticated human
actor in Atlas or a trusted internal system actor. Actor type, actor identity,
source, and timestamp are required provenance. Clarification remains untrusted
evidence.

If clarification changes the action, target, or decision-relevant content, the
existing request cannot authorize it. A new approval request is required.

### 8.5.1 Distinction From Ask-Instead-of-Guess

An ask-instead-of-guess question is created before a draft exists because the
agent lacks a required business fact. Its answer may create or update a governed
knowledge fact after validation. It does not create, advance, approve, reject,
or clarify an approval request and confers no authorization.

Request clarification is part of an existing pending approval and seeks missing
decision evidence without replacing the approval lifecycle. The two record
types, APIs, webhook events, state transitions, and audit meanings must remain
separate.

If expiry occurs first, the request becomes `Expired`. Later authorization
requires a new approval request.

### 8.6 Expiry

Expiry is based on the canonical expiry timestamp.

The Approval Service's authoritative time determines acceptance. Browser time
is presentation-only. A decision must be accepted before the exact expiry
instant; no authorization grace period applies.

Once expired:

- The approval becomes `Expired`.
- Approve, Reject, and Request clarification are unavailable.
- A decision in flight must fail closed if expiry occurs before the decision is
  accepted.
- The related run or step is informed through the defined lifecycle boundary.
- An audit event is recorded.

`Nearing expiry` and `Expiry imminent` are presentation and prioritization
facets, not persisted approval states.

### 8.7 Cancellation

Cancellation changes a pending request to `Cancelled` when the proposed action
is no longer applicable or the requesting workflow withdraws it through an
authorized path.

Cancellation must record its source and reason. A cancelled approval cannot be
decided or reused.

### 8.8 Continuation and Execution

After approval:

1. The runtime obtains the approved continuation.
2. The action, target, payload identity, policy context, and execution
   eligibility are revalidated.
3. Any mismatch, policy denial, expiry condition, or invalid continuation fails
   closed.
4. Atlas records and dispatches one authorized action intent using a stable
   idempotency identity.
5. Execution outcome is recorded separately.
6. Run state and audit history are updated.

If Atlas cannot determine whether an external action occurred, the outcome is
`Indeterminate`. Atlas must not retry automatically. Reconciliation or operator
investigation must establish whether retry is safe.

Approved authorization must not be transferred to a modified action. A changed
action requires a new approval request.

---

## 9. State Model

### 9.1 Canonical Approval States

```text
Pending
  |-- Approve --> Approved
  |-- Reject ---> Rejected
  |-- Expire ---> Expired
  +-- Cancel ---> Cancelled
```

All terminal states are immutable for decision purposes.

### 9.2 Review Facets

```text
Unopened <--> InReview <--> AwaitingInformation
```

Review facets apply only while the approval remains pending. They do not grant
authorization.

### 9.3 Execution Outcomes

Execution outcome is associated with the approval but does not replace its
decision state.

Supported logical outcomes are:

- NotAvailable.
- Pending.
- Succeeded.
- PartiallySucceeded.
- Failed.
- Indeterminate.

An `Approved` approval may therefore have a `Failed` execution outcome without
contradiction.

An `Approved` approval may also have an `Indeterminate` execution outcome when
Atlas cannot prove whether the external side effect occurred.

---

## 10. Logical Information Model

The existing Approval domain object remains the aggregate root for human
authorization.

### 10.1 Approval Identity

- Approval ID.
- Agent ID.
- Run ID.
- Run-step ID when applicable.
- Workspace and environment context when applicable.

### 10.2 Proposed Action Binding

- Action type.
- Exact target identity.
- Action summary.
- Content or payload reference.
- Content or payload integrity identity.
- Action revision or equivalent concurrency identity.
- Risk level.
- Risk reason.
- Governing policy reference.

### 10.3 Lifecycle

- Approval state.
- Review facet.
- Superseded approval ID and superseding approval ID when edit-then-approve
  replaces the bound content.
- Requested timestamp.
- Expiry timestamp.
- Cancellation timestamp and reason when applicable.

### 10.4 Decision

- Reviewer identity.
- Decision timestamp.
- Decision channel, `Internal` or `External`.
- Structured reason category when applicable.
- Explanatory reason text when required.
- Decision provenance or interaction source.

### 10.5 Evidence

- Evidence references.
- Evidence type.
- Evidence source or provenance.
- Evidence freshness or captured timestamp.
- Evidence sensitivity.
- Evidence completeness result.
- Redaction or truncation metadata.

### 10.6 Clarification

- Clarification request.
- Requesting reviewer.
- Destination when meaningful.
- Request timestamp.
- Response reference.
- Response source.
- Response timestamp.

### 10.7 Execution Outcome

- Execution status.
- Execution timestamp.
- Related run or step.
- Result reference.
- Normalized error reference when applicable.

The physical representation of this model belongs in a later data-design
specification. Sensitive content should be referenced rather than duplicated
where practical.

---

## 11. Evidence Architecture

### 11.1 Minimum Evidence Contract

The Approval Service must evaluate a minimum evidence contract before accepting
Approve.

The contract includes:

- Exact action.
- Exact target.
- Expected consequence and affected scope.
- Agent and run identity.
- Risk level and risk reason.
- Request and expiry timestamps.
- Relevant content or explicit no-content declaration.
- Evidence provenance.
- Governing policy or reason human approval is required.

### 11.2 Conditional Evidence

Action-specific evidence includes:

- Before-and-after state for modifications.
- Exact content for communications and publication.
- Audience and sensitivity for external sharing.
- Amount, currency, recipient, and purpose for financial actions.
- File identity, destination, and sensitivity for file transfers.

### 11.2.1 Facts Used by a Draft

Facts used by a draft fit within the existing approval evidence contract. The
evidence payload carries a typed `facts_used` collection rather than a new
top-level approval or decision field. Each item identifies the exact fact
revision used and presents the minimum fact value, provenance, volatility, and
confirmation context necessary for the human to review the draft.

The decision-context manifest binds the approval to those exact fact revisions.
If a referenced fact changes, is deleted, or becomes stale under its volatility
policy before execution, revalidation fails closed. Atlas must regenerate the
draft and create a new approval request when the bound draft is no longer valid.

### 11.3 Evidence Completeness

Evidence completeness is authoritative at the service boundary, not in the
browser.

An incomplete evidence set must:

- Prevent approval.
- Identify missing evidence categories.
- Continue to allow rejection while pending.
- Continue to allow clarification while pending.
- Produce observable diagnostic information without exposing sensitive content.

### 11.4 Evidence Snapshot

The architecture must preserve the decision context reviewed by the operator.

Evidence may reference canonical source objects, but mutable source content must
not make historical approval context misleading. The later data design must
choose an appropriate snapshot, version-reference, or integrity-reference
strategy according to sensitivity and retention requirements.

### 11.5 Decision-Context Manifest

Every terminal decision binds to an immutable decision-context manifest
containing approval and action identity, evidence references, source versions
when available, integrity digests, capture timestamps, redaction and truncation
metadata, and sensitivity and retention classifications.

Only the minimum content required to explain a decision is snapshotted when a
stable versioned source is unavailable. Large or sensitive content remains in
its governed source with a protected reference and integrity identity.

---

## 12. Decision Reasons

Every decision records a meaningful reason.

### 12.1 Low and Medium Risk Approval

- Structured reason category required.
- Free text optional unless `Other` is selected.

### 12.2 High and Critical Risk Approval

- Explanatory free text required.
- Structured category optional as a supplement.

### 12.3 Rejection

- Explanatory free text required for every rejection.
- Structured category may supplement the explanation.

Reason categories are governed product metadata. They must be stable enough for
history and reporting and must not be interpreted as policy authorization.

---

## 13. Security Architecture

### 13.1 Trust Boundaries

Trust boundaries exist between:

- Operator browser and Atlas control plane.
- Trusted external control plane and Atlas control plane.
- Approval Service and runtime continuation.
- Approval Service and evidence sources.
- Policy Engine and Approval Service.
- Runtime and connectors or tools.

### 13.2 Fail-Closed Rules

Approval must fail closed when:

- Reviewer identity is unavailable or not permitted.
- Approval state is stale or conflicting.
- Expiry cannot be evaluated reliably.
- Required evidence is missing.
- Action identity does not match the approval binding.
- Target or content changed.
- Applicable policy denies execution.
- Continuation identity is invalid or already consumed.
- Audit-critical decision provenance cannot be captured.

### 13.3 Non-Reuse

An approval authorizes only the bound action. It cannot authorize:

- A different action type.
- A different target.
- Modified content.
- A different agent or run.
- Execution after cancellation.
- A second execution.

### 13.4 Sensitive Data

- Queue summaries expose minimum necessary content.
- Evidence access follows the sensitivity of its source.
- Secrets and credentials never appear in approval payloads or previews.
- Audit events avoid unnecessary sensitive content.
- Content preview and history follow approved retention and redaction rules.

### 13.5 Reauthentication

The functional experience reserves a deliberate confirmation boundary for
high-risk actions. Exact reauthentication requirements and mechanisms remain a
separate authentication and authorization design decision.

Step-up authentication is required for every Critical approval and for
High-risk external communication, destructive actions, public or external
sharing, financial actions, credential or permission changes, and policy
exceptions.

### 13.6 Reviewer Authorization

Reviewer authorization is deny by default and evaluated at decision time.
The approval capability has exactly one configured human reviewer. The trusted
external control plane may submit a decision only as an authenticated channel
acting for that same human. It is not a reviewer and does not gain independent
human authority. Agents and other non-human service identities cannot act as
human reviewers. The evaluated human identity, external client identity when
applicable, authentication context, and decision channel are recorded with the
decision.

Multi-user approval, role-based access control, multi-tenant approval, reviewer
assignment, delegation, quorum, and multiple reviewers are prohibited by this
architecture. Supporting any of them requires a new architecture decision and
is not a compatible extension of this constraint.

### 13.7 Untrusted Evidence Isolation

Evidence metadata is normalized and validated at ingestion boundaries.
Previews render as inert content using allowlisted formats and prevent scripts,
active document content, remote embeds, and provider UI. Source evidence, agent
rationale, policy context, and operator content remain visually distinct.
Opening evidence must not trigger automatic model processing. Model summaries
remain untrusted derived evidence with source references. Redaction occurs
before logs, analytics, and audit export.

### 13.8 Retention Classification

Retention is classified independently for approval decision metadata, audit
events, decision-context manifests, decision reasons, evidence content,
clarification content, and execution-result content. Durable provenance and
integrity references follow audit policy; sensitive content follows its source
and sensitivity policy. History states when retained content is no longer
available.

---

## 14. Concurrency, Idempotency, and Consistency

### 14.1 Single Terminal Decision

Only one terminal decision may be accepted for an approval.

Concurrent or repeated decisions must produce one authoritative result and a
structured conflict response for all losing attempts.

### 14.2 Stale Review

A decision submitted from stale detail must not overwrite the current state.

The client must receive enough current-state information to present the actual
decision, expiry, or cancellation outcome.

### 14.3 At-Most-Once Execution

Approval and runtime continuation require a stable idempotency boundary that
prevents duplicate authorized intent and duplicate local dispatch. Provider
idempotency is used where available. When provider behavior is uncertain and no
safe idempotency or reconciliation mechanism exists, outcome is `Indeterminate`
and automatic retry is prohibited.

Detailed idempotency and reconciliation mechanisms belong in the Engineering
Specification.

### 14.4 Transaction Boundaries

Decision state, reviewer provenance, and the event that makes continuation
available must be coordinated so that Atlas does not present an approved state
without a recoverable continuation record.

The exact transactional or message-delivery pattern requires later detailed
design.

### 14.5 Authoritative Transaction and Continuation Intent

One authoritative transaction records the approval state transition, reviewer
and decision reason, durable audit event, and durable continuation intent.
Continuation is dispatched asynchronously from that intent. The consumer is
idempotent and revalidates the exact action before execution.

Atlas adopts a transactional-outbox pattern as the default consistency model,
as recorded by ADR-002. Physical design belongs in the Engineering
Specification.

---

## 15. Failure and Recovery

### 15.1 Decision Failure

If Atlas cannot confirm that a decision was recorded, it must return an
indeterminate or failed result rather than success. The operator must be able to
refresh canonical state safely.

### 15.2 Continuation Failure

An approved decision remains approved if continuation or execution fails. The
failure appears in execution outcome, related run state, alerts where
appropriate, and audit history.

If Atlas cannot establish whether an external action occurred, the result is
`Indeterminate`, not `Failed`. Reconciliation is required before retry.

### 15.3 Evidence Failure

If evidence cannot be retrieved or validated:

- Approve remains unavailable.
- Reject and Request clarification remain available while pending.
- The failure is observable.
- Sensitive internal details are not exposed to the operator.

### 15.4 Audit Failure

A decision fails closed if its durable local audit event cannot be recorded in
the authoritative transaction. A downstream telemetry, analytics, or
audit-export failure does not reverse a durable decision. Downstream delivery
retries asynchronously and preserves one logical event identity.

### 15.5 Expiry During Decision

If expiry occurs before the decision is accepted, the decision fails and the
canonical state becomes or remains `Expired`.

---

## 16. Audit Requirements

Audit events must be append-oriented and identify, as applicable:

- Event type.
- Approval ID.
- Agent ID.
- Run and step IDs.
- Actor type and identity.
- Decision channel, `Internal` or `External`, for each decision attempt and
  accepted decision.
- Delivery channel, `Internal` or `External`, for non-approval manual-handling
  notifications.
- Authenticated external client identity when applicable.
- Previous and resulting state.
- Action type and protected target reference.
- Risk level.
- Policy reference.
- Decision-reason category.
- Manual-hold reason category and policy or classification provenance when
  applicable.
- Protected decision-reason reference or appropriately governed content.
- Clarification activity.
- Expiry or cancellation reason.
- Correlation ID.
- Timestamp.
- Execution-outcome reference.

Material events include:

- Approval requested.
- Message held for manual handling without an approval request.
- Manual-handling notification emitted, delivered, or delivery failed.
- Approval superseded by an edit-then-approve operation.
- Clarification requested.
- Clarification received.
- Approval approved.
- Approval rejected.
- Approval expired.
- Approval cancelled.
- Approved continuation created or consumed.
- Execution succeeded, partially succeeded, or failed.
- Conflicting or duplicate decision rejected.

---

## 17. Observability Requirements

### 17.1 Metrics

The capability should expose:

- Pending approval count.
- Approval age.
- Time to expiry.
- Average and percentile wait time.
- Approval rate.
- Rejection rate.
- Clarification rate.
- Expired approval count.
- Cancelled approval count.
- Evidence-incomplete count.
- Decision-conflict count.
- Approved execution success and failure counts.
- Indeterminate execution count and reconciliation age.
- Approval volume by agent, action class, policy, and environment.
- Repeated materially similar request count.

### 17.2 Structured Logs

Structured logs should include:

- Approval ID.
- Agent ID.
- Run ID.
- Correlation ID.
- Component.
- Event type.
- Result category.
- Error category.
- Timestamp.

Logs must not include secrets, credentials, or full sensitive payloads.

### 17.3 Alerts

Future operational alerts may cover:

- Approval nearing expiry.
- Critical approval pending beyond threshold.
- Repeated evidence-completeness failure.
- Approval continuation failure.
- Repeated conflicting decisions.
- Audit event failure.
- Accumulating approval backlog.

---

## 18. Expiry Presentation Architecture

Expiry presentation is derived from canonical request and expiry timestamps.

### 18.1 Nearing Expiry

`Nearing expiry` begins when remaining time is at or below 20 percent of the
original approval window, bounded to a minimum of 15 minutes and a maximum of
24 hours.

### 18.2 Expiry Imminent

`Expiry imminent` begins when remaining time is at or below 5 percent of the
original approval window, bounded to a minimum of 5 minutes and a maximum of 1
hour.

These are derived operational facets. They must not create additional approval
states or alter canonical expiry.

All time evaluation must use a consistent authoritative time basis. The
interface may render relative time locally but must preserve the exact expiry
timestamp.

The Approval Service's time is authoritative for acceptance. No grace period
applies after expiry. Inability to evaluate authoritative time fails closed.

---

## 19. Scale Constraint and Future Extension

The approval architecture supports one human reviewer through either the Atlas
internal channel or one or more separately authenticated clients of the
governed external channel. Channel count does not change reviewer count.

The hard constraint is single reviewer only. Multi-user approval, role-based
access control, multi-tenant approval, reviewer assignment, delegation,
separation of duties, sequential or parallel reviewers, quorum decisions, and
reviewer groups are not supported and are not planned extensions of this
architecture.

Future extensions may improve queue delivery, webhook reliability, evidence
presentation, reconciliation, and external-client operations without weakening
the single-reviewer constraint or the exact action binding.

### 19.1 Approval-Flood Protection

Atlas monitors creation volume by agent, action class, policy, and environment.
Abnormal volume, repeated materially similar requests, and repeated
evidence-incomplete requests produce metrics and alerts. Resource controls must
not silently authorize actions. Critical and near-expiry requests remain
visible during backlog conditions, and different exact-action bindings are not
automatically merged.

---

## 20. Architecture Conformance

This specification conforms to the existing Atlas architecture by:

- Extending the existing Approval Service rather than introducing a duplicate service.
- Preserving Policy Engine authority.
- Preserving Action Validator treatment of agent output as untrusted.
- Preserving runtime revalidation before execution.
- Preserving PostgreSQL as the planned runtime system of record.
- Preserving the Audit Writer and append-oriented audit model.
- Preserving the control-plane and execution-plane separation.
- Extending the approval trust boundary through the existing Approval Service
  instead of creating a parallel approval authority.
- Preserving one human reviewer across internal and external decision channels.
- Avoiding a new deployment container or infrastructure framework.

The external decision channel changes the approval trust boundary and is
governed by accepted ADR-003. Any later decision that changes data
architecture, authentication, authorization, runtime continuation, deployment
boundaries, audit immutability, or the single-reviewer constraint must also
follow the ADR process before implementation.

---

## 21. Approved Architecture and Security Decisions

| Decision area | Approved resolution |
| --- | --- |
| Evidence history | Immutable decision-context manifest with source versions and integrity references; minimum snapshots only |
| Concurrency identity | Monotonic approval revision required by every decision attempt |
| Decision consistency | Authoritative transaction plus durable transactional outbox |
| Duplicate prevention | Stable dispatch identity, idempotent consumer, provider idempotency, and indeterminate outcome when uncertain |
| Clarification provenance | Authenticated Atlas human or trusted internal actor only in the initial capability |
| Step-up authentication | Critical always; specified High-risk actions require step-up |
| Reviewer eligibility | Deny by default and evaluated at decision time |
| Reviewer model | Exactly one human reviewer; no multi-user, role-based access control, or multi-tenant approval |
| Decision channels | Internal Atlas channel and authenticated external channel governed by accepted ADR-003 |
| Decision provenance | Human identity and `Internal` or `External` channel; authenticated external client when applicable |
| Manual-hold provenance | Hold reason and policy or classification provenance; `Internal` or `External` delivery channel; no approval or reviewer decision |
| Audit failure | Durable local audit failure blocks decision; downstream export retries asynchronously |
| Retention | Durable provenance separated from sensitive-content retention |
| Notifications | May deep-link to a governed approval or manual-handling surface but cannot record decisions or override suppression |

---

## 22. Architecture Acceptance Criteria

The architecture is acceptable when:

1. Approval is bound to one exact action, target, content identity, agent, run, expiry, and reviewer.
2. Policy Engine authority remains separate from human authorization.
3. Approval Service owns canonical approval state.
4. Atlas Web is not trusted to enforce approval validity.
5. A governed external client may submit decisions only through the
   authenticated Approval Service boundary for the same single human reviewer.
6. Multi-user, role-based access control, multi-tenant approval, and multiple
   reviewers remain prohibited.
7. Required evidence is enforced at the service boundary.
8. Reject and Request clarification remain possible when approval evidence is incomplete.
9. Clarification does not change approval state or extend expiry.
10. Only one terminal decision can be accepted.
11. Expired and cancelled approvals cannot be decided.
12. Approved actions are revalidated before execution.
13. A changed action requires a new approval.
14. Atlas records one authorized action intent, suppresses duplicate dispatch,
    uses provider idempotency where available, and requires reconciliation for
    indeterminate external outcomes.
15. Approval decision and execution outcome remain separate.
16. Material events produce append-oriented audit evidence with decision-channel provenance.
17. Sensitive content is minimized in queue, logs, and audit records.
18. Failures do not imply authorization or execution success.
19. Existing control-plane, runtime, policy, connector, audit, and deployment boundaries remain intact.
20. The external channel supports R0 edit-then-approve as one continuous user
    action, creates a linked superseding approval for the exact edited content,
    does not record a human rejection, and continues directly to send dispatch.
21. A suppressed clinical or protected-health-information message produces a
    minimized non-approval manual-handling event for the governed external
    product client without creating a draft, proposed action, approval, or
    authorization path.

---

## 23. Next Governance Steps

Before implementation reaches Definition of Ready:

1. The implementation artifact links accepted ADR-003, accepted ADR-004 when
   the external product contract is in scope, and this canonical architecture.
2. Phase 3 foundations are complete before Phase 5 external approval or
   manual-handling contract implementation, and Phase 5 foundations are
   complete before the Phase 6 Gmail end-to-end workflow.
3. The Human Approvals Engineering Specification defines the authenticated
   queue and decision APIs, external-client and human authentication, evidence
   minimization, webhook semantics, audit fields, errors, rate limits,
   retention, observability, threat mitigations, and the R0 edit-then-approve
   workflow, interface contract, and non-approval manual-handling event contract.
4. Detailed security and privacy review approves the Engineering Specification.
5. An implementation Work Order links the accepted ADR, architecture, and
   Engineering Specification and defines observable acceptance criteria,
   exclusions, dependencies, verification evidence, and a review owner.
6. The review owner confirms every applicable item in
   `docs/governance/definition-of-ready.md`.

No implementation may begin from this architecture specification alone.
