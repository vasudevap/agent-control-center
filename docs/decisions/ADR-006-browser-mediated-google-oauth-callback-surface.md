# ADR-006 - Browser-Mediated Google OAuth Callback Surface

**Status:** Proposed
**Date:** 2026-07-20
**Decision Owners:** Architecture and Security Review
**Review Owner:** Repository Maintainer
**Review State:** Pending
**Scope:** Google OAuth redirect handling for the hosted Atlas dashboard and API
**Related Decisions:** `ADR-004 - Governed External Product Client Contract`
**Related Work Orders:** `WO-036 - Gmail OAuth, Scopes, and Connector Boundary`, `WO-056 - Google OAuth Production Client and Redirects`, and `WO-056A - Grafley Custom Domain Cutover`

---

## Context

WO-036 established the governed connector OAuth boundary and accepted the MVP
Google scopes:

- `https://www.googleapis.com/auth/gmail.modify`
- `https://www.googleapis.com/auth/drive.file`

The broad Gmail scope `https://mail.google.com/` remains prohibited.

WO-056A completed the final Grafley product-domain decision for the hosted MVP:

- Dashboard: `https://atlas.grafley.com`
- API: `https://api.atlas.grafley.com`

WO-056 preflight found no implemented browser-facing Google OAuth redirect
handler at the earlier placeholder
`https://api.atlas.grafley.com/api/auth/google/callback`. The implemented
connector routes are:

- `POST /api/v1/connectors/{connector_type}/oauth/start`
- `POST /api/v1/connectors/{connector_type}/oauth/callback`

Both routes are protected by the external-client HMAC boundary. They are API
contracts, not direct Google browser redirect handlers. A Google OAuth redirect
cannot call those routes as currently designed because Google redirects the
user's browser with query parameters and no Atlas HMAC signature.

The hosted dashboard is a first-party Atlas control surface deployed on Netlify
with Next.js route-handler capability. That makes a server-side dashboard
callback possible without exposing external-client HMAC material to browser
JavaScript.

## Decision

Atlas will use a browser-mediated, server-side dashboard callback as the
production Google OAuth redirect surface.

The canonical Google OAuth redirect URI for WO-056 will be:

`https://atlas.grafley.com/oauth/google/callback`

Google redirects the owner's browser to this dashboard route after consent. The
dashboard callback route must execute server-side. It may read the transient
OAuth query parameters required to complete the flow, but it must not expose
authorization codes, access tokens, refresh tokens, client secrets, HMAC
secrets, or provider error details to browser JavaScript.

The Atlas API remains responsible for validating state, enforcing exact scopes,
exchanging the authorization code with Google, deriving the connected account
identity, storing credential references, updating connector state, and writing
audit evidence.

The dashboard callback route is an adapter between the browser redirect and the
governed API contract. It must complete the connection through an authenticated
server-to-server call to the Atlas API using the accepted first-party or
external-client authentication boundary. Browser JavaScript must not sign Atlas
API requests and must not receive OAuth token material.

The final Google provider setup for WO-056 must use:

- OAuth app/product identity: Atlas, a Grafley product.
- Administrative owner account: `atlas-owner@grafley.com`.
- Authorized JavaScript origin: `https://atlas.grafley.com`, if required by
  the selected Google OAuth client type.
- Authorized redirect URI:
  `https://atlas.grafley.com/oauth/google/callback`.
- Accepted scopes only: `gmail.modify` and `drive.file`.

## Required Implementation Properties

The WO-056 implementation must:

- Implement the source route before entering Google provider redirect values.
- Validate `state` against the API-owned stored OAuth state before accepting a
  callback.
- Preserve PKCE for Google authorization-code exchange.
- Require exact redirect URI matching between the stored OAuth state, the
  Google authorization URL, and the provider token exchange.
- Reject missing, expired, already consumed, or connector-mismatched state.
- Reject granted scopes that differ from the accepted connector scope set.
- Keep Google client secrets and refresh tokens only in provider-native
  server-side configuration or the accepted credential boundary.
- Emit minimized audit evidence for start, callback success, callback denial,
  provider exchange failure, revocation, and reconnect attempts.
- Avoid logging authorization codes, provider tokens, client secrets, HMAC
  secrets, raw Google error payloads, full email content, or mailbox data.
- Render only a minimized success or failure result to the browser and then
  return the owner to the connectors surface.

## Consequences

### Positive

- The public Google redirect URI uses the final Atlas product domain.
- The API does not need to expose the existing HMAC-protected completion route
  directly as an unauthenticated browser endpoint.
- The dashboard can provide a product-owned owner experience after consent.
- Token exchange, credential storage, connector state, and audit remain API
  responsibilities.
- Netlify and Render provider URLs remain rollback and diagnostics surfaces, not
  preferred OAuth surfaces.

### Trade-offs

- The dashboard server route becomes part of the OAuth trust boundary.
- The dashboard hosting environment needs any server-side credentials required
  to authenticate its completion call to the API.
- The authorization code still transits the browser redirect URL as part of the
  OAuth authorization-code flow, so callback handling and logging must be
  deliberately minimized.
- The API completion contract must evolve from the fake-provider test contract
  to a production provider-exchange contract that can derive granted scopes and
  account identity from Google rather than trusting browser-supplied values.

### Risks

- Accidentally implementing the callback as a client component could expose the
  authorization code or signing material.
- Reusing the existing callback contract without changing provider exchange
  semantics could trust browser-supplied account identifiers or scopes.
- Adding the API callback as a public unauthenticated route later could bypass
  the intended adapter boundary.
- Provider or platform logs could capture query parameters if callback logging
  is not minimized.

## Alternatives Considered

### API browser callback on `api.atlas.grafley.com`

Rejected for WO-056 because it would introduce a new unauthenticated
browser-facing API route for Google redirects while an authenticated API
completion boundary already exists. This can be reconsidered by a later ADR if
Atlas needs API-owned redirects for multi-client, non-dashboard, mobile, or
provider-specific requirements.

### Browser JavaScript completes OAuth directly

Rejected because browser JavaScript must not hold Atlas HMAC secrets, Google
client secrets, refresh tokens, or provider token material.

### Keep using provider-generated URLs

Rejected as the preferred production path because WO-056A accepted
`atlas.grafley.com` and `api.atlas.grafley.com` as the final Grafley product
domains. Provider-generated URLs remain rollback and diagnostics references.

### Configure the earlier placeholder API callback

Rejected because source inspection found no matching route, and configuring a
Google redirect URI that does not exist in source is an explicit WO-056
stop-and-ask trigger.

## Deferred Detailed Design

WO-056 implementation must define the exact API completion payload and tests.
That work may either evolve the existing
`POST /api/v1/connectors/{connector_type}/oauth/callback` contract for
server-side provider exchange or introduce a narrowly scoped authenticated
completion route. In either case, the implementation must preserve the
contract's authentication, authorization, state validation, scope enforcement,
credential-boundary, and audit expectations.

## Governance and Acceptance

This ADR is Proposed and has no implementation authority until accepted by the
Repository Maintainer.

After acceptance, implementation still requires WO-056 execution evidence,
including source-level callback route verification, Google provider setup
evidence with values redacted where required, exact scope verification,
connector health evidence, revoke/reconnect notes, and secret/token redaction
scans.
