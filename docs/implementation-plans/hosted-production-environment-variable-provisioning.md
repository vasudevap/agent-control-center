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
| Render API service | Render service environment variables or environment group | Partially configured | Owner identity and Google OAuth variables still require provider-native value entry |
| Render PostgreSQL database | Render PostgreSQL internal connection reference | Created and bound | Hosted migrations require WO-057 authority and backup/restore evidence |
| Google OAuth client | Google Cloud OAuth client configuration and secret store | Not configured | Requires WO-056 Google OAuth client details and `atlas-owner@grafley.com` owner account evidence |
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

| Variable | Provider location | Secret | Current WO-053 state |
| --- | --- | --- | --- |
| `ATLAS_API_ENVIRONMENT` | Render API service or environment group | No | Configured as production |
| `ATLAS_API_FRONTEND_ORIGIN` | Render API service or environment group | No | Cut over to `https://atlas.grafley.com` under WO-056A and redeployed |
| `ATLAS_API_DATABASE_URL` | Render API service, database reference | Yes | Configured from Render internal database URL without value exposure |
| `ATLAS_API_REQUIRE_DATABASE` | Render API service or environment group | No | Configured as true |
| `ATLAS_API_OWNER_IDENTITY_SUBJECT` | Render API service or environment group | No | Pending Google subject for `atlas-owner@grafley.com` |
| `ATLAS_API_EXTERNAL_CLIENT_ID` | Render API service or environment group | No | Configured |
| `ATLAS_API_EXTERNAL_CLIENT_KEY_ID` | Render API service or environment group | No | Configured |
| `ATLAS_API_EXTERNAL_CLIENT_SECRET` | Render API service or environment group | Yes | Configured without value exposure |
| `ATLAS_API_EXTERNAL_CLIENT_NEXT_KEY_ID` | Render API service or environment group | No | Rotation only |
| `ATLAS_API_EXTERNAL_CLIENT_NEXT_SECRET` | Render API service or environment group | Yes | Rotation only |
| `ATLAS_API_WEBHOOK_SIGNING_KEY_ID` | Render API service or environment group | No | Configured |
| `ATLAS_API_WEBHOOK_SIGNING_SECRET` | Render API service or environment group | Yes | Configured without value exposure |
| `ATLAS_API_WEBHOOK_SIGNING_NEXT_KEY_ID` | Render API service or environment group | No | Rotation only |
| `ATLAS_API_WEBHOOK_SIGNING_NEXT_SECRET` | Render API service or environment group | Yes | Rotation only |
| `ATLAS_API_GOOGLE_OAUTH_CLIENT_ID` | Render API service or environment group | No | Pending Google OAuth client |
| `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET` | Render API service or environment group | Yes | Pending provider-native secret entry |
| `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI` | Render API service or environment group | No | Pending WO-056 callback route decision/client setup; do not configure until the browser-facing Google redirect surface is implemented or confirmed |
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
