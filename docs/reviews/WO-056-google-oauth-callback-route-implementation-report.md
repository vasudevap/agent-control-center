# WO-056 Google OAuth Callback Route Implementation Report

**Work Order:** [WO-056](../work-orders/056-google-oauth-production-client-and-redirects.md)
**Status:** Callback Route Implemented - Provider Configuration Pending
**Date:** 2026-07-20
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Architecture Decision:** [ADR-006](../decisions/ADR-006-browser-mediated-google-oauth-callback-surface.md)

## Summary

WO-056 now has the source-level callback surface accepted by ADR-006.

The dashboard exposes `GET /oauth/google/callback` and completes the callback
server-side through signed Atlas API HMAC headers. The API exposes
`POST /api/v1/connectors/oauth/google/callback` for authenticated
server-to-server completion and keeps connector state, state validation,
provider token exchange, account identity derivation, scope enforcement,
credential-reference creation, and audit evidence in the API boundary.

No Google provider values were configured, no OAuth client secret was entered,
no authorization code was requested from Google, no access token or refresh
token value was persisted in source, fixtures, logs, screenshots, or docs, and
no production mailbox data was used.

## Scope Implemented

- Dashboard server route:
  - `apps/web/src/app/oauth/google/callback/route.ts`
  - accepts Google browser redirects;
  - handles provider-denied, missing-parameter, success, and failure paths;
  - redirects back to `/connectors` with minimized status only.
- Dashboard signing helper:
  - `apps/web/src/lib/atlas-api-signing.ts`
  - signs server-to-server JSON requests using the existing Atlas HMAC
    canonical request format.
- API callback route:
  - `POST /api/v1/connectors/oauth/google/callback`
  - protected by `ExternalClientHmac`;
  - resolves connector type from stored OAuth state rather than trusting the
    browser callback to identify the connector.
- Google authorization URL behavior:
  - uses configured `ATLAS_API_GOOGLE_OAUTH_CLIENT_ID`,
    `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET`, and
    `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI` when present;
  - preserves the fake-provider authorization URL path when Google OAuth values
    are absent for local and CI tests.
- Google provider completion behavior:
  - exchanges authorization code server-side;
  - validates exact granted scopes;
  - derives Gmail account identity from the Gmail profile endpoint;
  - derives Drive account identity from the Drive About endpoint;
  - creates only credential-reference metadata and never returns token values.
- Environment documentation:
  - records Netlify server-only dashboard base URL variable:
    `ATLAS_DASHBOARD_BASE_URL`;
  - records Netlify server-only dashboard callback signing variables:
    `ATLAS_DASHBOARD_EXTERNAL_CLIENT_ID`,
    `ATLAS_DASHBOARD_EXTERNAL_CLIENT_KEY_ID`, and
    `ATLAS_DASHBOARD_EXTERNAL_CLIENT_SECRET`.

## Remaining Provider Configuration Gate

The source route exists, but provider configuration remains pending.

Before entering Google provider values:

1. Merge and deploy this callback-route implementation to Netlify and Render.
2. Configure Netlify server-only `ATLAS_DASHBOARD_BASE_URL` to
   `https://atlas.grafley.com` so callback redirects remain on the accepted
   Grafley product domain when provider infrastructure presents an internal
   request origin.
3. Configure Netlify server-only dashboard callback signing variables through
   provider-native environment storage, without `NEXT_PUBLIC_`.
4. Configure Render Google OAuth values through provider-native environment
   storage.
5. Verify the deployed callback route and signed API completion path.
6. Configure Google OAuth with redirect URI
   `https://atlas.grafley.com/oauth/google/callback`.

## Validation Commands

Focused backend connector validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_connectors.py
```

Result:

```text
6 passed, 1 warning
```

Backend lint:

```text
cd apps/api
./.venv/bin/python -m ruff check .
```

Result:

```text
All checks passed!
```

Backend type check:

```text
cd apps/api
./.venv/bin/python -m mypy src
```

Result:

```text
Success: no issues found in 61 source files
```

Focused frontend validation:

```text
cd apps/web
npm test -- --run src/lib/atlas-api-signing.test.ts src/app/oauth/google/callback/route.test.ts
```

Result:

```text
2 passed, 5 tests passed
```

Follow-up canonical redirect validation:

```text
cd apps/web
npm test -- --run src/app/oauth/google/callback/route.test.ts
```

Result:

```text
1 passed, 4 tests passed
```

Frontend type check:

```text
cd apps/web
npm run typecheck
```

Result:

```text
Passed
```

Frontend lint:

```text
cd apps/web
npm run lint
```

Result:

```text
Passed
```

Whitespace validation:

```text
git diff --check
```

Result:

```text
Passed
```

## Security and Privacy Evidence

- Browser redirects never include authorization code, state, provider error
  detail, token, or secret values after callback handling.
- Browser redirects use the server-side dashboard base URL when configured,
  keeping owner navigation on the accepted Grafley product domain.
- Browser JavaScript does not sign Atlas API requests.
- Dashboard callback signing values use server-only environment variables and
  are not prefixed with `NEXT_PUBLIC_`.
- API callback route remains protected by the existing external-client HMAC
  boundary.
- API resolves connector type from stored state instead of trusting callback
  query values.
- API validates state, expiry, consumed status, redirect URI, account
  identifier, and exact scopes before creating a connection.
- Provider exchange errors are returned as minimized Atlas error codes.
- Provider token values are not returned in API responses or committed
  artifacts.

## Residual Risks and Follow-Up

| Item | Status | Next action |
| --- | --- | --- |
| Google provider values are not configured | Pending | Configure after source route deployment and explicit provider-action step |
| Netlify canonical dashboard base URL is not configured | Pending | Configure `ATLAS_DASHBOARD_BASE_URL=https://atlas.grafley.com` in provider-native Netlify environment variables |
| Netlify server-side callback signing values are not configured | Pending | Configure provider-native Netlify variables without `NEXT_PUBLIC_` |
| Hosted end-to-end OAuth evidence is not captured | Pending | Capture under the provider configuration step with redacted evidence |
| Credential encryption service remains reference-only metadata | Existing limitation | Do not store raw token values outside the accepted credential boundary; future credential-vault hardening remains a separate security/infrastructure task |
