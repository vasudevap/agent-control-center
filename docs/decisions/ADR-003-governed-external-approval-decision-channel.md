# ADR-003 - Governed External Approval Decision Channel

**Status:** Accepted
**Date:** 2026-07-16
**Decision Owners:** Architecture and Security Review
**Review Owner:** Repository Maintainer
**Accepted:** 2026-07-16
**Accepted By:** Repository Maintainer
**Updated:** 2026-07-17
**Scope:** Human Approvals trust boundary

---

## Context

Atlas currently defines its web interface as the only human approval decision
surface. MushingMule is a separate product that will provide a customer-facing
approval surface. Its first use case is a solo operator whose email agent drafts
replies and requires that one human to approve or reject each reply before the
Gmail agent sends it.

Treating external decisions as a later adapter would risk duplicating approval
state, weakening evidence and action binding, or creating a second authority.
The Approval Service must therefore recognize the external decision channel as
a first-class trust boundary from its initial design.

The platform, approval framework, and Gmail agent are not yet built. This ADR
defines a future boundary and does not authorize implementation.

## Decision

Atlas will accept approval decisions through two governed channels:

1. The internal Atlas decision channel.
2. An authenticated external decision channel used by a trusted external
   control plane, initially MushingMule.

The Approval Service remains the sole system of record and decision authority.
The external control plane is a client acting for the configured human, not a
second approval service and not an independent reviewer.

Both channels must use the same approval lifecycle, exact action binding,
evidence completeness, expiry, concurrency, reauthentication, fail-closed,
continuation, and audit rules. Every decision attempt and accepted decision
must record its channel as `Internal` or `External`. External decisions must
also record the authenticated external client and the human identity for whom
it acts.

The external channel is designed into the Approval Service from the start. Its
later backend scope includes:

- An authenticated API to read the pending-approval queue with evidence.
- An authenticated API to submit an approve or reject decision.
- Webhook events for approval pending and for send outcomes of `Sent`, `Failed`,
  or `Indeterminate`.
- An authentication model for a trusted external control plane acting for one
  human.
- Audit provenance that distinguishes internal and external decisions.

### R0 Interface Requirement: Edit-Then-Approve

The external channel must support edit-then-approve as one continuous user
action that ends in dispatch of the edited message for sending. Editing the
draft changes decision-relevant content, so the existing approval cannot
authorize it. Atlas must create a superseding new approval bound to the exact
edited content, accept the human's approval of that new request, and create the
send continuation through one governed service workflow.

The external interface must not present this operation as a rejection followed
by creation of a fresh message. The superseded request and its replacement must
remain linked for audit, concurrency, and history. The original request must
not be recorded as human-rejected, and no intermediate state may permit the
unedited or edited content to send without the applicable exact-content
approval.

This is an R0 requirement for the external-channel interface and for the future
Engineering Specification. The detailed design must define the atomicity or
recoverability boundary across supersession, replacement approval, decision,
continuation, and send dispatch. Send outcome remains separate from approval
and must still be recorded as `Sent`, `Failed`, or `Indeterminate`.

### Hard Constraint

The approval capability has exactly one human reviewer. Multi-user approval,
role-based access control, multi-tenant approval, reviewer assignment,
delegation, multiple reviewers, and quorum decisions are prohibited. The
external control plane acts only for the same single human who may use Atlas.
Adding channels does not add reviewers.

Changing this constraint requires a new ADR and architecture review. It is not
an incremental implementation detail.

## Trust Model

- The external control plane authenticates as an approved client through a
  mechanism selected in later security design.
- Client authentication does not replace proof that the decision is attributable
  to the configured human.
- The Approval Service authorizes the request, validates canonical approval
  state, and records the decision atomically under ADR-002.
- Queue and evidence responses expose only the minimum data required for the
  decision and follow source sensitivity and retention controls.
- Webhooks are authenticated event notifications. They do not authorize an
  action and do not become authoritative proof of approval or send outcome.
- Failure to authenticate the client, attribute the human, validate evidence,
  or record audit provenance causes the decision to fail closed.

## Consequences

### Positive

- MushingMule can provide a customer-facing approval experience without becoming
  a separate approval authority.
- Internal and external decisions share one canonical lifecycle and integrity
  model.
- Channel provenance supports audit and incident investigation.
- Designing the boundary early avoids retrofitting APIs, identity, events, and
  audit fields after the Approval Service is built.

### Trade-offs

- The initial Approval Service design must include external-client identity,
  channel provenance, API authorization, webhook delivery, and evidence
  disclosure boundaries even before the external client is implemented.
- Security review must distinguish the human reviewer from the control plane
  acting for that human.
- Webhook retry, ordering, deduplication, and outcome reconciliation require
  detailed design.

### Risks

- Weak client authentication could permit unauthorized decisions.
- Weak human attribution could make an external client appear to be the
  reviewer.
- Excessive evidence disclosure could expose sensitive email content.
- Duplicate or out-of-order webhook delivery could mislead the external user
  interface.
- Later implementation could accidentally introduce user, role, or tenant
  concepts that violate the single-reviewer constraint.

## Alternatives Considered

### Accept decisions only inside Atlas

Rejected because it prevents MushingMule from serving as the customer-facing
approval surface and forces the operator to leave that product to decide.

### Let MushingMule own approval state

Rejected because two systems of record could diverge and weaken Atlas policy,
evidence, audit, expiry, and continuation controls.

### Treat the external channel as a later adapter

Rejected because identity, evidence disclosure, decision provenance, webhook
semantics, and failure behavior are trust-boundary concerns that must shape the
Approval Service design from the start.

### Design now for teams, roles, or tenants

Rejected because the authorized use case has one human reviewer and explicitly
prohibits multi-user, role-based access control, and multi-tenant scope.

## Implementation Constraints and Sequencing

No implementation may begin under this ADR alone. The external approval channel
follows the roadmap phase boundaries:

- Phase 3 establishes the authenticated external API, client-authentication,
  and webhook-delivery foundations.
- Phase 5 establishes the generic external approval queue, evidence, decision,
  continuation, and approval-event contracts.
- Phase 6 supplies Gmail-specific approval evidence and send execution for the
  first end-to-end workflow.

Before implementation reaches Definition of Ready:

1. The implementation artifact must link this accepted ADR and the approved
   canonical Human Approvals architecture update.
2. Architecture and Security Review must approve the future Engineering
   Specification against this trust boundary.
3. An Engineering Specification must define API contracts, external-client and
   human authentication, authorization, evidence minimization, webhook
   authentication and delivery semantics, channel audit fields, error behavior,
   rate limits, retention, observability, threat mitigations, and the R0
   edit-then-approve workflow and interface contract.
4. Each implementation increment must be authorized by an approved Work Order
   after its phase-specific prerequisites are confirmed complete.
5. Acceptance criteria, test and verification plans, review ownership,
   dependencies, security and privacy controls, data ownership, and unresolved
   decisions must satisfy `docs/governance/definition-of-ready.md`.

This ADR does not modify current frontend prototypes or in-flight work orders.
