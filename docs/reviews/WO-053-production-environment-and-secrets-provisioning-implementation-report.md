# WO-053 Production Environment and Secrets Provisioning Implementation Report

**Work Order:** [WO-053](../work-orders/053-production-environment-and-secrets-provisioning.md)
**Status:** In Progress - Render Database and Signing Bound; Owner/OAuth Pending
**Date:** 2026-07-19
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Reconciliation - 2026-07-20 (post PR #93)

After the ADR-006 callback route was implemented and deployed, Netlify
production was configured with the non-secret server-side
`ATLAS_DASHBOARD_BASE_URL` value required to keep hosted OAuth callback
redirects on the accepted Grafley product domain.

Evidence, with values redacted before output:

- `ATLAS_DASHBOARD_BASE_URL` exists in Netlify for the
  `atlas-agent-control-center` site, is not marked secret, and has a non-empty
  production value.
- Netlify also stores empty placeholder values for `dev`, `branch-deploy`,
  `deploy-preview`, and `dev-server`; these do not change the production
  behavior.
- Production build `6a5e9b7efb8cc864c21fa9f8` created deploy
  `6a5e9b7efb8cc864c21fa9fa`, which reached `deploy_state=ready` with
  `error=null`.
- A hosted callback-denial check returned `HTTP/2 307` with
  `location:
  https://atlas.grafley.com/connectors?oauth=google&status=denied`, confirming
  the callback no longer redirects to the Netlify provider hostname.

No OAuth client secret, authorization code, access token, refresh token,
database URL, HMAC secret, or provider API token was written to Git or printed
in validation output.

## Reconciliation - 2026-07-19 (post WO-054 / WO-055)

The original blocker recorded below ("provider targets not yet provisioned")
has since been resolved by subsequent same-day Work Orders; the original
sections are retained as a point-in-time record.

- The Atlas Netlify site now exists (`atlas-agent-control-center`, created under
  WO-054). Live check after the WO-054 reconciliation deploy: the production
  URL returns HTTP 200 and the hosted dashboard runtime indicator reaches the
  API.
- The Render API service and PostgreSQL database now exist (created under
  WO-055). Live check: `/health/live` returns `status: ok`; `/health/ready`
  fails closed with configuration problem codes only (no secret values).
- Non-secret provider variables are configured on both providers per the WO-054
  and WO-055 implementation reports, including the Render API frontend origin
  used for the dashboard readiness CORS path.

WO-053's remaining gate is therefore no longer provider-target creation.
Subsequent provider-native updates have now bound the Render database URL,
external-client signing values, and webhook signing values without recording
secret values. Owner identity and Google OAuth client configuration remain
pending because they require maintainer/Google-account facts, not generated
placeholders.

No secret values were displayed, written to Git, captured in screenshots, or
shared in chat during this reconciliation.

## Summary

WO-053 is accepted and implementation was started. The source-level
environment variable inventory and redacted provider provisioning map are now
recorded, but provider-side secret provisioning cannot honestly be completed
until the target Netlify and Render resources exist.

No secret values were created, displayed, written to Git, captured in
screenshots, or shared in chat.

## Scope Implemented

- Recorded the accepted ES-008 / ADP-005 / WO-053 through WO-060 authority.
- Added the hosted production environment variable provisioning map:
  `docs/implementation-plans/hosted-production-environment-variable-provisioning.md`.
- Confirmed the backend production-like readiness contract already fails
  closed until required configuration is present.
- Confirmed browser-visible `NEXT_PUBLIC_` variables remain non-secret only.
- Captured provider-target evidence without recording provider secrets.

## Provider Evidence

| Provider area | Evidence | Result |
| --- | --- | --- |
| Netlify CLI authentication | `netlify status` | Authenticated account detected |
| Netlify local link | `netlify status` | Repository is not linked to a Netlify site |
| Netlify site inventory | `netlify sites:list --json --filter @atlas/web` | No Atlas / Agent Control Center site target identified; unrelated sites were not changed |
| Render tooling | `which render` | No Render CLI found in local path |
| Local provider variable names | Shell variable-name scan only | No matching provider variable names found |
| Committed provider config | Repository scan | No `.env`, `netlify.toml`, or `render.yaml` found |

All provider checks were read-only. No provider write was performed.

## Blocker (point-in-time; superseded — see Reconciliation above)

At the time of writing, WO-053 required provider-native variable locations that
did not yet exist from the current repository/provider context:

- the Atlas Netlify site is not created or linked;
- the Render API service is not created;
- the Render PostgreSQL database is not created;
- the hosted API URL is not available for Netlify or Google OAuth variables;
- the Google OAuth production redirect URI cannot be finalized until the
  hosted API callback URL exists.

Proceeding by writing placeholders or configuring unrelated provider sites
would violate the WO-053 secret and provider-boundary requirements.

## Safety Evidence

- No provider secret values were requested from the user or written to files.
- No provider tokens, OAuth tokens, database URLs, or client secrets were added
  to source.
- The Netlify output was used only to confirm absence of an Atlas target; no
  unrelated site was modified.
- The Render absence was treated as a blocker, not as permission to invent a
  provider target.

## Validation Commands

Documentation validation:

```text
git diff --check
```

Result:

```text
Passed
```

Secret scan:

```text
Secret-pattern scan over the ES-008, ADP-005, WO-053 through WO-060, WO-053
provisioning map, and WO-053 review files.
```

Result:

```text
No matches
```

## Residual Risks

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Owner identity and Google OAuth values are not yet entered | Pending | Provider-native owner/OAuth entry (tracked with WO-055 / WO-056) |
| Netlify dashboard callback signing values are not yet entered | Pending | Provider-native Netlify server-side `ATLAS_DASHBOARD_EXTERNAL_CLIENT_*` values must match the governed API external-client configuration |
| Netlify dashboard canonical base URL | Complete | `ATLAS_DASHBOARD_BASE_URL` configured and verified for production after PR #93 |
| Render provider access | Established | Render service/database created; database URL, external-client signing, and webhook signing bound through provider-native UI |
| Google OAuth production redirect cannot be finalized | Expected | WO-056 requires Google OAuth client details and authorized owner account evidence |
| Production readiness remains not ready | Expected | Readiness must fail closed until required variables exist |

## Completion State

WO-053 is not complete. Provider targets have since been created under WO-054
(Netlify) and WO-055 (Render API and PostgreSQL), and non-secret variables are
configured. Render database URL, external-client signing, and webhook signing
values have now been bound through provider-native UI without value exposure.
Netlify dashboard canonical base URL has also been configured and verified
without value exposure. The remaining dependency-safe actions are provider-native
Netlify dashboard callback signing, owner identity, and Google OAuth client
configuration; readiness must continue to fail closed until those API-required
values are bound.
