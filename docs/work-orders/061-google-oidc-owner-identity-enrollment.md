# Work Order 061: Google OIDC Owner Identity Enrollment

**Status:** In Progress - Provider Configuration Complete; Source Deployment, Owner Verification, and Subject Pending
**Work Order ID:** WO-061
**Type:** Identity and hosted configuration
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Architecture Decision:** Accepted [ADR-007 - Google OIDC Owner Identity Enrollment](../decisions/ADR-007-google-oidc-owner-identity-enrollment.md)
**Prerequisites:** ADR-007 accepted; WO-055 hosted API reachable; `grafleyinc@gmail.com` remains the authorized owner account
**Review Owner:** Repository Maintainer
**Review Record:** [WO-061 local source implementation report](../reviews/WO-061-google-oidc-owner-identity-enrollment-implementation-report.md)

**Implementation Authority:** Accepted by Repository Maintainer on 2026-07-20
for local source implementation only. Provider-action authority was granted on
2026-07-20. The dedicated Google OIDC client and required Render OIDC
configuration are now in place. Owner-subject entry, controlled login, hosted
verification, and production use remain pending.

## 1. Purpose

Obtain a Google-verified immutable subject for the authorized owner account and
enter it into Render as `ATLAS_API_OWNER_IDENTITY_SUBJECT`, without expanding
the Gmail/Drive connector scope posture or exposing provider credentials.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Owner account | `grafleyinc@gmail.com` only |
| Durable owner binding | Google OIDC `sub`, never email |
| OIDC client | Separate dedicated Google OAuth web client |
| OIDC scopes | `openid` and `email` only |
| OIDC redirect URI | `https://api.atlas.grafley.com/auth/owner/google/callback` |
| Connector isolation | Existing Gmail/Drive client, callbacks, and accepted scopes remain unchanged |
| Render mutation | Repository Maintainer enters the derived opaque subject manually; runtime code has no Render API authority |

## 3. Approved Scope if Accepted

- Implement the narrow API owner-OIDC start and callback routes defined by
  ADR-007, including state, nonce, PKCE, transaction-cookie handling, exact
  redirect validation, server-side code exchange, JWKS-backed ID-token
  validation, and redaction.
- Add the minimal typed configuration for the dedicated OIDC client, callback,
  bootstrap owner email, and transaction protection. Mark secrets with
  `SecretStr` or an equivalent redacted type.
- Add unit and integration tests for happy-path verified identity, incorrect
  audience/issuer/signature/nonce/state/PKCE/redirect/email, expired tokens,
  replay, error redaction, and transaction-cookie attributes.
- Configure the separate Google OIDC client and its exact redirect URI through
  Google Cloud after source routes are deployed and verified.
- Configure the dedicated provider-native Render OIDC values without exposing
  values in source, logs, screenshots, docs, or chat.
- Perform one controlled authorization with `grafleyinc@gmail.com`; retain
  only minimized confirmation evidence and no provider token material.
- Enter only the derived opaque subject in Render as
  `ATLAS_API_OWNER_IDENTITY_SUBJECT`, redeploy, and verify the readiness
  blocker is removed without printing the value.
- Update relevant architecture, work-order, plan, review, operational, and
  rollback records.

## 3A. Local Source Implementation Evidence

The accepted local source slice implemented:

- `GET /auth/owner/google/start` for the dedicated API-owned Google OIDC start
  route with exact `openid email` scopes, PKCE, nonce, state, no-store
  responses, and a secure host-only transaction cookie.
- `GET /auth/owner/google/callback` for the dedicated browser callback at the
  accepted API redirect path, with signed transaction validation, exact state
  binding, server-side code exchange, injectable JWKS-backed ID-token
  verification, bootstrap email enforcement, minimized success/failure output,
  and transaction-cookie deletion on completion.
- Separate typed OIDC configuration keys for the owner identity lane. These do
  not reuse or modify Gmail/Drive connector OAuth settings.
- Offline tests covering cookie attributes, redirect construction, minimized
  output, bad state, tampered transaction cookie, unexpected owner email,
  verifier denial, provider denial redaction, and fail-closed configuration.

This local implementation did not configure a Google OIDC client, change Render
secrets, perform a provider login, enter an owner subject, or verify hosted
readiness.

## 3B. Provider Configuration Evidence

On 2026-07-20, the Repository Maintainer granted the provider-action authority
required by this Work Order. A separate Google OAuth web client named `Atlas
owner identity OIDC` was created in the `atlas-agent-control-center` Google
Cloud project. Its only configured redirect URI is the accepted API callback
`https://api.atlas.grafley.com/auth/owner/google/callback`.

No client identifier, client secret, token, or subject value is recorded here.
The existing Gmail/Drive connector client remains unchanged. The dedicated
Google client credential and Render transaction secret were rotated during
configuration; superseded Google client credentials were revoked and deleted.

The verified Render target is project-scoped rather than visible from the
workspace homepage's ungrouped-resource list:

| Render boundary | Verified identity |
| --- | --- |
| Workspace | `My Workspace` (`tea-d8dqftek1jcs7399msjg`) |
| Project | `My project` (`prj-d8dqn1mk1jcs7399ubvg`) |
| Environment | `Production` (`evm-d8dqn1mk1jcs7399uc00`) |
| API service | `atlas-agent-control-center-api` (`srv-d9e2rprbc2fs73f4l23g`) |
| PostgreSQL database | `atlas-agent-control-center-db` (`dpg-d9e2rkbrjlhs73bkc6dg-a`) |

Navigate Render as **My project -> Production ->
atlas-agent-control-center-api -> Environment**. The workspace home may list
only ungrouped resources, such as `artifact-hub`, and is not evidence that the
Atlas resources are absent.

The five dedicated owner-OIDC Render values are configured without recording
their values: client ID, client secret, exact redirect URI, bootstrap email,
and transaction secret. The hosted readiness endpoint now reports only
`owner_identity_subject_missing`, confirming that owner-OIDC configuration is
no longer the configuration blocker. This verifies configuration parsing only:
the public owner-OIDC start route still returns `404` because the local WO-061
source slice has not yet been merged and deployed from `main`. No owner subject
has been entered and no controlled owner authorization has yet been performed.

## 4. Explicitly Out of Scope

Changing the existing Gmail/Drive connector OAuth client or scopes; requesting
`profile`, Gmail, Drive, or any additional identity/API scope; multi-user
authentication, RBAC, recovery, MFA, automatic Render mutation, production
mailbox scanning, token persistence, migration execution, release tagging, or
public launch.

## 5. Verification and Completion

Require `git diff --check`, focused secret and token scans, backend Ruff/mypy/
pytest, frontend checks only if the dashboard is touched, provider settings
evidence with values omitted, exact Google scope and redirect evidence, a
governed merge and Render deployment of the WO-061 source slice, controlled
owner verification evidence, Render readiness evidence without printing the
subject, and an implementation report under `docs/reviews/`.

## 6. Rollback Expectations

Rollback removes or disables the dedicated OIDC client and its Render secrets
if the flow is incorrect, clears an incorrectly entered owner subject, and
returns readiness to its deliberate fail-closed state. Connector OAuth clients,
credentials, and scopes are not modified by this Work Order.

## 7. Stop-and-Ask Triggers

Stop before changing the connector OAuth client or scopes; adding any scope
beyond `openid` and `email`; exposing a client secret, code, token, ID token,
or subject; using an account other than `grafleyinc@gmail.com`; automatically
writing Render configuration; weakening JWT/state/nonce/PKCE validation;
adding multi-user or recovery behavior; proceeding if Google requires a new
verification, consent, security, billing, or account decision; or starting
provider configuration before ADR-007 and this Work Order are accepted.
