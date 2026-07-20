# Work Order 056: Google OAuth Production Client and Redirects

**Status:** Accepted - Pending Implementation
**Work Order ID:** WO-056
**Type:** Google OAuth cutover
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-19; pending hosted URL decisions
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** WO-056A final domain decision complete or explicitly deferred; WO-054 and WO-055 hosted URLs accepted
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
| Preferred redirect host | `https://api.atlas.grafley.com` after WO-056A custom-domain cutover |

## 3. Approved Scope if Accepted

- Configure OAuth redirect URIs for hosted API callback routes.
- Prefer the final Grafley API domain for redirect URIs:
  `https://api.atlas.grafley.com/api/auth/google/callback`, unless the
  implementation discovers a different canonical callback path in source.
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

## 6. Rollback Expectations

Rollback must revoke or rotate incorrect OAuth credentials, remove bad redirect
URIs, and preserve minimized evidence without token exposure.

## 7. Stop-and-Ask Triggers

Stop before broadening scopes, exposing client secrets, using unauthorized
accounts, scanning production mailbox data, finalizing OAuth against temporary
provider URLs while WO-056A remains pending, or proceeding if Google requires a
new verification/security decision.
