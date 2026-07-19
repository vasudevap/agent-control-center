# WO-055 Render API and PostgreSQL Deployment Implementation Report

**Work Order:** [WO-055](../work-orders/055-render-api-and-postgresql-deployment.md)
**Status:** Blocked - Secret/Database Binding Pending
**Date:** 2026-07-19
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Summary

WO-055 implementation has started. The Render API service and PostgreSQL
database targets now exist, and the API liveness endpoint is reachable. The
API readiness endpoint correctly fails closed until required database,
owner-identity, signing, webhook, and Google OAuth configuration is entered
through provider-native secret storage.

No database connection URL, password, OAuth secret, token, or signing secret
was displayed, copied to Git, captured in screenshots, or shared in chat.

## Scope Implemented

- Installed and authenticated the official Render CLI.
- Set the active Render workspace to the only available workspace:
  `My Workspace`.
- Created the Render PostgreSQL target:
  - name: `atlas-agent-control-center-db`
  - ID: `dpg-d9e2rkbrjlhs73bkc6dg-a`
  - region: `ohio`
  - PostgreSQL version: `18`
  - plan: `basic_256mb`
  - status: `available`
- Created the Render API web service:
  - name: `atlas-agent-control-center-api`
  - ID: `srv-d9e2rprbc2fs73f4l23g`
  - URL: `https://atlas-agent-control-center-api.onrender.com`
  - branch: `main`
  - commit deployed: `17b5415dd9e009c3b15a78c95e142df05b3f5ece`
  - runtime: Python
  - build command: `python -m pip install -c apps/api/constraints.txt -e "apps/api"`
  - start command: `python -m uvicorn atlas_api.main:app --app-dir apps/api/src --host 0.0.0.0 --port $PORT`
  - health check: `/health/live`
- Configured only non-secret API values:
  - `ATLAS_API_ENVIRONMENT=production`
  - `ATLAS_API_REQUIRE_DATABASE=true`

## Hosted API Evidence

Liveness:

```text
curl -s https://atlas-agent-control-center-api.onrender.com/health/live
```

Result:

```json
{"status":"ok","service":"atlas-api","environment":"production"}
```

Readiness:

```text
curl -s https://atlas-agent-control-center-api.onrender.com/health/ready
```

Result:

```json
{"status":"not_ready","service":"atlas-api","checks":{"configuration":"failed"},"problems":["database_url_missing","external_client_id_missing","external_client_key_id_missing","external_client_secret_missing","google_oauth_client_id_missing","google_oauth_client_secret_missing","google_oauth_redirect_uri_missing","owner_identity_subject_missing","webhook_signing_key_id_missing","webhook_signing_secret_missing"]}
```

The readiness response contains stable problem codes only and does not expose
secret values.

## Explicitly Not Performed

- No hosted migration was run.
- No database URL was fetched with `render postgres get`.
- No database connection string was configured on the API service.
- No owner identity, external-client signing secret, webhook signing secret, or
  Google OAuth secret was entered.
- No production Gmail/Drive workflow was run.
- No release tag or public launch action was performed.

## Safety Evidence

- `render postgres get --output json` was rejected by the execution safety
  reviewer because it could disclose provider connection details. That command
  was not retried through another path.
- Render status evidence was collected through the safer resource inventory
  command, which reported service and database status without connection
  strings.
- The API readiness endpoint proves missing production-critical values fail
  closed.

## Validation Commands

Backend release-readiness provider guard:

```text
apps/api/.venv/bin/python -m pytest apps/api/tests/test_release_readiness.py
```

Result:

```text
2 passed
```

Frontend production build after deployment fixes:

```text
npm --workspace @atlas/web run build
```

Result:

```text
Passed under elevated local execution
```

## Blocker

WO-055 is not complete because the API service still needs provider-native
secret and database binding values:

- `ATLAS_API_DATABASE_URL`
- `ATLAS_API_OWNER_IDENTITY_SUBJECT`
- `ATLAS_API_EXTERNAL_CLIENT_ID`
- `ATLAS_API_EXTERNAL_CLIENT_KEY_ID`
- `ATLAS_API_EXTERNAL_CLIENT_SECRET`
- `ATLAS_API_WEBHOOK_SIGNING_KEY_ID`
- `ATLAS_API_WEBHOOK_SIGNING_SECRET`
- `ATLAS_API_GOOGLE_OAUTH_CLIENT_ID`
- `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET`
- `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI`

The CLI supports `--env-var KEY=VALUE`, but passing secret values through a
shell command would put them in command text and execution history. Secret
values must be entered through a provider-native flow that does not expose
them in source, logs, screenshots, PRs, or chat.

## Completion State

WO-055 is not complete. The Render targets exist and liveness is healthy, but
readiness is intentionally blocked until secret/database values are safely
bound and WO-057 migration authority is available.
