# WO-017 Runtime Hardening Implementation Report

**Work Order:** [WO-017 Backend Runtime and Dependency Hardening](../work-orders/017-backend-runtime-and-dependency-hardening.md)
**Implementation Branch:** `codex/wo-017-runtime-hardening-implementation`
**Implementation Status:** Complete - Pending Merge
**Report Date:** 2026-07-17
**Review Owner:** Repository Maintainer

---

## 1. Summary

WO-017 establishes a deterministic, documented backend development and CI
workflow before the next Phase 3 backend increment.

Delivered:

- `apps/api/constraints.txt` commits the resolved direct and transitive Python
  dependencies used by the backend and its development tools.
- Local setup and GitHub Actions both install with the same constraints file.
- The GitHub Actions pip-cache key now includes the constraints file.
- `Settings.environment` accepts only `local`, `development`, `test`,
  `staging`, or `production`.
- Regression coverage verifies database-readiness rules, explicit
  database-required mode, secret redaction, and rejection of an unsupported
  environment.
- Root and backend documentation now define one canonical backend setup,
  validation, migration-smoke, and development-server workflow.

## 2. Scope Guardrails Preserved

The implementation did not introduce:

- live Netlify, Render, PostgreSQL, worker, cron, or production provisioning;
- provider configuration, Terraform, Pulumi, Docker, Compose, or an
  `infrastructure/` directory;
- real secrets, `.env` files, migrations, or schema changes;
- authentication, authorization, API expansion, queue, scheduler, webhook
  hardening, observability, frontend integration, or Phase 5/6 behavior.

No ADR is required: the work preserves the accepted FastAPI toolchain and the
Netlify + Render + Render PostgreSQL strategy.

## 3. Dependency Strategy

The repository uses a committed pip constraints file rather than introducing a
new package manager or lockfile tool. This is the smallest stable mechanism for
the current single-backend workspace: it fixes the selected direct and
transitive dependency versions while preserving the existing `pyproject.toml`
package metadata and editable-install workflow.

Canonical install command:

```bash
apps/api/.venv/bin/python -m pip install -c apps/api/constraints.txt -e "apps/api[dev]"
```

Refresh the constraints only intentionally, using a clean Python 3.12
environment and the full backend validation suite. GitHub Actions provides the
Python 3.12 enforcement point for every pull request and main-branch push.

## 4. Runtime Settings Behavior

| Environment or flag | Database URL absent | Readiness result |
| --- | --- | --- |
| `local`, `development`, `test` | Allowed | Ready unless explicitly required |
| `staging`, `production` | Not allowed | `database_url_missing` |
| `ATLAS_API_REQUIRE_DATABASE=true` | Not allowed | `database_url_missing` |

The `ATLAS_API_` prefix and secret redaction behavior are preserved. Readiness
problems contain stable identifiers only and do not expose configuration values.

## 5. Validation Evidence

Completed locally:

- `apps/api/.venv/bin/python -m pip install -c apps/api/constraints.txt -e "apps/api[dev]"` — passed after allowing the isolated build step to reach PyPI.
- `apps/api/.venv/bin/python -m pytest apps/api` — 15 passed; one existing Starlette/httpx deprecation warning.
- `apps/api/.venv/bin/python -m ruff check apps/api` — passed.
- `apps/api/.venv/bin/python -m mypy apps/api/src` — passed.
- Alembic upgrade/downgrade smoke validation from `apps/api` — passed against
  the existing local SQLite substitute.
- `npm run typecheck` — passed.
- `npm run lint` — passed.
- `npm test` — 17 files and 80 tests passed.
- `npm run build` — passed.
- `git diff --check` — passed.
- Strict secret-pattern scan over changed files — no credential-like values;
  the only textual matches are pre-existing ADR phrases containing
  “ask-instead-of-guess”.

Still required before merge:

- GitHub Actions `Validate` check.

## 6. Residual Risks

| Risk | Treatment |
| --- | --- |
| The local validation environment is Python 3.14 because Python 3.12 is unavailable on this workstation. | CI runs the same constraints workflow on Python 3.12; merge remains gated on that result. |
| The constraints file must be refreshed deliberately as dependencies evolve. | The documented refresh procedure and CI cache input make changes visible and reviewable. |
| Migration smoke checks still use the prior local SQLite substitute. | WO-018 owns the approved local/test PostgreSQL path and migration hardening. |

## 7. Next Recommended Work Order

Proceed to WO-018 — PostgreSQL Environment and Migration Hardening. It should
implement the planned local and CI PostgreSQL strategy without changing the
accepted hosted Render PostgreSQL target or provisioning live resources.
