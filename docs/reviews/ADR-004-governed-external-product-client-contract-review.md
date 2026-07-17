# ADR-004 Governed External Product Client Contract Review Request

**Status:** Pending Architecture and Security Review
**Decision Record:** `docs/decisions/ADR-004-governed-external-product-client-contract.md`
**Review Owner:** Repository Maintainer
**Date Routed:** 2026-07-17

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

## Required Review Findings

Architecture Review must confirm:

- The platform-client relationship preserves control-plane and execution-plane
  separation.
- Atlas remains the sole system of record and execution authority.
- The external product contract is generic and does not couple Atlas to
  Plaintrol.
- Phase 3, Phase 5, and Phase 6 sequencing is coherent.

Security Review must confirm:

- Client authentication and human attribution are distinct concerns.
- Evidence disclosure is minimum necessary.
- Webhooks do not authorize actions or replace authoritative reconciliation.
- The held-message event cannot create a draft, approval, or suppression
  override.

## Deferred Detailed Design

Acceptance does not resolve the later design work recorded for:

- `docs/architecture/07-security-architecture.md`
- `docs/architecture/08-data-architecture.md`
- `docs/architecture/11-observability.md`

Those updates belong to the authorized Phase 3 and Phase 5 Engineering
Specifications.

## Acceptance Procedure

1. Record Architecture Review findings.
2. Record Security Review findings.
3. Revise ADR-004 if either review requires changes.
4. If accepted, update ADR-004 status, acceptance date, and accepted-by fields.
5. Update `docs/decisions/README.md` from Proposed to Accepted.
6. Confirm the canonical architecture remains internally consistent.

## Implementation Boundary

This review request and ADR-004 authorize no implementation. Phase 3 or Phase 5
implementation requires a separate approved Engineering Specification and Work
Order that satisfy the Definition of Ready.
