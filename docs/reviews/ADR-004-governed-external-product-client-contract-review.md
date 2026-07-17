# ADR-004 Governed External Product Client Contract Review Record

**Status:** Accepted
**Decision Record:** `docs/decisions/ADR-004-governed-external-product-client-contract.md`
**Review Owner:** Repository Maintainer
**Date Routed:** 2026-07-17
**Date Reviewed:** 2026-07-17
**Reviewed By:** Repository Maintainer
**Review Method:** Explicit evidence-based maintainer self-review under the repository pull-request process

## Review Objective

Determine whether ADR-004 should be accepted, revised, or rejected as the
general Atlas platform-client relationship for one authenticated external
customer-facing product client acting for the single human owner and reviewer.

## Scope Presented for Review

- The Atlas dashboard and one governed external product client consume the
  authoritative Atlas API.
- Authenticated webhooks notify the external product client of approval pending,
  send outcome, and held-for-manual-handling events.
- ADR-003 remains authoritative for external approval decisions.
- A policy-suppressed clinical or protected-health-information message is
  surfaced only through a minimized non-approval manual-handling event.
- Atlas remains independent of Plaintrol. Plaintrol is the first example client.
- Multi-user, role-based, multi-tenant, billing, marketplace, and multiple
  external product client concerns remain outside this decision.

## Architecture Review Findings

- **Control-plane separation:** Pass. The external product client calls the
  Backend API and cannot call agent tools, connectors, or execution-plane
  components directly.
- **Authoritative state:** Pass. Atlas remains the sole system of record and
  retains authority for policy, approval validity, continuation, execution
  outcomes, and audit evidence.
- **Contract independence:** Pass. Plaintrol is identified only as the first
  example consumer. The API and webhook contract uses generic external product
  client terminology.
- **Container responsibility:** Pass. The Backend API owns the governed inbound
  API boundary and outbound webhook responsibility without introducing a new
  deployment container.
- **Sequencing:** Pass. Phase 3 establishes API, authentication, and webhook
  foundations; Phase 5 establishes generic approval and manual-handling
  contracts; Phase 6 supplies Gmail-specific evidence and execution.
- **Scope constraint:** Pass. The decision permits one external product client
  acting for one human reviewer and excludes multi-user, role-based,
  multi-tenant, billing, marketplace, and multiple-client capabilities.

## Security Review Findings

- **Authentication and attribution:** Pass for architecture acceptance. Client
  authentication is explicitly separate from attribution to the single human
  reviewer. The mechanism remains mandatory Phase 3 and Phase 5 detailed design.
- **Authorization:** Pass for architecture acceptance. External API access is
  deny by default and remains enforced by Atlas. Review corrected one legacy
  container-document phrase from `Role and policy checks` to `Authorization and
  policy checks` so the current decision cannot be read as introducing RBAC.
- **Evidence minimization:** Pass. Approval evidence is minimum necessary, and
  the manual-handling event excludes message content unless a later approved
  contract proves necessity and permission.
- **Webhook authority:** Pass. Webhooks are authenticated notifications and do
  not authorize actions or replace authoritative API reconciliation.
- **Suppression integrity:** Pass. `message.held_for_manual_handling` has no
  draft, proposed action, approval identity, or authorization and cannot
  override clinical or protected-health-information suppression.
- **Audit provenance:** Pass. External-client and channel provenance are
  required. The non-approval hold records reason and delivery provenance without
  fabricating a reviewer, decision, or approval identity.
- **Failure posture:** Pass for architecture acceptance. Authentication,
  authorization, attribution, evidence, and durable audit failures remain
  fail-closed requirements for later detailed design.

## Review Limitations and Required Follow-Up

Acceptance establishes the platform-client stance but deliberately does not
select authentication mechanisms, schemas, retry policies, rate limits,
retention periods, or metric thresholds. Those decisions remain required in the
Phase 3 and Phase 5 Engineering Specifications and the deferred updates to
security, data, and observability architecture.

## Deferred Detailed Design

Acceptance does not resolve the later design work recorded for:

- `docs/architecture/07-security-architecture.md`
- `docs/architecture/08-data-architecture.md`
- `docs/architecture/11-observability.md`

Those updates belong to the authorized Phase 3 and Phase 5 Engineering
Specifications.

## Acceptance Decision

ADR-004 is **Accepted** on 2026-07-17 by the Repository Maintainer.

The acceptance basis is:

1. All required Architecture Review findings pass.
2. All required Security Review findings pass at the architecture-decision
   level.
3. The wording cleanup noted above removes a possible RBAC implication.
4. Canonical architecture and roadmap sequencing are consistent.
5. Deferred detailed design remains explicit and implementation remains
   prohibited until separate governed artifacts reach Definition of Ready.

## Implementation Boundary

This review record and accepted ADR-004 authorize no implementation. Phase 3 or
Phase 5 implementation requires a separate approved Engineering Specification
and Work Order that satisfy the Definition of Ready.
