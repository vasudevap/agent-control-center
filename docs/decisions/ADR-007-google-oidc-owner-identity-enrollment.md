# ADR-007 - Google OIDC Owner Identity Enrollment

**Status:** Accepted
**Date:** 2026-07-20
**Decision Owners:** Architecture and Security Review
**Review Owner:** Repository Maintainer
**Review State:** Architecture and Security Review Complete
**Accepted:** 2026-07-20
**Accepted By:** Repository Maintainer
**Scope:** Single-owner Google identity verification and initial immutable subject enrollment
**Related Decisions:** `ADR-006 - Browser-Mediated Google OAuth Callback Surface`
**Related Work Orders:** `WO-019 - Owner Authentication and Session Foundation`, `WO-053 - Production Environment and Secrets Provisioning`, `WO-055 - Render API and PostgreSQL Deployment`, and proposed `WO-061 - Google OIDC Owner Identity Enrollment`

---

## Context

Atlas production readiness requires
`ATLAS_API_OWNER_IDENTITY_SUBJECT`, but WO-019 deliberately implemented only a
provider-neutral verifier boundary. It correctly prohibits substituting an
email address for an immutable identity subject.

The existing Google connector OAuth client and callback flow are limited to
`gmail.modify` and `drive.file`. That flow derives connector account identity;
it does not request an OpenID Connect ID token, validate a Google identity, or
provide the owner subject required by the owner-session boundary. Adding
identity scopes or a browser callback to that connector lane without an
explicit decision would violate WO-053 and WO-056 stop-and-ask triggers.

The authorized single-owner Google account is `grafleyinc@gmail.com`.

## Decision

Atlas will establish a separate Google OIDC owner-identity lane. It is not a
connector authorization lane and must not alter the existing Gmail/Drive
connector client, accepted connector scopes, connector callback route, or
credential records.

The owner-identity lane will use a dedicated Google OAuth web client with only
the standard identity scopes `openid` and `email`. It will not request
`profile`, Gmail, Drive, or any other Google API scope. Its sole accepted
redirect URI will be the dedicated API callback:

`https://api.atlas.grafley.com/auth/owner/google/callback`

The API owns a short-lived authorization-code transaction. It will issue a
secure, host-only, `HttpOnly`, `Secure`, `SameSite=Lax` transaction cookie,
bind and validate `state`, `nonce`, PKCE, and the exact redirect URI, and
delete the cookie after completion. The API will exchange the code server-side
and accept the identity only after validating the ID token signature against
Google's published keys, issuer, audience, expiry, issued-at time, nonce, and
`email_verified` claim.

During initial enrollment, the verified email must exactly match the configured
bootstrap owner account `grafleyinc@gmail.com`; that email check is an
enrollment safeguard only, never the durable owner identity. The ID token's
opaque `sub` becomes the sole value entered into
`ATLAS_API_OWNER_IDENTITY_SUBJECT` in Render. The subject must not appear in
logs, errors, screenshots, documentation, source control, or chat.

The enrollment callback may display only a minimized, one-time owner-facing
confirmation sufficient for the Repository Maintainer to enter the opaque
subject into Render. It must not display or retain authorization codes, access
tokens, refresh tokens, client secrets, ID tokens, or raw provider responses.

ADR-006 continues to govern Gmail/Drive connector OAuth. Its browser callback
and the new owner callback are distinct trust boundaries with distinct clients,
scopes, state, and completion behavior.

## Required Implementation Properties

- Use a separate set of provider-native Render secrets for the OIDC client and
  transaction-cookie encryption/signing material; do not reuse connector
  client secrets or opaque session identifiers as cryptographic keys.
- Do not add an unauthenticated generic identity endpoint. The browser-facing
  start and callback routes are limited to the one owner-enrollment/login
  protocol and reject unexpected methods, parameters, issuer, audience,
  redirect URI, state, nonce, PKCE, or token claims.
- Treat Google tokens and all callback query values as secret material for
  logging and error handling. Redact them from audit events, provider logs,
  HTTP errors, browser pages, and test fixtures.
- Do not auto-write Render environment variables, database users, connector
  credentials, or sessions during initial enrollment. The Repository
  Maintainer performs the one-time Render subject entry after examining the
  minimized success surface.
- After Render binding, verify readiness reports no
  `owner_identity_subject_missing` problem. The value itself remains secret.
- Maintain the existing single-owner and fail-closed session contract. Multi-
  user accounts, RBAC, account recovery, and production mailbox actions remain
  out of scope.

## Consequences

### Positive

- The durable owner binding is a Google-verified immutable subject rather than
  a mutable email address.
- Connector consent remains constrained to the accepted Gmail and Drive scope
  posture.
- The OAuth redirect and token exchange have an explicit API-owned trust
  boundary with state, nonce, PKCE, and ID-token verification.

### Trade-offs

- Atlas gains a second, deliberately isolated Google OAuth client and callback
  surface.
- The hosted API needs narrowly scoped OIDC configuration and transient
  transaction-cookie secret material.
- The one-time bootstrap still requires a Repository Maintainer action in
  Render because application code must not mutate hosted environment settings.

## Alternatives Considered

### Set the owner subject to `grafleyinc@gmail.com`

Rejected. WO-019 expressly requires immutable subject equality and prohibits
email as a substitute.

### Reuse the Gmail/Drive connector OAuth client and scopes

Rejected. It would blur identity verification with connector authorization,
expand an accepted connector scope posture, and make the owner binding depend
on an unrelated integration flow.

### Obtain the subject from an unverified browser token or manual account page

Rejected. It would not establish the ID-token validation evidence needed for a
security boundary and risks copying tokens or account data into operator
records.

### Automatically update Render from the callback

Rejected. It would grant runtime code infrastructure mutation authority and
would make the enrollment path an implicit deployment control plane.

## Governance and Acceptance

This ADR is Accepted. On 2026-07-20, the Repository Maintainer accepted ADR-007
and WO-061, authorizing local source implementation only. Google client
configuration, Render secret changes, subject entry, provider login, hosted
verification, and production use remain governed by WO-061 stop-and-ask
triggers and require explicit provider-action authority.
