# Work Order 019: Owner Authentication and Session Foundation

**Status:** Proposed - Review Required
**Work Order ID:** WO-019
**Type:** Backend identity foundation
**Implementation Authorization:** Not Granted
**Accepted:** Not Accepted
**Accepted By:** Not Accepted
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Architecture Authority:** [Phase 3 Target Architecture](../implementation-plans/phase-3-platform-foundation-target-architecture.md), [Security Architecture](../architecture/07-security-architecture.md), [Data Architecture](../architecture/08-data-architecture.md)
**Decision Authority:** [ADR-003](../decisions/ADR-003-governed-external-approval-decision-channel.md), [ADR-004](../decisions/ADR-004-governed-external-product-client-contract.md)
**Prerequisite Work Order:** [WO-018 PostgreSQL Environment and Migration Hardening](./018-postgresql-environment-and-migration-hardening.md)
**Review Owner:** Repository Maintainer

---

## 1. Purpose

Establish the backend-only, single-owner authentication and session foundation
before authorization policy or operational APIs are implemented.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Human identity scope | Exactly one configured owner identity; no multi-user, role, or tenant model. |
| Provider scope | Provider-neutral verified-identity interface only. Google OAuth/OIDC client flow, redirects, provider credentials, and callback integration are deferred. |
| Session storage | Server-side PostgreSQL session record with opaque random identifier; only a hash of the identifier is persisted. |
| Cookie | Opaque identifier in an `HttpOnly`, `Secure`, `SameSite=Strict`, path-scoped session cookie. No identity claims or secrets in the cookie. |
| Revocation | Logout revokes the server-side session; expired or revoked records fail closed. |
| Owner binding | Verified identity subject must equal the configured owner subject; email is not a substitute for immutable subject identity. |
| Test path | An injected fake identity verifier is allowed in unit tests only. No header, query, environment, or public-route authentication bypass. |
| Database | PostgreSQL-only session persistence and migration validation follow WO-018. |

## 3. Approved Scope if Accepted

- Add typed settings for owner subject, session signing/validation secret, cookie
  policy, and session lifetime; redact all secret values.
- Add a provider-neutral `VerifiedIdentity` model and verifier protocol. A real
  provider implementation is explicitly not part of this Work Order.
- Add a backward-compatible migration and model for owner session records:
  subject/user reference, session-id hash, issued/expiry/revocation timestamps,
  and minimal audit-safe metadata.
- Add internal auth/session services that issue, validate, revoke, and expire
  sessions without logging identifiers or secrets.
- Add narrow backend endpoints or dependency boundaries for session creation,
  current-session verification, and logout only if they fail closed without a
  configured verifier.
- Add unit/integration tests for owner mismatch, missing/expired/revoked
  session, cookie flags, logout invalidation, and secret redaction.
- Update CI, local commands, README, work-order/backlog records, and an
  implementation report as needed.

## 4. Explicitly Out of Scope

- Google OAuth/OIDC, browser redirects, provider SDKs, client IDs/secrets,
  callback URLs, frontend login UI, or frontend integration;
- multi-user accounts, RBAC, permissions, external-client authorization,
  approval re-authentication, password authentication, MFA, recovery, or SSO;
- live provider/database provisioning, real secrets, or deployment changes;
- queue, scheduler, webhook, API-contract, observability, Phase 5, or Phase 6
  behavior.

## 5. Required File Scope

The implementing agent may modify backend settings, auth/session/database
modules, Alembic migrations, backend tests, CI, README files, and relevant
implementation-plan/work-order/review records. Frontend source and provider
configuration files are excluded.

## 6. Security Requirements

- Authentication and session validation deny by default.
- Missing owner/session configuration disables session issuance safely.
- Cookie/session identifiers, secrets, identity claims beyond required subject,
  database URLs, and provider tokens never appear in logs, errors, tests, or
  documentation.
- Session fixation is prevented by generating a new cryptographically random
  identifier at issuance; stored values are hashed.
- State-changing future APIs must be able to depend on the same verified owner
  session boundary.

## 7. Verification Plan

Required evidence: `git diff --check`, strict secret scan, PostgreSQL 18
migration upgrade/downgrade in CI, backend pytest/Ruff/mypy, frontend
typecheck/lint/test/build, and passing GitHub CI. The implementation report
must record scope, cookie policy, session lifecycle, residual risks, and the
next recommendation.

## 8. Acceptance Criteria

Completion requires maintainer acceptance before implementation, a tested
provider-neutral owner/session boundary, revocable PostgreSQL-backed sessions,
no provider-specific or frontend scope, required validation passing, and a
merged pull request.

## 9. Stop-and-Ask Triggers

Stop before adding provider OAuth behavior, an identity SDK, a new secrets
manager, a different session storage mechanism, multi-user/RBAC behavior, a
live credential, a frontend route, or any change to the accepted single-owner
identity boundary. These require separate authority or an ADR where applicable.

## 10. Review Notes

This proposal does not authorize implementation until accepted by the
repository maintainer.
