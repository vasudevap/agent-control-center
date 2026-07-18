# Atlas API

FastAPI backend foundation for the Agent Control Center.

This workspace is introduced by WO-015. It provides health endpoints,
configuration loading, structured errors, correlation IDs, deny-by-default
authorization, signed external-client authentication, webhook delivery
scaffolding, and initial PostgreSQL migration foundations.

It does not implement operational approvals, fact CRUD, ask-instead-of-guess,
Gmail behavior, connector execution, or frontend integration.

## Local commands

From the repository root, create an isolated Python 3.12+ environment and
install the committed dependency resolution:

```bash
python3 -m venv apps/api/.venv
apps/api/.venv/bin/python -m pip install --upgrade pip
apps/api/.venv/bin/python -m pip install -c apps/api/constraints.txt -e "apps/api[dev]"
```

The constraints file is the canonical resolved dependency input for local and
CI installs. Update it only from a clean Python 3.12 environment after the
backend validation suite passes.

Run validation from the repository root:

```bash
apps/api/.venv/bin/python -m pytest apps/api
apps/api/.venv/bin/python -m ruff check apps/api
apps/api/.venv/bin/python -m mypy apps/api/src
```

Database migrations require PostgreSQL 18 and an uncommitted database URL. The
local standard is a developer-managed PostgreSQL 18 service available on your
`PATH`; no container, Compose, or provider configuration is committed here.

```bash
createdb atlas_api_dev
export ATLAS_API_DATABASE_URL='postgresql+psycopg://<local-user>:<local-password>@localhost:5432/atlas_api_dev'
(
  cd apps/api
  .venv/bin/python -m alembic upgrade head
  .venv/bin/python -m alembic downgrade base
)
```

The migration command fails safely when `ATLAS_API_DATABASE_URL` is absent and
does not print the configured value. GitHub Actions runs the same migration
smoke check against a disposable PostgreSQL 18 service with synthetic data.

Run the local development server after installing dependencies:

```bash
apps/api/.venv/bin/python -m uvicorn atlas_api.main:app --app-dir apps/api/src --reload
```

The default `local` environment does not require a database. Any environment
with `ATLAS_API_REQUIRE_DATABASE=true` reports `database_url_missing` through
readiness until `ATLAS_API_DATABASE_URL` is set. `staging` and `production` are
production-like and also require the release-critical owner identity,
external-client signing, webhook signing, and Google OAuth configuration
documented in
[`docs/implementation-plans/phase-7-environment-configuration-and-secrets-readiness.md`](../../docs/implementation-plans/phase-7-environment-configuration-and-secrets-readiness.md).
Configuration uses the `ATLAS_API_` prefix. Do not commit `.env` files or real
credentials.

External-client authentication fails closed unless a persistent database session
factory and all current-key settings are supplied. The approved request proof
uses the client identifier, key identifier, timestamp, nonce, and lowercase
hex HMAC signature headers. The current client ID/key ID/secret use
`ATLAS_API_EXTERNAL_CLIENT_ID`, `ATLAS_API_EXTERNAL_CLIENT_KEY_ID`, and
`ATLAS_API_EXTERNAL_CLIENT_SECRET`; an overlapping rotation key can use
`ATLAS_API_EXTERNAL_CLIENT_NEXT_KEY_ID` and
`ATLAS_API_EXTERNAL_CLIENT_NEXT_SECRET`. Keep all secrets outside the
repository and never use the retired `X-Atlas-Client-Secret` header.

Webhook signing uses `ATLAS_API_WEBHOOK_SIGNING_KEY_ID` and
`ATLAS_API_WEBHOOK_SIGNING_SECRET`; an overlapping rotation key can use
`ATLAS_API_WEBHOOK_SIGNING_NEXT_KEY_ID` and
`ATLAS_API_WEBHOOK_SIGNING_NEXT_SECRET`. Google OAuth release readiness uses
`ATLAS_API_GOOGLE_OAUTH_CLIENT_ID`,
`ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET`, and
`ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI`, while preserving the accepted
`gmail.modify` and `drive.file` scope posture.

Operational API routes use the versioned `/api/v1` contract. Successful
responses are wrapped in `data` and optional `meta`; errors use a stable
`error.code`, safe message, and correlation ID. Pagination is cursor-based with
`limit=50` by default and `100` maximum. The canonical details are in
[`docs/specifications/api-contract-conventions.md`](../../docs/specifications/api-contract-conventions.md).

## Scheduler sweep

The scheduler is an internal interval-only foundation: it has no public API,
daemon, worker, or hosted cron resource. A separately invoked one-shot command
locks due schedules, creates at most one queue occurrence per schedule, and
advances the schedule in the same database transaction.

With `ATLAS_API_DATABASE_URL` configured, run one sweep with:

```bash
apps/api/.venv/bin/atlas-schedule-sweep
```

The command prints only the number of triggered schedules. Invocation and
hosting policy are intentionally deferred; do not run this against production
without a later approved deployment work order.
