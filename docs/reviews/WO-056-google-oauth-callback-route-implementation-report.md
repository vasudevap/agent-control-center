# WO-056 Google OAuth Callback Route Implementation Report

**Work Order:** [WO-056](../work-orders/056-google-oauth-production-client-and-redirects.md)
**Status:** Google OAuth Provider Configured - Owner OIDC Gate Cleared
**Date:** 2026-07-20
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Architecture Decision:** [ADR-006](../decisions/ADR-006-browser-mediated-google-oauth-callback-surface.md)

## Summary

WO-056 now has the source-level callback surface accepted by ADR-006.

The hosted readiness response recorded below predates the completed WO-061
owner identity enrollment. WO-061 has since deployed the separate owner-OIDC
client lane, completed controlled owner authorization, manually bound the
immutable owner subject in Render without value exposure, and cleared the
owner identity readiness gate.

The dashboard exposes `GET /oauth/google/callback` and completes the callback
server-side through signed Atlas API HMAC headers. The API exposes
`POST /api/v1/connectors/oauth/google/callback` for authenticated
server-to-server completion and keeps connector state, state validation,
provider token exchange, account identity derivation, scope enforcement,
credential-reference creation, and audit evidence in the API boundary.

Google provider values have now been configured through Google Cloud and Render
provider-native storage. No OAuth client secret value, authorization code,
access token, refresh token value, production mailbox data, or full email
content was persisted in source, fixtures, logs, screenshots, or docs.

The Repository Maintainer confirmed on 2026-07-20 that
`atlas-owner@grafley.com` is not a Google account and authorized
`grafleyinc@gmail.com` as the single-owner Google OAuth account for the hosted
cutover.

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

## Provider Configuration Evidence - 2026-07-20

Google provider configuration is complete for the accepted redirect and scope
posture:

- Google Cloud project: `atlas-agent-control-center`
- Google account: `grafleyinc@gmail.com`
- OAuth app name: `Atlas Agent Control Center`
- Publishing status: Testing
- Test user: `grafleyinc@gmail.com`
- Accepted scopes:
  - `https://www.googleapis.com/auth/gmail.modify`
  - `https://www.googleapis.com/auth/drive.file`
- Enabled APIs:
  - Gmail API
  - Google Drive API
- OAuth web client name: `Atlas production web client`
- Authorized JavaScript origin: `https://atlas.grafley.com`
- Authorized redirect URI: `https://atlas.grafley.com/oauth/google/callback`
- Render service `atlas-agent-control-center-api` has:
  - `ATLAS_API_GOOGLE_OAUTH_CLIENT_ID`
  - `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET`
  - `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI`

Hosted readiness after the Render environment update:

```text
{"status":"not_ready","service":"atlas-api","checks":{"configuration":"failed"},"problems":["owner_identity_subject_missing"]}
```

## Remaining Owner Identity Gate

The source route exists and Google provider configuration is complete. The
remaining readiness gate is owner identity subject binding.

Completed provider setup sequence:

1. Merge and deploy this callback-route implementation to Netlify and Render.
2. Configure Netlify server-only `ATLAS_DASHBOARD_BASE_URL` to
   `https://atlas.grafley.com` so callback redirects remain on the accepted
   Grafley product domain when provider infrastructure presents an internal
   request origin. Completed on 2026-07-20 after PR #93 merged.
3. Configure Netlify server-only dashboard callback signing variables through
   provider-native environment storage, without `NEXT_PUBLIC_`. Completed on
   2026-07-20 with a rotated Render external-client key.
4. Configure Render Google OAuth values through provider-native environment
   storage. Completed on 2026-07-20.
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

Hosted follow-up verification after PR #93:

```text
netlify api getEnvVar --data '{"account_id":"652ed3c4f4e7dd56552d3e4c","site_id":"cc07a93e-8ffe-47e7-b328-e5ae4247b14d","key":"ATLAS_DASHBOARD_BASE_URL"}'
```

Result, with values redacted before output:

```text
ATLAS_DASHBOARD_BASE_URL is non-secret, available in all Netlify scopes, and
has a non-empty production value. Netlify also stores empty placeholder values
for dev, branch-deploy, deploy-preview, and dev-server contexts.
```

```text
netlify api createSiteBuild --data '{"site_id":"cc07a93e-8ffe-47e7-b328-e5ae4247b14d"}'
netlify api getSiteBuild --data '{"build_id":"6a5e9b7efb8cc864c21fa9f8"}'
```

Result:

```text
Build 6a5e9b7efb8cc864c21fa9f8 created deploy
6a5e9b7efb8cc864c21fa9fa and reached deploy_state=ready with error=null.
```

```text
curl -s -I -w "%{http_code}\n" \
  "https://atlas.grafley.com/oauth/google/callback?error=access_denied"
```

Result:

```text
HTTP/2 307
location: https://atlas.grafley.com/connectors?oauth=google&status=denied
307
```

```text
curl -s -o /dev/null -w "%{http_code}\n" \
  -X POST https://api.atlas.grafley.com/api/v1/connectors/oauth/google/callback
```

Result:

```text
401
```

At that point, production readiness remained fail-closed only for the then
pending owner and Google OAuth provider values:

```text
google_oauth_client_id_missing
google_oauth_client_secret_missing
google_oauth_redirect_uri_missing
owner_identity_subject_missing
```

Hosted dashboard HMAC binding follow-up:

```text
render deploys list srv-d9e2rprbc2fs73f4l23g --output json
```

Result, with environment values omitted:

```text
Render deploy dep-d9fa0r3rjlhs739t64vg reached status=live from
trigger=service_updated at commit c5ead8140bab8a6259a3826d19d50013343052a8.
```

```text
netlify api getEnvVars --data '{"account_id":"652ed3c4f4e7dd56552d3e4c","site_id":"cc07a93e-8ffe-47e7-b328-e5ae4247b14d"}'
```

Result, with values redacted before output:

```text
ATLAS_DASHBOARD_EXTERNAL_CLIENT_ID has a non-empty production value.
ATLAS_DASHBOARD_EXTERNAL_CLIENT_KEY_ID has a non-empty production value.
ATLAS_DASHBOARD_EXTERNAL_CLIENT_SECRET is marked secret and has a non-empty
production value.
```

```text
netlify api createSiteBuild --data '{"site_id":"cc07a93e-8ffe-47e7-b328-e5ae4247b14d"}'
netlify api getSiteBuild --data '{"build_id":"6a5ea0ffc589f8cbec2f4680"}'
```

Result:

```text
Build 6a5ea0ffc589f8cbec2f4680 created deploy
6a5ea0ffc589f8cbec2f4682 and reached deploy_state=ready with error=null.
```

```text
curl -s -I -w "%{http_code}\n" \
  "https://atlas.grafley.com/oauth/google/callback?state=[invalid-state]&code=[invalid-code]"
```

Result:

```text
HTTP/2 307
location: https://atlas.grafley.com/connectors?oauth=google&status=failed
307
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
- Dashboard callback signing values are bound through provider-native Netlify
  environment storage and matched to the rotated Render external-client key
  without committing or printing the HMAC secret.
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
| Google provider values are configured | Complete | Google Cloud project/client/scopes/test user and Render OAuth env values configured without value exposure |
| Owner identity subject is not configured | Pending | Requires immutable Google subject for `grafleyinc@gmail.com` before readiness can pass |
| Netlify canonical dashboard base URL is configured | Complete | PR #93 merged; Netlify production `ATLAS_DASHBOARD_BASE_URL` verified redacted; hosted callback denial redirects to `https://atlas.grafley.com/connectors?oauth=google&status=denied` |
| Netlify server-side callback signing values are configured | Complete | Provider-native Netlify `ATLAS_DASHBOARD_EXTERNAL_CLIENT_*` values are configured and matched to the rotated Render external-client key |
| Hosted end-to-end OAuth evidence is not captured | Pending | Capture under the provider configuration step with redacted evidence |
| Credential encryption service remains reference-only metadata | Existing limitation | Do not store raw token values outside the accepted credential boundary; future credential-vault hardening remains a separate security/infrastructure task |
