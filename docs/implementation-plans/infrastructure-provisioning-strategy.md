# Infrastructure Provisioning Strategy

**Status:** Completed - Review Pending Merge
**Owner:** Repository Maintainer
**Date:** 2026-07-17
**Governing Work Order:** [WO-016 Infrastructure Provisioning and Environment Strategy](../work-orders/016-infrastructure-provisioning-and-environment-strategy.md)
**Implementation Authorization:** Not Granted
**Live Provisioning Authorization:** Not Granted

---

## 1. Decision Summary

Atlas will retain the accepted hosting target:

| Layer | Planned platform |
| --- | --- |
| Dashboard | Netlify |
| Backend API | Render Web Service |
| Background workers | Render Background Workers |
| Scheduler | Render Cron Job |
| Runtime database | Render PostgreSQL |
| Initial queue | PostgreSQL-backed queue |
| Source control and CI | GitHub |
| Notion provisioner | Local developer machine initially |

Preferred provisioning approach:

1. **No live provisioning during WO-016.**
2. **No top-level `infrastructure/` directory yet.**
3. **Use provider-native configuration when live provisioning is later
   authorized:**
   - Render Blueprint for Render services, Render PostgreSQL, Render Cron,
     Render Background Workers, and Render environment groups.
   - Netlify monorepo/site configuration for the dashboard.
4. **Defer Terraform and Pulumi** until Atlas needs cross-provider orchestration,
   reusable modules, policy-as-code, drift management beyond provider-native
   controls, or multiple independently managed environments.
5. **Require a later accepted provisioning Work Order** before adding
   `render.yaml`, `netlify.toml`, live provider resources, production secrets,
   or deployment automation.

ADR requirement:

- No ADR is required for this WO-016 strategy because it preserves the accepted
  Netlify + Render + Render PostgreSQL architecture.
- A future ADR is required before changing provider topology, replacing Render
  PostgreSQL, adopting Terraform or Pulumi as the primary infrastructure
  authority, or introducing a new persistent infrastructure platform.
- A future deployment/provisioning Work Order may authorize Render Blueprint and
  Netlify configuration files because those operationalize the already accepted
  provider architecture.

## 2. Current Architecture Baseline

Accepted architecture already selects:

- Netlify for dashboard hosting.
- Render for backend API, workers, scheduler, and database hosting.
- Render PostgreSQL as the hosted PostgreSQL target.
- PostgreSQL as the runtime system of record.
- PostgreSQL-backed queue initially, with Redis-compatible infrastructure
  deferred unless a later ADR accepts it.
- Production deployment requiring explicit approval.

WO-016 does not change those decisions.

## 3. Provider Documentation Reviewed

Official provider documentation reviewed on 2026-07-17:

- Render Blueprints infrastructure-as-code:
  <https://render.com/docs/infrastructure-as-code>
- Render Blueprint YAML reference:
  <https://render.com/docs/blueprint-spec>
- Render environment variables and secret files:
  <https://render.com/docs/configure-environment-variables>
- Render PostgreSQL create/connect guidance:
  <https://render.com/docs/postgresql-creating-connecting>
- Render PostgreSQL recovery and backups:
  <https://render.com/docs/postgresql-backups>
- Render service types:
  <https://render.com/docs/service-types>
- Render private network:
  <https://render.com/docs/private-network>
- Netlify monorepo deployment configuration:
  <https://docs.netlify.com/build/configure-builds/monorepos/>
- Netlify deploy contexts:
  <https://docs.netlify.com/deploy/deploy-overview/>
- Netlify environment variables:
  <https://docs.netlify.com/build/environment-variables/overview/>

Key provider facts used:

- Render Blueprints use a repository YAML file, commonly `render.yaml`, to
  manage interconnected services, databases, and environment groups.
- Render Blueprint files can define Render PostgreSQL databases and reference
  database connection strings from services with Blueprint environment variable
  references.
- Render warns not to commit secret values in Blueprint files; secret values
  should use dashboard-provided values or non-synced placeholders.
- Render services should use internal database URLs when the service and
  database are in the same account and region.
- Paid Render PostgreSQL databases support point-in-time recovery; free
  instances do not provide recovery capabilities.
- Netlify supports monorepo site configuration, including package directory,
  base directory, build command, and publish directory.
- Netlify deploy contexts allow different production, deploy-preview,
  branch-deploy, preview-server, and local development behavior.
- Netlify recommends storing sensitive environment variables in the Netlify UI,
  CLI, or API rather than committing sensitive values to repository
  configuration.

## 4. Provisioning Option Matrix

| Option | Decision | Why |
| --- | --- | --- |
| Manual provider dashboard runbook | Allowed for initial account/site creation only | Useful when a one-time provider setup step cannot be represented safely in source, but not enough as the long-term source of repeatable runtime configuration. |
| Render Blueprint | Preferred for later Render provisioning | Provider-native, lightweight, supports Render services, databases, cron jobs, workers, and environment groups without adopting a broader IaC stack. |
| Netlify monorepo/site configuration | Preferred for later dashboard deployment | Aligns with the current monorepo and Netlify’s documented package/base/build/publish model. |
| Terraform | Deferred | More power than Atlas currently needs; revisit when cross-provider resources, stronger drift workflows, policy-as-code, or reusable environment modules become necessary. |
| Pulumi | Deferred | Similar deferral rationale to Terraform; revisit if TypeScript/Python-based infrastructure programming becomes valuable enough to justify the toolchain. |
| No documented provisioning mechanism | Rejected | Conflicts with the project’s plan-before-build governance. |

## 5. Environment Model

| Environment | Purpose | Provider location | Data | Deployment expectation |
| --- | --- | --- | --- | --- |
| Local | Developer iteration, local validation, migration development | Developer machine | Fake or developer-owned non-production data only | No live provider provisioning required. |
| Test / CI | Automated tests and migration validation | GitHub Actions with ephemeral PostgreSQL service when authorized by WO-018 | Synthetic test data only | Created and destroyed per run. No provider secrets. |
| Development | Hosted integration environment after live provisioning is authorized | Netlify + Render project/environment | Non-production synthetic or scrubbed data only | Used for integration smoke checks before production. |
| Staging | Deferred | Not provisioned now | Not applicable | Revisit when production workflows, multiple operators, or external-client integration risk require a separate pre-production environment. |
| Production | Explicitly approved live operating environment | Netlify + Render project/environment | Real operational data | Requires separate production deployment approval. |

Promotion order:

1. Local validation.
2. CI validation.
3. Hosted development smoke validation once provisioned.
4. Production promotion only after explicit approval and rollback evidence.

Allowed fake/local behavior:

- Fake webhook transport is allowed in local and CI.
- Fake webhook transport is allowed in hosted development only for isolated
  smoke tests.
- Fake webhook transport is not allowed for production behavior unless a
  documented emergency/test exception is approved.

## 6. PostgreSQL Placement Matrix

| Environment | Database placement | Connection rule | Migration expectation |
| --- | --- | --- | --- |
| Local | Developer-managed PostgreSQL, preferably containerized or locally installed with the same major version selected for hosted Render PostgreSQL | Local `DATABASE_URL` in an uncommitted environment file or shell environment | Developers run Alembic upgrade/downgrade against local PostgreSQL before DB-related PRs. |
| Test / CI | Ephemeral PostgreSQL service created by CI when WO-018 adds PostgreSQL migration hardening | CI-only `DATABASE_URL` injected by the workflow | CI runs Alembic upgrade/downgrade against PostgreSQL-compatible service. |
| Development | Render PostgreSQL development instance after provisioning authorization | Render services use internal database URL when in the same account and region; maintainer tools may use external URL only when necessary | Migrations run through an approved deployment/migration command with rollback notes. |
| Production | Paid Render PostgreSQL production instance after explicit production authorization | Runtime services use internal database URL; external URL reserved for maintainer-admin operations | Migration execution requires backup/restore awareness, approval, and rollback plan. |

Database rules:

- PostgreSQL remains the system of record.
- SQLite may remain useful for narrow unit tests, but it must not be the only
  migration validation path after WO-018.
- Local and CI migration checks should move to PostgreSQL in WO-018.
- Render database URLs must never be committed.
- Production database restore should prefer provider-supported point-in-time
  recovery when available rather than destructive in-place restore.
- Free or disposable database tiers must not store durable production or
  sensitive operational data.

## 7. Secrets and Configuration Ownership

| Location | Owner | Allowed contents | Rules |
| --- | --- | --- | --- |
| Local developer shell / ignored local env file | Maintainer | Local-only non-production values | Never commit `.env` files or real secrets. |
| GitHub Actions secrets / variables | Maintainer | CI-only tokens and test configuration if later needed | Prefer no provider production secrets in CI until deployment automation is explicitly authorized. |
| Netlify site/team environment variables | Maintainer | Dashboard build/runtime configuration | Use deploy contexts; mark sensitive values appropriately; do not commit secret values to Netlify config files. |
| Render service environment variables and environment groups | Maintainer | Backend runtime configuration, generated app secrets, database references, webhook secrets | Prefer Blueprint references or dashboard-provided non-synced values for secrets; do not commit secret values. |
| Repository configuration files | Maintainer through PR review | Non-secret build/provisioning shape only | Secret placeholders are allowed only when clearly non-secret. |

Dedicated secrets manager:

- Deferred.
- Revisit when Atlas stores or rotates multiple provider credentials, supports
  more than one operator, introduces multiple external product clients, or
  needs centralized audit and rotation beyond Netlify/Render/GitHub controls.

## 8. Backup, Restore, Retention, and Rollback

Development:

- Development data is disposable unless explicitly marked otherwise.
- Backups are optional for development until real external-client integration
  or non-reproducible test data exists.

Production:

- Use a paid Render PostgreSQL plan with provider recovery support before any
  real production data is stored.
- Confirm recovery window, backup/export process, and restore procedure before
  production promotion.
- Treat destructive operations as privileged actions requiring explicit
  maintainer approval.
- Prefer restore into a separate recovery database, validate it, then redirect
  services if appropriate.
- Record migration rollback notes for each schema-changing PR.

Application rollback:

- Netlify and Render service rollback procedures must be documented in the
  future provisioning/deployment Work Order.
- Database rollback must not rely on application rollback alone.
- Backward-compatible migrations are preferred.

Retention:

- Keep only operationally required data.
- Do not store full email bodies, OAuth token plaintext, or prohibited
  knowledge values.
- Production retention policies remain future work for Phase 5/6 data
  contracts.

## 9. Provider Access Controls

Minimum expectations before live production provisioning:

- MFA enabled on GitHub, Netlify, and Render accounts.
- Least-privilege access for any collaborator account.
- Production deployment actions restricted to the maintainer unless delegated
  explicitly.
- Render database administration treated as privileged.
- Netlify production deploy settings protected from accidental branch or
  context changes.
- GitHub branch protection and required CI remain in force.

Provider resources should be named generically around Atlas / Agent Control
Center, not MushingMule-specific terminology.

## 10. Repository Structure Decision

Decision:

- Do not introduce a top-level `infrastructure/` directory during WO-016.

Rationale:

- The current preferred approach is provider-native configuration rather than a
  general IaC stack.
- Render expects Blueprint YAML in the repository, commonly at the root.
- Netlify monorepo guidance supports site-specific configuration near the site
  package.
- A top-level `infrastructure/` directory becomes useful if Atlas later adopts
  Terraform, Pulumi, shared deployment modules, or environment manifests that
  outgrow provider-native files.

Revisit trigger:

- Adopt `infrastructure/` when Terraform/Pulumi is accepted, when provider
  configuration grows beyond provider-native files, or when multiple products
  or environments require reusable provisioning modules.

## 11. Future Work Order Prerequisites

WO-017 - Backend Runtime and Dependency Hardening:

- May continue without live provisioning.
- Must preserve environment-based configuration.
- Must not assume committed secrets or provider-created database URLs.

WO-018 - PostgreSQL Environment and Migration Hardening:

- Should implement local and CI PostgreSQL migration validation.
- Should document the selected local PostgreSQL setup command.
- Should avoid provisioning hosted Render PostgreSQL unless a later
  provisioning Work Order authorizes it.

Future provisioning/deployment Work Order:

- May add `render.yaml` and Netlify configuration files.
- May create live development resources.
- Must not create production resources without explicit production
  authorization.
- Must include provider-account, region, tier, backup, restore, migration, and
  rollback evidence.

## 12. ADR Assessment

No new ADR is required to complete WO-016 because this strategy preserves
accepted architecture and records operational planning detail.

Create a proposed ADR before implementation if future work:

- changes Netlify dashboard hosting;
- changes Render backend hosting;
- changes Render PostgreSQL as the initial hosted database target;
- adopts Terraform or Pulumi as the primary provisioning authority;
- introduces a new secrets manager;
- introduces a new persistent queue service before PostgreSQL-backed queue
  requirements are exhausted;
- creates a multi-environment or multi-product infrastructure model that
  changes the single-owner/single-client architecture assumptions.

## 13. Residual Risks

| Risk | Treatment |
| --- | --- |
| Provider-native tooling may be less portable than Terraform/Pulumi. | Accepted for MVP simplicity; revisit when portability or cross-provider orchestration matters. |
| Manual steps may still exist for initial account/site setup. | Require a future runbook and review evidence before live provisioning. |
| Render Blueprint adoption can still cause configuration drift if dashboard changes bypass source. | Future provisioning Work Order should define source-of-truth and drift-review rules. |
| Production backup details depend on selected paid plan. | Do not store real production data until recovery capability is confirmed. |
| Local PostgreSQL setup may vary by developer machine. | WO-018 should standardize the local/test PostgreSQL path and fallback documentation. |

## 14. Review Outcome

This strategy is ready for review under WO-016. It does not authorize live
provisioning, production deployment, provider resource creation, application
code changes, migrations, or secret handling.
