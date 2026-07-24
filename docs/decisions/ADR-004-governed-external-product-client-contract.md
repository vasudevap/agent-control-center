# ADR-004 - Governed External Product Client Contract

**Status:** Superseded by `ADR-008 - Atlas Agent Visibility and Lifecycle Control Center`
**Date:** 2026-07-16
**Updated:** 2026-07-17
**Decision Owners:** Architecture and Security Review
**Review Owner:** Repository Maintainer
**Review State:** Architecture and Security Review Complete
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Scope:** Atlas platform-client relationship
**Related Decision:** `ADR-003 - Governed External Approval Decision Channel`

---

> Historical decision: retained as evidence for the original Atlas
> external-product-client direction. It no longer governs the active MVP.

## Context

Atlas is both an operator-facing control plane and a governed backend platform.
Its own dashboard is the first-party control surface. Atlas is also being adopted
by an external customer-facing product that needs to read governed platform
state, present approval evidence, submit approval decisions, and receive
lifecycle events without becoming a second system of record.

MushingMule is the first external product client. It acts on behalf of the single
human owner and reviewer. Atlas must not depend on MushingMule-specific concepts,
deployment choices, or user experience. The platform-client contract must be
generic enough for MushingMule to consume while remaining owned and governed by
Atlas.

ADR-003 establishes the narrower external approval decision channel. A broader
decision is required to establish the general relationship between Atlas and an
external product client for agent status, run status, approvals, evidence, and
webhook events.

The Gmail clinical and protected-health-information suppression rule creates no
draft and no approval. The external product contract must still surface that a
message was held so the human owner can take over manually without weakening
the suppression rule.

The current scope permits one external product client acting for the single
human reviewer. Multiple external product clients, multi-tenant isolation,
billing, and marketplace capabilities are not part of this decision.

## Decision

Atlas will support two governed classes of control-plane consumer:

1. The first-party Atlas dashboard.
2. One authenticated external customer-facing product client acting on behalf
   of the single human owner and reviewer.

The authenticated Atlas API and authenticated outbound webhooks form the
platform contract for the external product client. Atlas remains authoritative
for platform state, authorization, approval validity, policy enforcement,
execution continuation, execution outcomes, and audit evidence.

The external product client is a presentation and interaction surface. It may:

- Read the pending-approval queue and governed decision evidence.
- Read agent status and run status.
- Submit an approve or reject decision through the Approval Service boundary.
- Receive approval-pending and send-outcome webhook events.
- Receive a minimized `message.held_for_manual_handling` event for a message
  suppressed by policy.

The external product client must not:

- Become a second system of record for Atlas state.
- Execute agent tools or connector actions directly.
- Bypass the Approval Service, Policy Engine, Connector Runtime, or Audit Writer.
- Assert an independent human reviewer identity.
- Introduce additional reviewers, roles, tenants, or tenant isolation under this
  decision.
- Require Atlas to expose MushingMule-specific domain concepts in the general API.

MushingMule is the first example of this consumer class. Atlas contracts must use
generic external-product-client terminology and remain independent of MushingMule.

## Contract Boundary

The external product client contract consists of:

- An authenticated API with deny-by-default scope.
- Versioned request and response contracts.
- Structured errors and correlation identities.
- Approval revision and idempotency controls where decisions are submitted.
- Minimum-necessary evidence disclosure.
- Authenticated webhook events with delivery, retry, ordering, and deduplication
  semantics defined before implementation.
- Audit provenance for external-client activity.

Client authentication and attribution to the single human owner are distinct
security concerns. The exact authentication and attribution mechanism remains a
Phase 3 and Phase 5 security design decision.

Webhooks notify the external product client that authoritative state may have
changed. They do not authorize actions and do not replace an authoritative API
read for approval, hold, or execution outcome reconciliation.

### Non-Approval Manual-Handling Event

When the Policy Engine suppresses an inbound message classified as clinical or
as containing protected health information, Atlas will expose a canonical hold
reference through the API and emit `message.held_for_manual_handling` through
the authenticated webhook channel.

The event must identify the message through a governed source reference and
include a reason category such as `Clinical` or
`ProtectedHealthInformation`. It may include the hold identifier, agent and run
references, sensitivity classification, correlation identity, and held
timestamp. It must not include message content or other sensitive evidence
unless a later approved contract establishes necessity and permission.

The event is not an approval request. It contains no draft, creates no
approvable action, confers no authorization, and cannot be used to trigger
automatic drafting or override the suppression decision. The external product
client may present only a manual-handling path for the item.

Audit evidence records the hold reason, policy and classification provenance,
authenticated external client, delivery channel, correlation identity, and
timestamp. The channel uses the same `Internal` or `External` vocabulary as
decision-channel provenance, but the audit record must not claim a reviewer,
decision, or approval identity because no decision occurred.

## Scope Constraint

This decision is limited to one external product client acting for one human
owner and reviewer.

The following remain outside this decision:

- Multiple external product clients operating concurrently.
- Multi-user and role-based operation.
- Multi-tenant isolation.
- Billing and subscription management.
- A public or private product marketplace.
- General partner-platform or developer-platform capabilities.

A future multi-product platform is a possible direction. It requires a separate
architecture decision covering client registration, isolation, ownership,
versioning, quotas, lifecycle, and operational governance.

## Consequences

### Positive

- Atlas has an explicit platform contract beyond its own dashboard.
- External customer-facing experiences can reuse Atlas governance without
  duplicating control-plane authority.
- The first external client validates a general contract rather than creating a
  product-specific backend fork.
- API, webhook, identity, audit, and observability requirements can shape the
  platform foundation before implementation.

### Trade-offs

- Phase 3 must treat API contract governance and external-client authentication
  as platform responsibilities.
- Phase 5 must expose approval evidence, decisions, and the non-approval
  manual-handling event without weakening ADR-002 or ADR-003.
- Webhook delivery introduces reliability and reconciliation requirements.
- External evidence disclosure requires explicit minimization and retention
  boundaries.

### Risks

- A product-specific contract could couple Atlas to MushingMule.
- Weak external-client authentication could expose platform state or permit an
  unauthorized decision attempt.
- Confusing client authentication with human attribution could weaken approval
  audit integrity.
- Webhook consumers could treat a notification as authoritative state.
- A consumer could incorrectly render a held-message event as an approval or
  use it to request a draft.
- An over-broad held-message payload could disclose sensitive clinical content.
- The initial single-client contract could be extended informally into a
  multi-product or multi-tenant platform without the required architecture work.

## Alternatives Considered

### Dashboard-only Atlas

Rejected because it prevents governed external customer-facing products from
using Atlas as their backend engine.

### MushingMule-specific backend endpoints

Rejected because Atlas must own a general platform contract and must not depend
on one consuming product.

### External client owns approval or run state

Rejected because duplicate systems of record would weaken policy, audit,
concurrency, and recovery controls.

### Design a multi-product or multi-tenant platform now

Rejected for the current scope. The authorized requirement is one external
product client acting for the single human reviewer. Broader platform scope
requires separate architecture decisions.

## Deferred Design Work

The following architecture documents require design-time updates during the
relevant Phase 3 or Phase 5 specification work. This ADR records the obligation
but does not design those changes:

- `docs/architecture/07-security-architecture.md`: external-client trust
  boundary and the distinction between client authentication and human
  attribution.
- `docs/architecture/08-data-architecture.md`: external client identity,
  decision-channel provenance, human attribution fields, and non-approval
  manual-hold event provenance.
- `docs/architecture/11-observability.md`: external API, webhook delivery, and
  external decision-channel metrics.

## Sequencing Reconciliation

The roadmap, ADR-003, and Human Approvals architecture use the same phased
boundary for review:

- Phase 3 establishes the general external-client API, authentication, and
  webhook foundations.
- Phase 5 establishes the generic external approval contract governed by
  ADR-002 and ADR-003, plus the non-approval manual-handling event contract.
- Phase 6 supplies the Gmail-specific evidence and send execution needed for the
  first end-to-end product workflow.

This sequencing separates general platform and approval contracts from the
Gmail-specific end-to-end workflow without permitting implementation before the
applicable phase reaches Definition of Ready.

## Governance and Acceptance

This ADR is Accepted and has no implementation authority.

The acceptance review confirmed:

1. The platform-client relationship aligns with the Atlas control-plane and
   execution-plane separation.
2. The accepted trust boundary is suitable for later detailed security design.
3. Atlas remains authoritative for state, policy, approval validity, execution,
   outcomes, and audit evidence.
4. Client authentication and human attribution remain distinct concerns.
5. The held-message event is minimized, non-approvable, non-authorizing, and
   unable to override clinical or protected-health-information suppression.
6. The contract remains single-reviewer and introduces no users, roles, RBAC,
   tenants, or multi-tenant isolation.
7. Phase 3, Phase 5, and Phase 6 sequencing is internally consistent.

The durable review evidence is recorded in
`docs/reviews/ADR-004-governed-external-product-client-contract-review.md`.

After acceptance, implementation still requires approved Phase 3 and Phase 5
Engineering Specifications or Work Orders that satisfy the Definition of Ready.
Those artifacts must define the external API contract, authentication,
authorization, human attribution, evidence minimization, webhook delivery,
audit fields, manual-hold reason and channel provenance, observability, failure
behavior, versioning, rate limits, and verification evidence.

No implementation may begin under this accepted decision or the documentation
changes that reference it. This decision does not modify frontend prototypes or
in-flight Work Orders.
