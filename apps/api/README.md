# Atlas API

FastAPI backend foundation for the Agent Control Center.

This workspace is introduced by WO-015. It provides health endpoints,
configuration loading, structured errors, correlation IDs, external-client
authentication scaffolding, webhook delivery scaffolding, and initial
PostgreSQL migration foundations.

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

The default `local` environment does not require a database. `staging` and
`production`, or any environment with `ATLAS_API_REQUIRE_DATABASE=true`, report
`database_url_missing` through readiness until `ATLAS_API_DATABASE_URL` is set.
Configuration uses the `ATLAS_API_` prefix. Do not commit `.env` files or real
credentials.
