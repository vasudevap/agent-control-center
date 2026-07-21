# WO-055 Render API and PostgreSQL Deployment Implementation Report

**Work Order:** [WO-055](../work-orders/055-render-api-and-postgresql-deployment.md)
**Status:** In Progress - Hosted API Ready; Migration Pending
**Date:** 2026-07-19
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Reconciliation - 2026-07-20 (WO-061 local source implementation)

The deployment evidence below predates the completed WO-061 owner identity
enrollment. WO-061 has since deployed the owner-OIDC API routes, completed
controlled owner authorization with `grafleyinc@gmail.com`, manually bound the
opaque owner subject in Render without value exposure, and cleared the hosted
configuration-readiness gate. The remaining WO-055-adjacent gate is the
separately governed migration work under WO-057.

## Summary

WO-055 implementation has started. The Render API service and PostgreSQL
database targets now exist, the API liveness endpoint is reachable, and the
Render database URL plus external-client/webhook signing values are now bound
through provider-native service environment variables. After WO-061 owner
identity binding, the API readiness endpoint returns `ready` with no
configuration problems. Hosted database migrations remain separately governed
by WO-057.

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

Provider-native update on 2026-07-20:

- Bound the Render internal PostgreSQL URL to `ATLAS_API_DATABASE_URL` without
  printing or storing the URL value.
- Configured the current external-client identity/key variables:
  - `ATLAS_API_EXTERNAL_CLIENT_ID`
  - `ATLAS_API_EXTERNAL_CLIENT_KEY_ID`
  - `ATLAS_API_EXTERNAL_CLIENT_SECRET`
- Configured the current webhook signing variables:
  - `ATLAS_API_WEBHOOK_SIGNING_KEY_ID`
  - `ATLAS_API_WEBHOOK_SIGNING_SECRET`
- Left rotation-only variables unset.

## Reconciliation - 2026-07-20

Hosted dashboard smoke testing under WO-054 initially proved the Netlify
deployment could render with `NEXT_PUBLIC_API_BASE_URL`, but browser runtime
health settled to `Runtime unavailable`. Direct API checks showed
`/health/ready` returned stable readiness problem codes over curl, while
responses from the Netlify origin lacked `Access-Control-Allow-Origin` and
browser preflight received `405`.

A narrow source fix now adds optional CORS support controlled by
`ATLAS_API_FRONTEND_ORIGIN`. It is intended to allow only the accepted Netlify
origin to perform browser-safe `GET` calls such as `/health/ready`; it does not
weaken readiness checks, expose secrets, or broaden provider topology.

The non-secret value was configured in Render and deployed by
`dep-d9f3m1ernols73fc43k0` from
`fd04ec47edd5ad425dbc4de6e09bf707fb3b2156`:

- `ATLAS_API_FRONTEND_ORIGIN=https://atlas-agent-control-center.netlify.app`

After that deploy, the hosted API returns the expected CORS headers for the
accepted Netlify origin and the dashboard settles to `Runtime not ready (10)`.
The remaining `not_ready` payload at that point was expected until
provider-native secret and database binding was completed.

Later on 2026-07-20, provider-native Render UI updates bound the database URL,
external-client signing values, and webhook signing values. Render deploy
`dep-d9f5j43rjlhs73djmmog` made those values live from
`6a1db71bb2a9404070ac5ace84a710dbe70a19f3`.

Additional provider-native rotation on 2026-07-20 preserved the existing
external-client identity and replaced only the current external-client key ID
and HMAC secret so the Netlify dashboard callback route can sign
server-to-server completion requests. Render deploy
`dep-d9fa0r3rjlhs739t64vg` was triggered by `service_updated`, reached `live`,
and deployed commit `c5ead8140bab8a6259a3826d19d50013343052a8`. No HMAC secret
value was written to Git or recorded in this report.

Google OAuth provider-native binding on 2026-07-20 configured
`ATLAS_API_GOOGLE_OAUTH_CLIENT_ID`, `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET`, and
`ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI` in Render without value exposure. Hosted
readiness after that Render environment update no longer reported Google OAuth
variable problems and remained fail-closed only for
`owner_identity_subject_missing` in the then-deployed revision.

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

Readiness after Render database/signing binding:

```text
curl -s -i -H 'Origin: https://atlas-agent-control-center.netlify.app' \
  https://atlas-agent-control-center-api.onrender.com/health/ready
```

Result:

```text
HTTP/2 200
access-control-allow-origin: https://atlas-agent-control-center.netlify.app

{"status":"not_ready","service":"atlas-api","checks":{"configuration":"failed"},"problems":["google_oauth_client_id_missing","google_oauth_client_secret_missing","google_oauth_redirect_uri_missing","owner_identity_subject_missing"]}
```

Hosted dashboard smoke after the same deploy settled to
`Runtime not ready (4)`.

CORS readiness check from the accepted Netlify origin:

```text
curl -s -i -H 'Origin: https://atlas-agent-control-center.netlify.app' \
  https://atlas-agent-control-center-api.onrender.com/health/ready
```

Result:

```text
HTTP/2 200
access-control-allow-origin: https://atlas-agent-control-center.netlify.app

{"status":"not_ready","service":"atlas-api","checks":{"configuration":"failed"},"problems":["database_url_missing","external_client_id_missing","external_client_key_id_missing","external_client_secret_missing","google_oauth_client_id_missing","google_oauth_client_secret_missing","google_oauth_redirect_uri_missing","owner_identity_subject_missing","webhook_signing_key_id_missing","webhook_signing_secret_missing"]}
```

CORS preflight:

```text
curl -s -i -X OPTIONS -H 'Origin: https://atlas-agent-control-center.netlify.app' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: accept' \
  https://atlas-agent-control-center-api.onrender.com/health/ready
```

Result:

```text
HTTP/2 200
access-control-allow-methods: GET
access-control-allow-origin: https://atlas-agent-control-center.netlify.app

OK
```

## Explicitly Not Performed

- No hosted migration was run.
- No database URL was fetched with `render postgres get`.
- No database connection string was printed, written to files, committed, or
  shared in chat. The internal database URL was transferred from the Render
  database page to the Render service environment form without recording the
  value.
- Google OAuth values were later entered through provider-native storage
  without value exposure. The current source additionally awaits separately
  governed owner-OIDC configuration and owner-subject enrollment.
- No production Gmail/Drive workflow was run.
- No release tag or public launch action was performed.

## Safety Evidence

- `render postgres get --output json` was rejected by the execution safety
  reviewer because it could disclose provider connection details. That command
  was not retried through another path.
- Render status evidence was collected through the safer resource inventory
  command, which reported service and database status without connection
  strings.
- Render logs after deploy `dep-d9f5j43rjlhs73djmmog` showed build, liveness,
  and service-live events without environment values, database URLs, OAuth
  tokens, or signing secrets.
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
owner identity and Google OAuth values:

- `ATLAS_API_OWNER_IDENTITY_SUBJECT`
- `ATLAS_API_GOOGLE_OAUTH_CLIENT_ID`
- `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET`
- `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI`

The CLI supports `--env-var KEY=VALUE`, but passing secret values through a
shell command would put them in command text and execution history. Secret
values must be entered through a provider-native flow that does not expose
them in source, logs, screenshots, PRs, or chat.

## Completion State

WO-055 is no longer blocked by owner identity or Google OAuth configuration.
The Render targets exist, liveness is healthy, and hosted readiness now returns
`ready` with no configuration problems. Hosted database migrations remain
deferred until WO-057 migration authority and backup/restore evidence are
available.
