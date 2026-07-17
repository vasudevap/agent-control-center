# Work Order 020: Authorization and External-Client Identity Boundary

**Status:** Completed
**Work Order ID:** WO-020
**Type:** Backend security foundation
**Implementation Authorization:** Granted
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Architecture Authority:** [Phase 3 Target Architecture](../implementation-plans/phase-3-platform-foundation-target-architecture.md), [Security Architecture](../architecture/07-security-architecture.md)
**Decision Authority:** [ADR-003](../decisions/ADR-003-governed-external-approval-decision-channel.md), [ADR-004](../decisions/ADR-004-governed-external-product-client-contract.md)
**Prerequisite:** [WO-019](./019-owner-authentication-and-session-foundation.md)
**Review Record:** [WO-020 Authorization Implementation Report](../reviews/WO-020-authorization-implementation-report.md)

## 1. Purpose

Create the deny-by-default authorization boundary and replace the current
shared-header external-client scaffold with a replay-resistant identity proof.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Authorization input | Typed `actor`, `channel`, `resource`, `action`, and optional risk/environment context. |
| Actor kinds | `human_owner`, `external_client`, and `service`; none may be silently converted into another. |
| Policy behavior | Explicit allow rules only; missing or malformed context denies with a stable non-secret reason. |
| External-client count | One approved external client for this phase; multi-client/tenant behavior is deferred. |
| Request authentication | HMAC-SHA256 over method, canonical path/query, timestamp, nonce, and SHA-256 body digest. |
| Request headers | `X-Atlas-Client-Id`, `X-Atlas-Key-Id`, `X-Atlas-Timestamp`, `X-Atlas-Nonce`, and lowercase-hex `X-Atlas-Signature`. |
| Replay protection | Five-minute timestamp window plus a PostgreSQL unique nonce record scoped to client/key identity. |
| Nonce retention | Retain accepted nonce records for ten minutes, then permit bounded cleanup; nonce values are random opaque identifiers. |
| Secret ownership | Current and next verification keys come from environment/provider secret storage; PostgreSQL stores metadata and key identifiers only. |
| Rotation | Current and next key identifiers may overlap during a bounded rotation window; retired keys fail closed. |
| Audit | Authentication and authorization outcomes record actor/client, channel, action/resource, result, reason code, and correlation ID without signatures or secrets. |

## 3. Approved Scope if Accepted

- Typed authorization context, decision, reason-code, and policy interfaces.
- Explicit initial policies for existing health/authentication probe boundaries
  only; no future business capability is implicitly allowed.
- HMAC request verification, canonicalization, constant-time comparison,
  timestamp validation, nonce persistence, and rotation-aware key selection.
- Migrations/models for external-client credential metadata and replay nonces as
  required; no secret material in database columns.
- Audit provenance for accepted and denied authentication/authorization checks.
- Tests for default deny, actor separation, malformed signatures, body changes,
  replay, clock skew, unknown/retired keys, rotation overlap, and redaction.

## 4. Explicitly Out of Scope

Approval decisions, operational knowledge writes, multi-client/RBAC behavior,
OAuth, API rate limiting, live credentials, frontend work, provider
provisioning, and permissions for unimplemented endpoints are excluded.

## 5. Verification and Completion

Required evidence includes PostgreSQL 18 migration validation, backend tests,
Ruff, mypy, frontend regression checks, secret scan, `git diff --check`, and
passing CI. Completion also requires an implementation report and merge through
the governed PR process.

## 6. Stop-and-Ask Triggers

Stop before storing verification keys in PostgreSQL, adding asymmetric PKI,
changing the single-client boundary, creating business permissions, or
weakening nonce/timestamp/signature validation.

## 7. Review Notes

Accepted as part of the consolidated Phase 3 planning package. Implement only
after WO-019 has merged.
