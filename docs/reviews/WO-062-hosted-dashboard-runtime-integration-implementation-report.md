# WO-062 Hosted Dashboard Runtime Integration - Implementation Report

**Status:** Completed - Deployed and Authenticated Runtime Surfaces Verified
**Date:** 2026-07-22
**Work Order:** [WO-062](../work-orders/062-hosted-dashboard-runtime-integration.md)
**Scope Authorized:** Repository Maintainer accepted WO-062 and authorized autonomous implementation, WO-058 rerun, WO-059, and WO-060 continuation.

## Summary

WO-062 implements an owner-authenticated dashboard-to-runtime integration path
without exposing external-client HMAC secrets or provider credentials to the
browser. The final design uses API-owned dashboard facade endpoints protected
by the existing single-owner session cookie and CSRF boundary. The hosted web
dashboard calls these endpoints with browser credentials and renders live
runtime data when the API base URL and owner session are available.

The fixture-only operational pages remain available only as an explicitly
quarantined fallback when no runtime API base URL is configured or runtime data
is unavailable. Release-critical evidence must use the live runtime path after
merge and deployment.

## Source Changes

- Added `atlas_api.api.dashboard` with owner-session-gated facade endpoints:
  - `GET /api/v1/dashboard/session`
  - `POST /api/v1/dashboard/session/logout`
  - `GET /api/v1/dashboard/connectors`
  - `GET /api/v1/dashboard/agents`
  - `POST /api/v1/dashboard/connectors/oauth/start`
  - `POST /api/v1/dashboard/connections/{connection_id}/health`
  - `GET /api/v1/dashboard/runs`
  - `GET /api/v1/dashboard/runs/{run_id}`
  - `POST /api/v1/dashboard/runs`
  - `GET /api/v1/dashboard/approvals`
  - `GET /api/v1/dashboard/approvals/{approval_id}`
  - `GET /api/v1/dashboard/audit`
  - `GET /api/v1/dashboard/monitoring`
- Extended owner-session support so successful owner OIDC callback can create
  or update the single active owner user, bind the configured external product
  client to that owner when needed, issue owner-session cookies, and redirect
  back to the hosted dashboard.
- Added dashboard authorization rules for the human-owner dashboard channel.
- Enabled credentialed CORS for the hosted dashboard origin while keeping
  allowed methods and headers explicit.
- Added `apps/web/src/lib/dashboard-runtime.ts`, a browser-side dashboard API
  client and metadata adapters for connectors, runs, approvals, audit, and
  monitoring.
- Integrated runtime-aware paths into the hosted Connectors, Runs, Run Detail,
  Approvals, Approval Detail, Audit, and Alerts/Monitoring surfaces.

## Security Evidence

- Browser JavaScript receives only runtime metadata, owner-session state, and a
  CSRF token issued by the owner-session facade.
- External-client HMAC secrets, provider credentials, OAuth codes, access
  tokens, refresh tokens, database URLs, owner subject values, and raw logs are
  not exposed in dashboard responses or web adapters.
- Missing, expired, revoked, or invalid owner sessions fail closed with 401.
- State-changing facade calls require a valid owner session and CSRF token.
- Manual run creation preserves existing idempotency-key validation.
- Audit and monitoring views expose metadata only; raw payloads and provider
  content remain server-side.
- Live approval detail is read-only in this slice; decision mutation controls
  remain disabled until a separately accepted safe mutation facade exists.

## Validation

Commands run from the repository root:

```text
apps/api/.venv/bin/python -m ruff check apps/api/src/atlas_api/api/dashboard.py apps/api/src/atlas_api/api/owner_identity.py apps/api/src/atlas_api/core/owner_sessions.py apps/api/src/atlas_api/core/authorization.py apps/api/src/atlas_api/main.py apps/api/tests/test_dashboard_facade.py apps/api/tests/test_owner_identity.py
apps/api/.venv/bin/python -m pytest apps/api/tests/test_dashboard_facade.py apps/api/tests/test_owner_identity.py apps/api/tests/test_owner_sessions.py
apps/api/.venv/bin/python -m pytest apps/api/tests
apps/api/.venv/bin/python -m mypy apps/api/src
npm run lint --workspace apps/web
npm run typecheck --workspace apps/web
npm test --workspace apps/web
npm test --workspace apps/web -- dashboard-runtime.test.ts
npm run build --workspace apps/web
git diff --check
rg -n "(sk-[A-Za-z0-9]|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\s*=|refresh_token|access_token)" <touched files>
```

Results:

- API focused Ruff: passed
- API focused pytest: 18 passed, 1 existing Starlette/httpx deprecation warning
- API full pytest: 165 passed, 1 existing Starlette/httpx deprecation warning
- API mypy: passed
- Web lint: passed
- Web typecheck: passed
- Web tests: 22 files passed, 98 tests passed
- Web focused runtime-client tests: 1 file passed, 4 tests passed
- Web production build: passed
- `git diff --check`: passed
- Focused touched-file secret scan: no secret values found; reported only
  false positives from `risk-*` names in CSS/import strings.

## Remaining Work

WO-062 source implementation, deployment, and authenticated browser
verification are complete. WO-058 was rerun against the hosted runtime path and
is now blocked by a narrower runtime smoke seed / connector enablement gap,
not by dashboard-to-runtime integration. WO-059 rollback/withdrawal rehearsal
and WO-060 release closeout remain blocked until WO-058 reruns successfully.

## Post-Merge Hosted Verification Finding - 2026-07-22

After PR #105 merged and Netlify deployed `main@ff59a93`, hosted verification
confirmed the dashboard facade routes were present in OpenAPI, but
`GET https://api.atlas.grafley.com/api/v1/dashboard/session` returned
`dashboard_store_not_configured`.

Root cause: production `create_app()` populated `app.state.session_factory`
only when tests injected a session factory. The hosted app had a valid
`ATLAS_API_DATABASE_URL` and readiness was green, but no default SQLAlchemy
session factory was created from that setting for API routes that require DB
access.

Follow-up fix: `create_app()` now builds a default SQLAlchemy `sessionmaker`
from the existing normalized database URL when one is configured and no test
session factory is injected. The fix does not add a new provider setting or
schema change.

Additional validation for the follow-up fix:

```text
apps/api/.venv/bin/python -m ruff check apps/api/src apps/api/tests
apps/api/.venv/bin/python -m mypy apps/api/src
apps/api/.venv/bin/python -m pytest apps/api/tests
git diff --check
```

Results:

- API Ruff: passed
- API mypy: passed
- API full pytest: 166 passed, 1 existing Starlette/httpx deprecation warning
- `git diff --check`: passed

## Authenticated Hosted Verification Finding - 2026-07-22

After PR #106 deployed and owner sign-in completed in Chrome, the hosted
dashboard reached `https://atlas.grafley.com/connectors?owner_session=signed_in`
and no longer showed the unauthenticated runtime gate. The Connectors page then
rendered the application error boundary. Browser console evidence identified a
runtime adapter crash: `TypeError: e.scopes.map is not a function`.

Root cause: the hosted dashboard facade returned connector
`required_scopes` using the existing backend connector contract shape,
`operation_id -> scope[]`, while the WO-062 web adapter assumed the field was a
flat `string[]`. The API contract was not wrong; the frontend adapter was too
narrow for the accepted backend shape.

Follow-up fix: the web dashboard adapter now accepts either a flat scope list
or an operation-scoped scope map, flattens and de-duplicates map values for
display, and preserves granted scopes when an owner connection already exists.

Additional validation for the adapter fix:

```text
npm test --workspace apps/web -- dashboard-runtime.test.ts
npm run typecheck --workspace apps/web
npm run lint --workspace apps/web
npm test --workspace apps/web
npm run build --workspace apps/web
git diff --check
rg -n "(sk-[A-Za-z0-9]|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\s*=|refresh_token|access_token)" apps/web/src/lib/dashboard-runtime.ts apps/web/src/lib/dashboard-runtime.test.ts
```

Results:

- Focused web runtime-client tests: 1 file passed, 5 tests passed
- Web typecheck: passed
- Web lint: passed
- Web full tests: 22 files passed, 99 tests passed
- Web production build: passed
- `git diff --check`: passed
- Touched-file secret scan: no matches

PR #107 merged to `main` as `3ce58c8`. GitHub Actions run `29889387816`
passed, and Netlify production deploy `6a603d84c07e05000871e659` published
`main@3ce58c8e1507540408d3b2c57069273cce1e39d3` with no secret-scan matches.
Authenticated browser rerun confirmed that the Connectors page renders
`Live runtime` with Gmail and Google Drive descriptors and no page error.

## Rollback

Rollback can disable or revert the dashboard facade router and the web runtime
client integration. Existing backend contracts, database records, provider
credentials, and hosted migration state are not changed by this rollback. If
the hosted runtime path is unsafe or unusable, WO-058 remains blocked rather
than using fixture-only dashboard evidence.
