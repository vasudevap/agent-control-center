# ADR-006 Browser-Mediated Google OAuth Callback Surface Review Record

**Status:** Accepted
**Decision Record:** `docs/decisions/ADR-006-browser-mediated-google-oauth-callback-surface.md`
**Review Owner:** Repository Maintainer
**Date Routed:** 2026-07-20
**Technical Review Date:** 2026-07-20
**Technical Review Prepared By:** Codex architecture and security review
**Decision Authority:** Repository Maintainer
**Accepted:** 2026-07-20
**Accepted By:** Repository Maintainer

## Review Objective

Determine whether WO-056 should use a server-side Atlas dashboard callback or a
new API browser callback as the production Google OAuth redirect surface.

## Scope Routed for Review

- Final Grafley product domains:
  - `https://atlas.grafley.com`
  - `https://api.atlas.grafley.com`
- Accepted single-owner administrative account:
  `atlas-owner@grafley.com`.
- Accepted Google OAuth scopes:
  - `https://www.googleapis.com/auth/gmail.modify`
  - `https://www.googleapis.com/auth/drive.file`
- Existing HMAC-protected connector API contracts:
  - `POST /api/v1/connectors/{connector_type}/oauth/start`
  - `POST /api/v1/connectors/{connector_type}/oauth/callback`
- Source finding that the earlier placeholder API callback route does not
  exist.

## Required Architecture Review

Architecture Review must confirm:

1. The selected redirect URI uses the accepted Grafley product domain.
2. The existing Atlas API connector boundary remains authoritative for
   connector state, provider token exchange, credential references, and audit.
3. The selected route does not require an unauthenticated browser-facing API
   callback under WO-056.
4. The dashboard callback can act as a thin adapter without becoming a second
   system of record.
5. Provider-generated URLs remain rollback and diagnostics references, not the
   preferred production OAuth surface.

## Architecture Review Findings

- **Product-domain alignment:** Pass. The accepted redirect URI is
  `https://atlas.grafley.com/oauth/google/callback`, which uses the final
  Atlas dashboard domain accepted under WO-056A.
- **API authority:** Pass. ADR-006 keeps state validation, exact scope
  enforcement, Google provider token exchange, account identity derivation,
  credential references, connector state, and audit evidence in the Atlas API.
- **Browser/API boundary:** Pass. The dashboard receives the Google browser
  redirect and completes the flow through an authenticated server-to-server API
  call. The existing HMAC-protected connector completion contract is not exposed
  directly to Google browser redirects.
- **Dashboard responsibility:** Pass. The dashboard callback is an adapter and
  user-return surface. It does not become authoritative for tokens, connector
  state, owner identity, or audit evidence.
- **Provider URL posture:** Pass. Netlify and Render provider URLs remain
  rollback and diagnostics surfaces only.

## Required Security Review

Security Review must confirm:

1. Browser JavaScript does not receive Google client secrets, Atlas HMAC
   secrets, access tokens, refresh tokens, or persisted credential material.
2. Authorization codes and provider error payloads are handled only as
   transient callback inputs and are not logged or rendered.
3. API implementation must validate `state`, PKCE, redirect URI, connector
   type, expiry, consumption status, and exact scopes before accepting a
   connection.
4. The production provider exchange must derive account identity and granted
   scopes from Google rather than trusting browser-supplied values.
5. Audit and review evidence must remain minimized and must not include secrets,
   tokens, authorization codes, or mailbox content.

## Security Review Findings

- **Browser secret exposure:** Pass for architecture acceptance. ADR-006
  explicitly prohibits browser JavaScript from signing Atlas API requests or
  receiving token material, Google client secrets, or Atlas HMAC secrets.
- **Transient callback data:** Pass. The accepted route may read callback query
  parameters server-side, but must not expose authorization codes, provider
  tokens, client secrets, HMAC secrets, or raw provider error details to browser
  JavaScript or logs.
- **Callback validation:** Pass. Implementation is required to validate state,
  PKCE, redirect URI, connector type, expiry, consumption status, and exact
  scopes fail-closed.
- **Provider-trusted account and scope evidence:** Pass. ADR-006 requires the
  API completion contract to evolve from fake-provider semantics so production
  account identity and granted scopes come from Google provider evidence rather
  than browser-supplied fields.
- **Evidence minimization:** Pass. Provider setup and execution evidence must be
  redacted and must not retain authorization codes, access tokens, refresh
  tokens, client secrets, HMAC secrets, or mailbox content.

## Alternatives Reviewed

- **API browser callback on `api.atlas.grafley.com`:** Rejected for WO-056
  because it would introduce a new unauthenticated browser-facing API route
  while an authenticated completion boundary already exists.
- **Browser JavaScript completes OAuth directly:** Rejected because it would
  expose signing or provider credential material to the browser.
- **Provider-generated URLs:** Rejected as the preferred OAuth surface after
  WO-056A accepted the final Grafley product domains.
- **Earlier placeholder API callback:** Rejected because source inspection found
  no matching route.

## Acceptance Decision

The Repository Maintainer accepted ADR-006 on 2026-07-20.

WO-056 may proceed with implementation using
`https://atlas.grafley.com/oauth/google/callback` as the production Google
OAuth redirect URI, subject to the Work Order's scope, validation, rollback,
and stop-and-ask triggers.

This review does not authorize exposing secrets, entering Google provider
values before the source route exists, broadening Google scopes, using
unauthorized accounts, scanning production mailbox data, or launching publicly.
