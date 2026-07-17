# Work Order 017: Backend Runtime and Dependency Hardening

**Status:** Proposed - Review Required
**Work Order ID:** WO-017
**Type:** Backend platform foundation
**Implementation Authorization:** Not Granted
**Accepted:** Not Accepted
**Accepted By:** Not Accepted
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Governing Strategy:** [Infrastructure Provisioning Strategy](../implementation-plans/infrastructure-provisioning-strategy.md)
**Architecture Authority:** [Component Architecture](../architecture/05-component-architecture.md), [Deployment Architecture](../architecture/06-deployment-architecture.md), [Security Architecture](../architecture/07-security-architecture.md), [Data Architecture](../architecture/08-data-architecture.md), [Technology Strategy](../architecture/12-technology-strategy.md)
**Decision Authority:** [ADR-003](../decisions/ADR-003-governed-external-approval-decision-channel.md), [ADR-004](../decisions/ADR-004-governed-external-product-client-contract.md), [ADR-005](../decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md)
**Prerequisite Work Order:** [WO-016 Infrastructure Provisioning and Environment Strategy](./016-infrastructure-provisioning-and-environment-strategy.md)
**Review Owner:** Repository Maintainer

---

## 1. Purpose

Harden the Atlas backend runtime and dependency workflow before broader Phase 3
backend implementation continues.

WO-015 created the first FastAPI backend foundation. WO-016 documented the
infrastructure and environment strategy. WO-017 should make backend dependency
installation, local commands, runtime settings, and CI behavior deterministic
enough for future implementation agents to work from a stable foundation.

## 2. Objective and User Outcome

The repository gains a predictable backend developer and CI workflow:

- backend dependencies install consistently;
- backend command documentation is canonical;
- runtime settings are validated and redacted safely;
- local startup commands are clear;
- CI dependency caching and backend validation remain aligned with the chosen
  dependency strategy;
- future agents can run backend checks without rediscovering setup details.

## 3. Proposed Scope

Acceptance of this Work Order would authorize implementation within the
following scope.

### 3.1 Backend dependency determinism

- Decide and implement the next backend dependency-stability step appropriate
  for the current repository stage.
- The preferred minimum is a committed backend constraints file or equivalent
  deterministic install input for direct and development dependencies.
- A full lockfile tool may be introduced only if the implementation proves it
  is justified, low-risk, and consistent with repository governance.
- Update backend install commands and CI cache inputs to use the selected
  dependency strategy.

### 3.2 Backend command standardization

- Document canonical backend commands for:
  - local environment creation;
  - dependency installation;
  - local API startup;
  - tests;
  - lint;
  - typecheck;
  - Alembic upgrade/downgrade smoke validation.
- Add narrow root scripts or helper commands only if they reduce ambiguity
  without hiding important backend details.

### 3.3 Runtime settings validation

- Tighten backend settings validation without requiring live provider
  resources.
- Preserve the `ATLAS_API_` environment variable prefix.
- Preserve secret redaction for database URLs, external-client secrets, and
  webhook signing secrets.
- Make environment names, database requirements, and readiness problems more
  explicit and testable.
- Add tests for accepted runtime-settings behavior.

### 3.4 CI alignment

- Keep GitHub Actions aligned with the backend dependency strategy.
- Keep backend validation steps explicit:
  - install backend dependencies;
  - backend typecheck;
  - backend lint;
  - backend tests;
  - backend migration smoke check.
- Avoid adding deployment or provider secrets to CI.

### 3.5 Documentation updates

- Update `README.md`, `apps/api/README.md`, and relevant planning/review docs
  to reflect the accepted backend runtime and dependency workflow.
- Add a WO-017 implementation report under `docs/reviews/`.
- Update the Phase 3 backlog and work-order index after completion.

## 4. Explicitly Out of Scope

WO-017 does not authorize:

- live Netlify, Render, database, worker, cron, or production provisioning;
- adding `render.yaml`, `netlify.toml`, Terraform, Pulumi, Docker, or Compose
  files;
- creating a top-level `infrastructure/` directory;
- collecting, storing, or committing real secrets;
- changing provider topology;
- changing the accepted Netlify + Render + Render PostgreSQL strategy;
- replacing FastAPI, SQLAlchemy, Alembic, PostgreSQL, Ruff, mypy, pytest, or
  GitHub Actions without a separate ADR or explicitly accepted exception;
- implementing local/CI PostgreSQL hardening from WO-018;
- changing database schema or adding migrations;
- implementing authentication sessions, authorization policy, API contract
  behavior, queue, scheduler, webhook hardening, observability, Phase 5
  knowledge behavior, or Phase 6 Gmail behavior;
- frontend integration with the backend.

## 5. Required File Scope

The implementing agent may create or modify:

- `apps/api/pyproject.toml`
- backend dependency constraints or lock files under `apps/api/`
- backend runtime settings modules under `apps/api/src/atlas_api/core/`
- backend tests under `apps/api/tests/`
- `.github/workflows/ci.yml`
- root `package.json` only for narrow command delegation if justified
- `README.md`
- `apps/api/README.md`
- relevant `docs/implementation-plans/`, `docs/work-orders/`, and
  `docs/reviews/` files

The implementing agent must not modify frontend source files, migrations,
provider configuration files, live infrastructure, secret-bearing files, or
unrelated documentation.

## 6. Functional Requirements

- A fresh local backend setup path is documented and executable.
- Backend dependency installation uses the selected deterministic dependency
  strategy.
- CI installs backend dependencies using the same strategy documented for
  local development.
- Settings validation has tests for:
  - local/development behavior without a required database;
  - production-like behavior requiring a database URL;
  - explicit database-required mode;
  - redaction of secret settings;
  - invalid or unsupported environment values if implemented.
- Local API startup command remains documented and does not require live
  provider resources.
- Readiness problems remain structured and non-secret.

## 7. Security and Privacy Requirements

- No secrets, `.env` files, provider tokens, database URLs, API keys, OAuth
  credentials, or generated local database files may be committed.
- Secret values must not appear in logs, errors, tests, fixtures, or docs.
- CI must not require production provider secrets.
- Runtime validation must fail safely when required configuration is missing.
- Documentation examples must use placeholder values only.

## 8. Verification Plan

The implementation PR must include evidence for:

- `git diff --check`
- strict secret-pattern scan over changed files
- backend dependency install from a clean environment or documented equivalent
- `apps/api/.venv/bin/python -m pytest apps/api`
- `apps/api/.venv/bin/python -m ruff check apps/api`
- `apps/api/.venv/bin/python -m mypy apps/api/src`
- Alembic upgrade/downgrade smoke validation from `apps/api`
- `npm run typecheck`
- `npm run lint`
- `npm test`
- `npm run build`
- GitHub CI passing

If a check cannot run locally, the PR must record the exact command, failure
reason, compensating evidence, and whether the blocker must stop the PR.

## 9. Acceptance Criteria

WO-017 is complete only when:

- this Work Order is accepted by the repository maintainer;
- the backend dependency strategy is documented and implemented;
- local and CI backend install paths are aligned;
- backend command documentation is current;
- runtime settings validation is more explicit and tested;
- no live provisioning, deployment automation, production secrets, migrations,
  auth behavior, queue, scheduler, webhook hardening, or API expansion is
  introduced;
- required local checks and GitHub CI pass;
- a review or implementation report records scope, validation, residual risks,
  and the next recommended Work Order;
- the branch merges through the approved pull-request process.

## 10. Stop-and-Ask Triggers

The implementing agent must stop and ask before proceeding if:

- dependency hardening requires adopting a new package manager, lockfile tool,
  or workflow that materially changes backend development;
- the task requires live provider resources or production secrets;
- dependency resolution requires upgrading a major framework or replacing an
  accepted tool;
- settings validation would require changing infrastructure, authentication,
  authorization, database schema, or deployment architecture;
- CI changes require provider credentials or deployment permissions;
- implementation reveals that WO-018 PostgreSQL environment work must happen
  first;
- unrelated user changes overlap with required files;
- a destructive action is needed.

## 11. Review Notes

This Work Order is proposed for review. It does not authorize implementation
until accepted by the repository maintainer.
