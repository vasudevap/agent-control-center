# Work Order 056: Google OAuth Production Client and Redirects

**Status:** Accepted - Pending Implementation - Callback Route Decision Required
**Work Order ID:** WO-056
**Type:** Google OAuth cutover
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-19; pending hosted URL decisions
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** WO-056A final domain decision complete or explicitly deferred; WO-054 and WO-055 hosted URLs accepted
**Preflight Record:** [WO-056 Google OAuth Production Client Preflight Report](../reviews/WO-056-google-oauth-production-client-preflight-report.md)
**Review Record:** TBD

## 1. Purpose

Configure Google OAuth client settings and redirect URIs for the hosted Atlas
API while preserving the accepted Gmail and Drive scope posture.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Gmail scope | `https://www.googleapis.com/auth/gmail.modify` |
| Drive scope | `https://www.googleapis.com/auth/drive.file` |
| Broad Gmail scope | `https://mail.google.com/` remains prohibited |
| Account boundary | Authorized single-owner account only |
| Owner account | Dedicated Grafley owner account `atlas-owner@grafley.com` |
| Preferred redirect host | Final Grafley domain after WO-056A custom-domain cutover |
| Source-confirmed callback state | No direct Google redirect handler exists yet; the implemented connector completion route is a signed API `POST` endpoint |

## 3. Approved Scope if Accepted

- Configure OAuth redirect URIs for the hosted callback route selected during
  WO-056 implementation.
- Do not configure Google OAuth against the earlier placeholder
  `https://api.atlas.grafley.com/api/auth/google/callback`; source inspection
  found no matching route.
- Source inspection found the implemented connector completion route at
  `POST /api/v1/connectors/{connector_type}/oauth/callback`, which is protected
  by the external-client HMAC boundary and is not a direct Google browser
  redirect handler.
- Before provider setup, choose and implement or confirm the browser-facing
  OAuth callback surface. The preferred final host remains one of the accepted
  Grafley domains after WO-056A TLS verification, not a provider-generated URL
  unless WO-056A records an explicit deferment or rollback decision.
- Use provider-generated Render URLs for OAuth only if WO-056A records an
  explicit deferment or rollback decision.
- Verify OAuth start/callback behavior with accepted scopes.
- Confirm connector health, revoke, reconnect, and redaction behavior.
- Record minimized evidence without authorization codes, access tokens, refresh
  tokens, client secrets, or full email content.

## 4. Explicitly Out of Scope

Broader Google scopes, multi-user OAuth verification, production mailbox scans,
public Google verification for broad user populations, and production launch
announcement are excluded.

## 5. Verification and Completion

Require scope verification, hosted OAuth redirect evidence, connector health
evidence, redaction scans, revoke/reconnect notes, and an implementation report
under `docs/reviews/`.

Source-level preflight for WO-056:

- `apps/api/src/atlas_api/api/connectors.py` exposes
  `POST /api/v1/connectors/{connector_type}/oauth/start`.
- `apps/api/src/atlas_api/api/connectors.py` exposes
  `POST /api/v1/connectors/{connector_type}/oauth/callback`.
- `apps/api/src/atlas_api/services/connectors.py` currently generates a
  fake/local Google authorization URL and does not yet consume
  `ATLAS_API_GOOGLE_OAUTH_CLIENT_ID`,
  `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET`, or
  `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI` for a production provider exchange.
- No frontend OAuth callback route was found in `apps/web/src`.

Therefore, WO-056 must not be treated as provider configuration only; it also
needs the minimal production OAuth redirect/callback implementation decision
before Google provider values are entered.

## 6. Rollback Expectations

Rollback must revoke or rotate incorrect OAuth credentials, remove bad redirect
URIs, and preserve minimized evidence without token exposure.

## 7. Stop-and-Ask Triggers

Stop before broadening scopes, exposing client secrets, using unauthorized
accounts, scanning production mailbox data, finalizing OAuth against temporary
provider URLs while WO-056A remains pending, configuring a redirect URI that
does not exist in source, bypassing the external-client boundary without an
accepted design decision, or proceeding if Google requires a new
verification/security decision.
