# Atlas Human Approvals Architecture

**Status:** Approved
**Version:** 1.0
**Date:** 2026-07-13
**Capability:** Human Approvals
**Product:** Atlas

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
12. Extend to future team review without redesigning the core domain.

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
- Active assignment in single-reviewer mode.
- Escalation routing.
- Multi-reviewer and quorum approval.
- Delegation.
- External-channel approval decisions.
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
    |                         |
    |                         | inspect evidence and decide
    |                         v
    +-------------------- Audit Writer
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
activity.

It must preserve traceability without allowing later state changes to rewrite
earlier events.

### 7.8 Notification Capability

A future notification capability may notify an operator about pending,
near-expiry, clarification, or completed approvals.

Notification delivery must not become an alternative authorization channel
unless explicitly designed and approved later.

The initial capability accepts decisions and clarification only within Atlas.
Notifications may deep-link to Atlas but cannot carry an authorization result.

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
- Requested timestamp.
- Expiry timestamp.
- Cancellation timestamp and reason when applicable.

### 10.4 Decision

- Reviewer identity.
- Decision timestamp.
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
Eligibility may be scoped by workspace, environment, action class, and risk.
Agents and non-human service identities cannot act as human reviewers. The
evaluated identity and authorization context are recorded with the decision.

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
- Previous and resulting state.
- Action type and protected target reference.
- Risk level.
- Policy reference.
- Decision-reason category.
- Protected decision-reason reference or appropriately governed content.
- Clarification activity.
- Expiry or cancellation reason.
- Correlation ID.
- Timestamp.
- Execution-outcome reference.

Material events include:

- Approval requested.
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

## 19. Scalability and Future Extension

The architecture must scale from one operator to future teams without changing
the core approval identity or decision model.

Future extensions may add:

- Owner and assignee routing.
- Escalation destinations.
- Delegation.
- Separation of duties.
- Sequential reviewers.
- Parallel reviewers.
- Quorum decisions.
- Policy-specific reviewer groups.
- Bulk rejection and assignment.
- Constrained bulk approval through a separately approved design.
- External notification channels that deep-link to Atlas.

Future multi-reviewer workflows should compose reviewer requirements around the
same exact action binding. They must not weaken evidence, expiry, non-reuse,
audit, or execution controls.

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
- Avoiding a new deployment container or infrastructure framework.

No ADR is required solely to adopt this capability within the existing
boundaries. Any later decision that changes data architecture, authentication,
authorization, runtime continuation, deployment boundaries, or audit
immutability strategy must follow the ADR process before implementation.

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
| Audit failure | Durable local audit failure blocks decision; downstream export retries asynchronously |
| Retention | Durable provenance separated from sensitive-content retention |
| Notifications | Deferred; notifications may deep-link to Atlas but cannot record decisions |

---

## 22. Architecture Acceptance Criteria

The architecture is acceptable when:

1. Approval is bound to one exact action, target, content identity, agent, run, expiry, and reviewer.
2. Policy Engine authority remains separate from human authorization.
3. Approval Service owns canonical approval state.
4. Atlas Web is not trusted to enforce approval validity.
5. Required evidence is enforced at the service boundary.
6. Reject and Request clarification remain possible when approval evidence is incomplete.
7. Clarification does not change approval state or extend expiry.
8. Only one terminal decision can be accepted.
9. Expired and cancelled approvals cannot be decided.
10. Approved actions are revalidated before execution.
11. A changed action requires a new approval.
12. Atlas records one authorized action intent, suppresses duplicate dispatch,
    uses provider idempotency where available, and requires reconciliation for
    indeterminate external outcomes.
13. Approval decision and execution outcome remain separate.
14. Material events produce append-oriented audit evidence.
15. Sensitive content is minimized in queue, logs, and audit records.
16. Failures do not imply authorization or execution success.
17. Existing control-plane, runtime, policy, connector, audit, and deployment boundaries remain intact.
18. Deferred team and bulk capabilities can extend the model without redesigning the core approval aggregate.

---

## 23. Next Governance Steps

Before implementation:

1. Update affected canonical architecture and data documentation during detailed design where required.
2. Produce the Human Approvals Engineering Specification.
3. Complete detailed security and privacy review of the Engineering Specification.
4. Produce an implementation Work Order that meets the Definition of Ready.

No implementation may begin from this architecture specification alone.
