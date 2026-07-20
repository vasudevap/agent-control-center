# Phase 7 Environment Configuration and Secrets Readiness

**Status:** Implemented - Pending Review
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Work Order:** [WO-047](../work-orders/047-environment-configuration-and-secrets-readiness.md)
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)

---

## 1. Purpose

Define the release-readiness configuration inventory for Atlas before any live
Gmail, Google Drive, Netlify, Render, or production database use.

This record contains names, ownership, environment posture, and safety rules
only. It does not contain secret values and does not authorize live credential
creation or production deployment.

## 2. Environment Model

| Environment | Purpose | Secret posture | Readiness posture |
| --- | --- | --- | --- |
| Local | Developer iteration and fake-provider validation | Developer shell or ignored local env file | Does not require database or release secrets by default |
| Test / CI | Automated validation with synthetic data | GitHub Actions secrets only if later required | Does not require provider production secrets |
| Development | Hosted integration smoke checks after provisioning authority | Netlify and Render non-production variables | Must provide release-critical config before hosted smoke use |
| Staging | Deferred pre-production environment | Provider-native variables | Treated as production-like by backend readiness |
| Production | Explicitly approved single-owner operation | Provider-native variables only | Treated as production-like by backend readiness |

## 3. Backend Configuration Inventory

All backend variables use the `ATLAS_API_` prefix.

| Variable | Required in staging/production | Secret | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `ATLAS_API_ENVIRONMENT` | Yes | No | Maintainer | Selects `local`, `development`, `test`, `staging`, or `production` behavior |
| `ATLAS_API_DATABASE_URL` | Yes | Yes | Maintainer | PostgreSQL runtime system of record and migration target |
| `ATLAS_API_REQUIRE_DATABASE` | Optional | No | Maintainer | Forces database readiness in non-production checks |
| `ATLAS_API_OWNER_IDENTITY_SUBJECT` | Yes | No | Maintainer | Single-owner identity binding |
| `ATLAS_API_EXTERNAL_CLIENT_ID` | Yes | No | Maintainer | Governed external product client identity |
| `ATLAS_API_EXTERNAL_CLIENT_KEY_ID` | Yes | No | Maintainer | Current external-client signing key identifier |
| `ATLAS_API_EXTERNAL_CLIENT_SECRET` | Yes | Yes | Maintainer | Current external-client HMAC signing secret |
| `ATLAS_API_EXTERNAL_CLIENT_NEXT_KEY_ID` | Rotation only | No | Maintainer | Overlapping next external-client key identifier |
| `ATLAS_API_EXTERNAL_CLIENT_NEXT_SECRET` | Rotation only | Yes | Maintainer | Overlapping next external-client signing secret |
| `ATLAS_API_WEBHOOK_SIGNING_KEY_ID` | Yes | No | Maintainer | Current webhook signing key identifier |
| `ATLAS_API_WEBHOOK_SIGNING_SECRET` | Yes | Yes | Maintainer | Current webhook signing secret |
| `ATLAS_API_WEBHOOK_SIGNING_NEXT_KEY_ID` | Rotation only | No | Maintainer | Overlapping next webhook signing key identifier |
| `ATLAS_API_WEBHOOK_SIGNING_NEXT_SECRET` | Rotation only | Yes | Maintainer | Overlapping next webhook signing secret |
| `ATLAS_API_GOOGLE_OAUTH_CLIENT_ID` | Yes | No | Maintainer | Google OAuth client identifier for Gmail and Drive connector setup |
| `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET` | Yes | Yes | Maintainer | Google OAuth client secret |
| `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI` | Yes | No | Maintainer | Approved Google OAuth redirect URI |
| `ATLAS_API_OWNER_SESSION_IDLE_MINUTES` | Optional | No | Maintainer | Owner session idle timeout, default 30 minutes |
| `ATLAS_API_OWNER_SESSION_ABSOLUTE_HOURS` | Optional | No | Maintainer | Owner session absolute timeout, default 12 hours |

## 4. Frontend Configuration Inventory

| Variable | Required for hosted dashboard | Secret | Owner | Purpose |
| --- | --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Yes | No | Maintainer | Browser-visible Atlas API base URL |
| `NEXT_PUBLIC_APP_ENV` | Yes | No | Maintainer | Browser-visible environment label |
| `NEXT_PUBLIC_RELEASE_VERSION` | Recommended | No | Maintainer | Browser-visible release/version identifier |
| `ATLAS_DASHBOARD_EXTERNAL_CLIENT_ID` | Required for server-side OAuth callback | No | Maintainer | Server-side dashboard identity for signed Atlas API callback completion |
| `ATLAS_DASHBOARD_EXTERNAL_CLIENT_KEY_ID` | Required for server-side OAuth callback | No | Maintainer | Server-side dashboard signing key identifier |
| `ATLAS_DASHBOARD_EXTERNAL_CLIENT_SECRET` | Required for server-side OAuth callback | Yes | Maintainer | Server-side dashboard HMAC signing secret for Atlas API callback completion |

Frontend variables prefixed with `NEXT_PUBLIC_` are visible to the browser and
must never contain secret values.

Dashboard variables without the `NEXT_PUBLIC_` prefix must remain server-side
only in Netlify. They must not be read from client components, returned in API
responses, embedded in built client bundles, screenshots, logs, or committed
configuration files.

## 5. Provider Storage Rules

| Location | Allowed | Not allowed |
| --- | --- | --- |
| Local shell or ignored local env file | Local non-production values | Committed `.env` files or real production secrets |
| GitHub Actions | CI-only synthetic credentials when needed | Provider production secrets unless a later Work Order authorizes them |
| Netlify environment variables | Dashboard build/runtime values, including server-side callback signing values | Secret values in repository config files or `NEXT_PUBLIC_` variables |
| Render environment variables/groups | API, worker, cron, database, webhook, and OAuth values | Secret values in `render.yaml` or logs |
| Repository docs and fixtures | Variable names, placeholders, and redacted examples | Real tokens, client secrets, passwords, private keys, or full Gmail bodies |

## 6. Startup and Readiness Behavior

Backend readiness treats `staging` and `production` as production-like
environments. In those environments, readiness fails closed with stable problem
codes until all required release-critical values are configured:

- `database_url_missing`
- `external_client_id_missing`
- `external_client_key_id_missing`
- `external_client_secret_missing`
- `google_oauth_client_id_missing`
- `google_oauth_client_secret_missing`
- `google_oauth_redirect_uri_missing`
- `owner_identity_subject_missing`
- `webhook_signing_key_id_missing`
- `webhook_signing_secret_missing`

Readiness problem codes must not include secret values.

## 7. OAuth Setup Expectations

- Keep the accepted Google scopes: `gmail.modify` and `drive.file`.
- Do not request `https://mail.google.com/`.
- Configure Google OAuth redirect URIs from
  `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI`.
- Use provider-native secret storage for the OAuth client secret.
- Rotate or revoke the Google OAuth client secret if exposure is suspected.
- Do not use live Google credentials until a Work Order explicitly authorizes
  the target account and evidence boundary.

## 8. Rotation and Emergency Response

External-client and webhook signing secrets support overlapping current/next
configuration. Rotation should:

1. Add the next key ID and secret through provider-native secret storage.
2. Deploy and verify both current and next keys are accepted where applicable.
3. Move clients or webhook consumers to the next key.
4. Remove the retired key after the overlap window.
5. Record the rotation in audit or release evidence without writing secret
   values.

If exposure is suspected, revoke or rotate the affected credential immediately,
review logs for accidental disclosure, and record the incident and recovery
steps in the applicable release or incident report.
