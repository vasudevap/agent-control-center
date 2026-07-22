# WO-063 Hosted Runtime Smoke Seed and Synthetic Connector Enablement - Implementation Report

**Status:** Source Implemented - Pending Hosted Deployment and WO-058 Rerun
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

## Remaining Work

WO-063 is source-implemented locally. It is not complete until the source is
merged, deployed to the hosted targets, and WO-058 reruns successfully through
the owner-authenticated dashboard surfaces using the synthetic seed evidence.

WO-059 rollback/withdrawal rehearsal and WO-060 release closeout remain blocked
until WO-058 passes after WO-063 deployment.

## Rollback

Rollback can remove the smoke seed service, dashboard facade route, and
authorization rule. The rollback does not require provider cleanup because the
implementation does not submit OAuth consent, store live provider credentials,
or touch Gmail/Drive data.
