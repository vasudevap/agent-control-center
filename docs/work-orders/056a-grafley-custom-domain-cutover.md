# Work Order 056A: Grafley Custom Domain Cutover

**Status:** In Progress - DNS Propagation and Certificates Pending
**Work Order ID:** WO-056A
**Type:** Custom domain and DNS cutover
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-20 after accepting the Grafley-hosted URL recommendation
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing Plan:** [Hosted Production Cutover Work Order Backlog](../implementation-plans/hosted-production-cutover-work-order-backlog.md)
**Prerequisites:** WO-054 hosted Netlify target exists; WO-055 hosted Render API target exists; provider custom-domain target values are available
**Review Record:** [WO-056A Implementation Report](../reviews/WO-056A-grafley-custom-domain-cutover-implementation-report.md)

## 1. Purpose

Cut over the hosted Atlas MVP from provider-generated hostnames to accepted
Grafley product domains before Google OAuth is finalized, so the production
owner consent flow, browser runtime, and API CORS posture use stable public
URLs.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Product ownership | Atlas is a Grafley product |
| Owner account | `atlas-owner@grafley.com` is the dedicated Atlas owner account |
| Frontend domain | `https://atlas.grafley.com` |
| API domain | `https://api.atlas.grafley.com` |
| DNS authority | Repository Maintainer provisions Grafley DNS records after provider target values are known |
| Temporary provider URLs | May remain as deployment/rollback evidence, but should not be the preferred public OAuth/browser surface once custom domains are active |

## 3. Approved Scope if Accepted

- Configure the Netlify custom domain target for `atlas.grafley.com` and
  capture the required CNAME or provider DNS target value without exposing
  unrelated provider account details.
- Configure the Render custom domain target for `api.atlas.grafley.com` and
  capture the required CNAME or provider DNS target value without exposing
  unrelated provider account details.
- Hand off the exact DNS records required for Grafley domain provisioning.
- After the Repository Maintainer provisions DNS records, verify DNS
  propagation, provider TLS issuance, and HTTPS reachability for both custom
  domains.
- Update Netlify runtime configuration so the dashboard calls
  `https://api.atlas.grafley.com`.
- Update Render runtime configuration so `ATLAS_API_FRONTEND_ORIGIN` allows
  `https://atlas.grafley.com`.
- Record the accepted final OAuth redirect URI candidate for WO-056:
  `https://api.atlas.grafley.com/api/auth/google/callback`, unless the
  implementation discovers a different canonical callback path in source.
- Preserve provider-generated Netlify and Render URLs as rollback references.

## 4. Explicitly Out of Scope

Changing hosting providers, changing DNS registrars, provisioning wildcard
domains, changing Google OAuth scopes, creating broad public launch collateral,
running hosted migrations, creating release tags, or using production mailbox
data are excluded.

This Work Order does not authorize Codex to change Grafley DNS records unless
the Repository Maintainer separately provides an in-scope DNS tool and explicit
authority for the exact records.

## 5. Verification and Completion

Require provider-domain configuration evidence, DNS record handoff evidence,
post-DNS HTTPS checks for both custom domains, API CORS/readiness evidence from
`https://atlas.grafley.com`, redaction scans, and an implementation report
under `docs/reviews/`.

WO-056A is complete when the final Grafley frontend and API domains are active
or when the Repository Maintainer explicitly records a deferment allowing WO-056
to proceed with provider-generated URLs.

## 6. Rollback Expectations

Rollback must preserve the existing provider-generated Netlify and Render URLs,
restore Netlify and Render runtime variables to the provider-generated URLs if
needed, remove or disable incorrect custom-domain bindings if they create
traffic risk, and record the residual OAuth redirect impact before WO-056
continues.

## 7. Stop-and-Ask Triggers

Stop before changing domain names, provisioning DNS records without explicit
DNS authority, proceeding when provider custom-domain setup requires a new paid
plan or ownership decision, broadening Google OAuth scope, exposing provider
secrets, or finalizing OAuth against temporary provider URLs while the Grafley
custom-domain cutover remains pending.
