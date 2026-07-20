# WO-056 Google OAuth Production Client Preflight Report

**Work Order:** [WO-056](../work-orders/056-google-oauth-production-client-and-redirects.md)
**Status:** Preflight Complete - Callback Route Decision Required
**Date:** 2026-07-20
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Summary

WO-056 should not proceed directly to Google provider configuration yet. Source
inspection found that Atlas has governed connector OAuth start and completion
API contracts, but it does not currently expose a direct browser-facing Google
OAuth redirect handler at the earlier placeholder path
`/api/auth/google/callback`.

This preflight did not create or change a Google OAuth client, did not enter
client secrets, did not request authorization codes, and did not use production
mailbox data.

## Source Findings

Implemented backend connector OAuth routes:

| Purpose | Implemented route | Method | Notes |
| --- | --- | --- | --- |
| Start connector OAuth | `/api/v1/connectors/{connector_type}/oauth/start` | `POST` | Protected by the external-client HMAC boundary |
| Complete connector OAuth | `/api/v1/connectors/{connector_type}/oauth/callback` | `POST` | Protected by the external-client HMAC boundary; accepts callback payload data, not a direct Google browser redirect |

Additional findings:

- No `GET /api/auth/google/callback` route exists in `apps/api/src`.
- No frontend OAuth callback handler was found in `apps/web/src`.
- `ATLAS_API_GOOGLE_OAUTH_CLIENT_ID`,
  `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET`, and
  `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI` exist in configuration/readiness, but
  the current connector service still generates a fake/local Google
  authorization URL and does not consume those production values for a real
  provider exchange.
- The accepted scopes remain:
  - `https://www.googleapis.com/auth/gmail.modify`
  - `https://www.googleapis.com/auth/drive.file`
- The broad Gmail scope remains prohibited:
  - `https://mail.google.com/`

## Provider Setup Checklist, Not Yet Executed

After WO-056A confirms valid TLS for the final Grafley domains and WO-056
selects the callback implementation surface, configure Google OAuth with:

- Application/product identity: Atlas, a Grafley product.
- Administrative owner account: `atlas-owner@grafley.com`.
- Authorized JavaScript origin: `https://atlas.grafley.com`, if the selected
  browser flow requires a frontend origin.
- Authorized redirect URI: the source-confirmed browser-facing callback URL
  selected by WO-056 implementation. Do not use
  `https://api.atlas.grafley.com/api/auth/google/callback` unless that route is
  explicitly implemented and verified before provider setup.
- Scopes:
  - `https://www.googleapis.com/auth/gmail.modify`
  - `https://www.googleapis.com/auth/drive.file`
- Evidence capture:
  - record configured URI names, timestamps, provider pages, and redacted
    configured/not-configured state only;
  - never record client secrets, authorization codes, access tokens, refresh
    tokens, or mailbox content.

## Post-TLS Runtime Cutover Checklist

Keep this sequence gated behind valid TLS for both custom domains:

1. Verify `https://atlas.grafley.com` serves the Netlify-hosted dashboard over
   valid HTTPS.
2. Verify `https://api.atlas.grafley.com/health/live` returns the Atlas API
   health response over valid HTTPS.
3. Netlify production: set `NEXT_PUBLIC_API_BASE_URL` to
   `https://api.atlas.grafley.com` and redeploy the dashboard.
4. Render API: set `ATLAS_API_FRONTEND_ORIGIN` to
   `https://atlas.grafley.com` and restart or redeploy the API service.
5. Verify browser/API behavior from `https://atlas.grafley.com`.
6. Only then proceed to WO-056 callback implementation and Google provider
   configuration.

## Recommendation

Treat WO-056 as a small implementation-and-provider work order, not a
provider-configuration-only work order. The next engineering decision should
choose whether the production OAuth callback is:

1. a frontend callback route on `https://atlas.grafley.com` that exchanges the
   Google result through the existing signed connector completion API; or
2. a new API callback route on `https://api.atlas.grafley.com` that is designed
   explicitly for Google browser redirects and then hands off to the governed
   connector completion contract.

Option 1 preserves the existing external-client API boundary more cleanly for
the browser flow. Option 2 keeps callback ownership in the API but requires a
new unauthenticated browser redirect boundary with careful state validation,
redaction, and audit behavior.

No provider values should be entered until this choice is implemented or
explicitly accepted as already existing.
