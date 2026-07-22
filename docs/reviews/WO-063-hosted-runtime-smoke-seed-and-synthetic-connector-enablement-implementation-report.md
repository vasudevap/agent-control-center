# WO-063 Hosted Runtime Smoke Seed and Synthetic Connector Enablement - Implementation Report

**Status:** Completed - Hosted Seed Verified and WO-058 Rerun Passed
**Date:** 2026-07-22
**Work Order:** [WO-063](../work-orders/063-hosted-runtime-smoke-seed-and-synthetic-connector-enablement.md)
**Scope Authorized:** Repository Maintainer accepted WO-063 and authorized implementation on 2026-07-22.

## Summary

WO-063 adds a deliberately bounded, owner-authenticated hosted smoke seed path
to unblock the remaining WO-058 evidence gap without using live Gmail or Drive
content. The implementation creates deterministic synthetic runtime records in
the existing Atlas database tables:

- Gmail and Google Drive connector connections using synthetic account labels
  under `grafley.invalid`;
- one active, manual-run-capable hosted runtime smoke agent;
- one succeeded synthetic manual run with metadata-only run steps;
- one pending synthetic draft-review approval tied to that run;
- metadata-only audit events for the seed action.

The route does not submit OAuth consent, call Google APIs, read or mutate
mailbox or Drive data, expose provider credentials, or add a visible product UI
control.

## Source Changes

- Added `atlas_api.services.smoke_seed.seed_hosted_runtime_smoke` for
  deterministic, idempotent synthetic smoke records.
- Added `POST /api/v1/dashboard/smoke-seed` to the owner-authenticated
  dashboard facade.
- Required owner session, CSRF, and `Idempotency-Key` for the seed operation.
- Added explicit dashboard authorization for the `runtime_smoke_seed:create`
  resource/action.
- Added API tests for authorization failure, CSRF/idempotency behavior,
  synthetic connector/run/approval/audit evidence, and idempotent reruns.
- Added a web runtime adapter test proving seeded records map into the existing
  live dashboard state without frontend fixture promotion.

## Security Evidence

- Browser JavaScript receives only synthetic metadata and normal dashboard
  runtime DTOs.
- No OAuth code, access token, refresh token, Google client secret, external
  client HMAC secret, database URL, owner subject, raw log, Gmail message, or
  Drive object is returned by the seed response.
- Synthetic connector accounts use `grafley.invalid` labels and synthetic
  credential-reference metadata only; no provider token material is created.
- The operation is state-changing and therefore requires owner session, CSRF,
  and idempotency.
- Audit output remains `metadata_only` and uses sanitized audit metadata.

## Validation

Commands run from the repository root:

```text
apps/api/.venv/bin/python -m ruff check apps/api/src/atlas_api/api/dashboard.py apps/api/src/atlas_api/services/smoke_seed.py apps/api/src/atlas_api/core/authorization.py apps/api/tests/test_dashboard_facade.py
apps/api/.venv/bin/python -m pytest apps/api/tests/test_dashboard_facade.py
apps/api/.venv/bin/python -m ruff check apps/api/src apps/api/tests
apps/api/.venv/bin/python -m mypy apps/api/src
apps/api/.venv/bin/python -m pytest apps/api/tests
npm run lint --workspace apps/web
npm run typecheck --workspace apps/web
npm test --workspace apps/web
npm test --workspace apps/web -- dashboard-runtime.test.ts
npm run build --workspace apps/web
git diff --check
rg -n "(sk-[A-Za-z0-9]{20,}|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\s*=|refresh_token|access_token)" <touched files>
```

Results:

- API focused Ruff: passed
- API focused dashboard tests: 8 passed, 1 existing Starlette/httpx
  deprecation warning
- API full Ruff: passed
- API mypy: passed
- API full pytest: 169 passed, 1 existing Starlette/httpx deprecation warning
- Web lint: passed
- Web typecheck: passed
- Web full tests: 22 files passed, 100 tests passed
- Web focused runtime-client tests: 1 file passed, 6 tests passed
- Web production build: passed
- `git diff --check`: passed
- Focused touched-file secret scan: no secret values found; reported only
  expected negative assertions for `access_token` and `refresh_token` absence.

## Hosted Deployment and WO-058 Rerun Evidence

PR #109 merged WO-063 to `main` on 2026-07-22 at merge commit
`18336a3cfec936b97456c8a594ece5969eadad95`.

Post-merge hosted evidence:

- Netlify production deploy `6a60e50ca105e1000899df08` published
  `main@18336a3`; secret scanning reported no classic or enhanced matches.
- `GET https://api.atlas.grafley.com/health/live` returned `status=ok`,
  `service=atlas-api`, `environment=production`.
- `GET https://api.atlas.grafley.com/health/ready` returned `status=ready`
  with no readiness problems.
- Unauthenticated `POST /api/v1/dashboard/smoke-seed` returned
  `401 owner_session_missing`, confirming the route fails closed.
- Owner session verification returned `200`, authenticated, active, and Google
  identity provider through the dashboard facade.
- Owner-authenticated `POST /api/v1/dashboard/smoke-seed` returned `200` with
  `synthetic=true`, `scope=hosted_mvp_smoke`, two connector connections, one
  succeeded run, and one pending synthetic draft-review approval.
- Dashboard runtime API evidence showed synthetic Gmail and Google Drive
  connections with `connected` / `healthy` status.
- Runtime run evidence showed run
  `run_32c066d59fe7457a8c80cd72c805dc71` with `succeeded` status and
  `manual` trigger source.
- Runtime approval evidence showed approval
  `appr_5a64dc95895743d4b73f65e081ed58cb` with `pending` status and
  `synthetic_draft_review` action type.
- Runtime audit evidence showed `dashboard.seed_runtime_smoke` and
  `smoke_seed.hosted_runtime_seeded` events with `metadata_only` redaction and
  `succeeded` result.
- Runtime monitoring evidence returned `ready`, zero readiness problems,
  `runtime_origin=atlas-api`, and one runtime agent.

No Gmail or Drive OAuth consent was submitted. No Google APIs were called. No
mailbox or Drive data was read, searched, created, modified, or deleted. No
provider token, OAuth code, CSRF token, cookie, owner subject value, secret, raw
log, Gmail message, or Drive object was recorded.

WO-063 is complete. WO-058 reran successfully after WO-063 deployment. WO-059
rollback/withdrawal rehearsal is now the next dependency-ready cutover Work
Order; WO-060 remains blocked until WO-059 completes and final go/no-go / tag
authority is recorded.

## Rollback

Rollback can remove the smoke seed service, dashboard facade route, and
authorization rule. The rollback does not require provider cleanup because the
implementation does not submit OAuth consent, store live provider credentials,
or touch Gmail/Drive data.
