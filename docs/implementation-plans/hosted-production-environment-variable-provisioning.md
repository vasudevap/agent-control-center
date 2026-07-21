# Hosted Production Environment Variable Provisioning

**Status:** Accepted - WO-053 In Progress
**Owner:** Repository Maintainer
**Date:** 2026-07-19
**Work Order:** [WO-053](../work-orders/053-production-environment-and-secrets-provisioning.md)
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)

---

## 1. Purpose

Record the provider-native environment variable and secret provisioning map for
the hosted MVP production cutover without storing secret values.

This file contains variable names, provider locations, required dependency
state, redaction posture, and owner expectations only.

## 2. Provider Target State

| Provider target | Expected location | WO-053 state | Blocking dependency |
| --- | --- | --- | --- |
| Netlify dashboard site | Netlify site environment variables for `@atlas/web` | Configured, deploy healthy | Runtime-health browser evidence captured; backend readiness remains WO-055 |
| Render API service | Render service environment variables or environment group | Partially configured | Owner identity subject still requires provider-native value entry |
| Render PostgreSQL database | Render PostgreSQL internal connection reference | Created and bound | Hosted migrations require WO-057 authority and backup/restore evidence |
| Google OAuth client | Google Cloud OAuth client configuration and secret store | Configured | Configured for `grafleyinc@gmail.com` after Repository Maintainer confirmed `atlas-owner@grafley.com` is not a Google account |
| Google OIDC owner client | Google Cloud OAuth client configuration and Render secret store | Configured | Immutable owner subject and controlled authorization remain WO-061 work |
| External product client | Render API environment variables or environment group | Configured in API environment | Database-side client/owner linkage remains migration/seed dependent |
| Webhook signing | Render API environment variables or environment group | Configured in API environment | Rotation-only variables remain unset |

WO-053 can verify the inventory and redaction posture before target resources
exist. It must not claim provider-side provisioning is complete until the
provider targets exist and redacted evidence is captured.

## 3. Netlify Variables

| Variable | Provider location | Secret | Current WO-053 state |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Netlify production environment, `@atlas/web` | No | Cut over to `https://api.atlas.grafley.com` under WO-056A; production rebuild completed |
| `NEXT_PUBLIC_APP_ENV` | Netlify production environment, `@atlas/web` | No | Configured as production |
| `NEXT_PUBLIC_RELEASE_VERSION` | Netlify production environment, `@atlas/web` | No | Configured to reviewed source commit |

`NEXT_PUBLIC_` variables are browser-visible and must never contain secret
values.

Planned custom-domain cutover under WO-056A:

- Final dashboard origin: `https://atlas.grafley.com`
- Final API origin: `https://api.atlas.grafley.com`
- Current provider-generated URLs remain rollback references after WO-056A
  verified DNS, TLS, and runtime behavior.
- Netlify and Render custom-domain bindings are configured. The Repository
  Maintainer provisioned the accepted Grafley CNAME records, provider TLS is
  active, and runtime variables have been cut over:
  - `atlas` CNAME to `atlas-agent-control-center.netlify.app`
    - provisioned; Netlify TLS issued and production HTTPS verified
  - `api.atlas` CNAME to `atlas-agent-control-center-api.onrender.com`
    - provisioned and verified by Render; custom-domain HTTPS and final-origin
      CORS verified

## 4. Render API Variables

### Canonical Render Location

Atlas production resources are project-scoped. Use **My project -> Production
-> atlas-agent-control-center-api -> Environment**, not the workspace homepage
resource list. The homepage can show only ungrouped services and is not a
complete inventory.

| Boundary | Canonical identity |
| --- | --- |
| Workspace | `My Workspace` (`tea-d8dqftek1jcs7399msjg`) |
| Project | `My project` (`prj-d8dqn1mk1jcs7399ubvg`) |
| Environment | `Production` (`evm-d8dqn1mk1jcs7399uc00`) |
| API service | `atlas-agent-control-center-api` (`srv-d9e2rprbc2fs73f4l23g`) |
| PostgreSQL database | `atlas-agent-control-center-db` (`dpg-d9e2rkbrjlhs73bkc6dg-a`) |

The repository maintainer's Render login is the established provider identity
for this workspace. Do not infer the provider account from Google, Gmail, or
Grafley account context.

| Variable | Provider location | Secret | Current WO-053 state |
| --- | --- | --- | --- |
| `ATLAS_API_ENVIRONMENT` | Render API service or environment group | No | Configured as production |
| `ATLAS_API_FRONTEND_ORIGIN` | Render API service or environment group | No | Cut over to `https://atlas.grafley.com` under WO-056A and redeployed |
| `ATLAS_API_DATABASE_URL` | Render API service, database reference | Yes | Configured from Render internal database URL without value exposure |
| `ATLAS_API_REQUIRE_DATABASE` | Render API service or environment group | No | Configured as true |
| `ATLAS_API_OWNER_IDENTITY_SUBJECT` | Render API service or environment group | No | Configured from controlled `grafleyinc@gmail.com` owner authorization without recording the value |
| `ATLAS_API_EXTERNAL_CLIENT_ID` | Render API service or environment group | No | Configured |
| `ATLAS_API_EXTERNAL_CLIENT_KEY_ID` | Render API service or environment group | No | Configured |
| `ATLAS_API_EXTERNAL_CLIENT_SECRET` | Render API service or environment group | Yes | Configured without value exposure |
| `ATLAS_API_EXTERNAL_CLIENT_NEXT_KEY_ID` | Render API service or environment group | No | Rotation only |
| `ATLAS_API_EXTERNAL_CLIENT_NEXT_SECRET` | Render API service or environment group | Yes | Rotation only |
| `ATLAS_API_WEBHOOK_SIGNING_KEY_ID` | Render API service or environment group | No | Configured |
| `ATLAS_API_WEBHOOK_SIGNING_SECRET` | Render API service or environment group | Yes | Configured without value exposure |
| `ATLAS_API_WEBHOOK_SIGNING_NEXT_KEY_ID` | Render API service or environment group | No | Rotation only |
| `ATLAS_API_WEBHOOK_SIGNING_NEXT_SECRET` | Render API service or environment group | Yes | Rotation only |
| `ATLAS_API_GOOGLE_OAUTH_CLIENT_ID` | Render API service or environment group | No | Configured from Google OAuth web client without value exposure |
| `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET` | Render API service or environment group | Yes | Configured through provider-native Render secret entry without value exposure |
| `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI` | Render API service or environment group | No | Configured as `https://atlas.grafley.com/oauth/google/callback` |
| `ATLAS_API_OWNER_OIDC_CLIENT_ID` | Render API service | No | Configured for the separate WO-061 Google OIDC client without value exposure |
| `ATLAS_API_OWNER_OIDC_CLIENT_SECRET` | Render API service | Yes | Configured through provider-native secret entry; rotated during setup and not recorded |
| `ATLAS_API_OWNER_OIDC_REDIRECT_URI` | Render API service | No | Configured as `https://api.atlas.grafley.com/auth/owner/google/callback` |
| `ATLAS_API_OWNER_OIDC_BOOTSTRAP_EMAIL` | Render API service | No | Configured as the accepted owner bootstrap account |
| `ATLAS_API_OWNER_OIDC_TRANSACTION_SECRET` | Render API service | Yes | Generated and configured in Render; rotated during setup and not recorded |
| `ATLAS_API_OWNER_SESSION_IDLE_MINUTES` | Render API service or environment group | No | Optional default available |
| `ATLAS_API_OWNER_SESSION_ABSOLUTE_HOURS` | Render API service or environment group | No | Optional default available |

## 5. Redaction and Readiness Rules

- Secret values must be entered only through provider-native UI, CLI, or API
  flows that do not write values to Git, screenshots, logs, PRs, or chat.
- Evidence may record variable names, provider locations, configured/not
  configured state, timestamps, command names, and redacted markers.
- Production-like readiness remains fail-closed until the required backend
  variables are configured.
- Rotation-only variables must remain unset unless a rotation window is opened
  by a later Work Order or incident response decision.
- If a secret value is exposed, rotate or revoke it immediately and record the
  incident without reproducing the exposed value.

## 6. Owner and Emergency Response

| Area | Owner | Emergency action |
| --- | --- | --- |
| Netlify dashboard variables | Repository Maintainer | Remove incorrect browser-visible values and redeploy |
| Render API secrets | Repository Maintainer | Rotate affected service secret and redeploy |
| Render PostgreSQL URL | Repository Maintainer | Rotate database credentials or restore provider reference |
| Google OAuth client secret | Repository Maintainer | Rotate or revoke OAuth client secret in Google Cloud |
| Google OIDC owner client secret | Repository Maintainer | Rotate or revoke the dedicated owner OIDC client secret in Google Cloud |
| External-client signing secret | Repository Maintainer | Add next key, migrate client, retire exposed key |
| Webhook signing secret | Repository Maintainer | Add next key, migrate receiver verification, retire exposed key |

## 7. WO-053 Provider Check Evidence

Provider checks performed on 2026-07-19:

| Check | Result | Side effect |
| --- | --- | --- |
| Netlify CLI authentication | Authenticated account detected | Read-only |
| Netlify local site link | Repository is not linked to a Netlify site | Read-only |
| Netlify site inventory for `@atlas/web` | No Atlas / Agent Control Center site target identified | Read-only |
| Render CLI availability | No Render CLI found in local path | Read-only |
| Local provider env-name scan | No `NETLIFY_`, `RENDER_`, `ATLAS_`, `GOOGLE_`, `GMAIL_`, or `DRIVE_` shell variable names found | Read-only |
| Committed provider config scan | No `.env`, `netlify.toml`, or `render.yaml` found in the repository root tree | Read-only |

No provider environment variables or secrets were created, changed, displayed,
or committed during these checks.
