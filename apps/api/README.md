# Atlas API

FastAPI backend foundation for the Agent Control Center.

This workspace is introduced by WO-015. It provides health endpoints,
configuration loading, structured errors, correlation IDs, external-client
authentication scaffolding, webhook delivery scaffolding, and initial
PostgreSQL migration foundations.

It does not implement operational approvals, fact CRUD, ask-instead-of-guess,
Gmail behavior, connector execution, or frontend integration.

## Local commands

```bash
python3 -m pip install -e "apps/api[dev]"
python3 -m pytest apps/api
python3 -m ruff check apps/api
python3 -m mypy apps/api/src
```

Run the development server after installing dependencies:

```bash
python3 -m uvicorn atlas_api.main:app --app-dir apps/api/src --reload
```
