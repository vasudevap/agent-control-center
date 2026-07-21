# WO-061 Google OIDC Owner Identity Enrollment - Local Source Implementation Report

**Status:** Provider configuration complete; owner verification and subject pending
**Date:** 2026-07-20
**Work Order:** [WO-061](../work-orders/061-google-oidc-owner-identity-enrollment.md)
**ADR:** [ADR-007](../decisions/ADR-007-google-oidc-owner-identity-enrollment.md)
**Scope Authorized:** Local source implementation; provider-action authority
granted on 2026-07-20

## Summary

The local source slice for WO-061 implemented a dedicated Google OIDC
owner-identity enrollment boundary, isolated from the Gmail/Drive connector
OAuth lane. The implementation adds browser-facing API routes for owner OIDC
start and callback, dedicated configuration keys, signed transaction-cookie
handling, PKCE/state/nonce support, server-side token exchange, injectable
JWKS-backed ID-token verification, bootstrap email enforcement, minimized
browser output, and offline tests.

The source implementation itself made no provider changes. The subsequent
provider progress is recorded below. No owner subject was changed, no
controlled owner login was performed, and hosted readiness remains deliberately
blocked only on that missing immutable subject.

## Provider Progress

After explicit provider-action authority was granted on 2026-07-20, a separate
Google OAuth web client named `Atlas owner identity OIDC` was created in the
`atlas-agent-control-center` project. It is configured with the sole accepted
redirect URI `https://api.atlas.grafley.com/auth/owner/google/callback`.

No provider credential, token, or immutable subject is recorded in this
report. The existing Gmail/Drive connector OAuth client was not modified.

The initial Render discovery issue was navigational, not an account or service
loss: the workspace homepage lists only ungrouped resources. Atlas is in
`My project` / `Production`, with project ID `prj-d8dqn1mk1jcs7399ubvg`,
environment ID `evm-d8dqn1mk1jcs7399uc00`, API service ID
`srv-d9e2rprbc2fs73f4l23g`, and database ID
`dpg-d9e2rkbrjlhs73bkc6dg-a`. The canonical path is **My project -> Production
-> atlas-agent-control-center-api -> Environment**.

The five dedicated Render owner-OIDC values are configured and the service was
rebuilt without exposing their values. During setup, the dedicated Google
client credential and Render transaction secret were rotated; superseded Google
credentials were revoked and deleted. The hosted readiness endpoint returned
the expected configuration-only blocker, `owner_identity_subject_missing`,
rather than an owner-OIDC configuration error. The public
`/auth/owner/google/start` route returns `404`, correctly showing that Render
is still deploying `main` before this unmerged local source slice.

## Source Changes

- Added `atlas_api.services.owner_identity` for owner-OIDC protocol handling,
  transaction-cookie serialization, Google token exchange, ID-token
  verification boundary, and bootstrap owner-claim validation.
- Added `atlas_api.api.owner_identity` with:
  - `GET /auth/owner/google/start`
  - `GET /auth/owner/google/callback`
- Registered the owner-identity router in the FastAPI app.
- Added dedicated owner-OIDC settings:
  - `ATLAS_API_OWNER_OIDC_CLIENT_ID`
  - `ATLAS_API_OWNER_OIDC_CLIENT_SECRET`
  - `ATLAS_API_OWNER_OIDC_REDIRECT_URI`
  - `ATLAS_API_OWNER_OIDC_BOOTSTRAP_EMAIL`
  - `ATLAS_API_OWNER_OIDC_TRANSACTION_SECRET`
- Added `PyJWT[crypto]` as the declared production dependency for
  JWKS-backed RSA ID-token verification.

## Security Evidence

- Owner OIDC uses only `openid email`.
- The owner-OIDC client and settings are separate from the Gmail/Drive
  connector OAuth settings.
- Transaction cookies are `HttpOnly`, `Secure`, host-only, `SameSite=Lax`, and
  use the `__Host-` prefix with `Path=/`.
- Callback validation binds state, transaction signature, exact redirect URI,
  PKCE verifier, ID-token nonce, configured audience, issuer, expiry, issued-at
  time, verified email, and exact bootstrap email.
- Browser output is minimized and does not include authorization codes,
  provider tokens, client secrets, ID tokens, raw provider errors, or provider
  payloads.

## Validation

Commands run from the repository root:

```text
apps/api/.venv/bin/python -m ruff check apps/api/src apps/api/tests
apps/api/.venv/bin/python -m mypy apps/api/src
apps/api/.venv/bin/python -m pytest apps/api/tests
```

Results:

- Ruff: passed
- mypy: passed
- pytest: 150 passed, 1 existing Starlette/httpx deprecation warning

Focused owner-identity tests cover start redirect construction, secure cookie
attributes, minimized success output, bad state rejection, tampered transaction
cookie rejection, unexpected email rejection, verifier denial redaction,
provider denial redaction, and fail-closed configuration.

## Remaining Work

- Refresh the API dependency environment with the new `PyJWT[crypto]`
  dependency before hosted deployment.
- Merge the reviewed WO-061 source slice through the governed pull-request
  process and allow Render to deploy that `main` revision.
- Perform one controlled authorization with `grafleyinc@gmail.com`.
- Enter only the derived opaque subject in Render as
  `ATLAS_API_OWNER_IDENTITY_SUBJECT`.
- Redeploy after manual subject entry and verify readiness no longer reports
  `owner_identity_subject_missing`, without printing the subject value.

## Rollback

Rollback removes the dedicated Render owner-OIDC values, clears an incorrectly
entered owner subject, and disables or deletes the dedicated Google client if
the flow is incorrect. The Gmail/Drive connector client remains untouched.
