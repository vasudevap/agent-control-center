# ES-008 - Hosted MVP Production Cutover

**Status:** Accepted
**Owner:** Repository Maintainer
**Review Owner:** Repository Maintainer
**Date:** 2026-07-19
**Version:** 1.0
**Accepted:** 2026-07-19 by Repository Maintainer
**Implementation Authorization:** Granted for WO-053 through WO-060, including WO-056A, under ADP-005
**Target Release:** Hosted MVP production cutover
**Related Phase:** Post-Phase 7 hosted production cutover
**Prerequisite Engineering Specification:** `docs/engineering-specifications/ES-007-operational-mvp-release-readiness.md`
**Related Work Orders:** `docs/work-orders/053-production-environment-and-secrets-provisioning.md` through `docs/work-orders/060-release-tag-and-production-closeout.md`, including `docs/work-orders/056a-grafley-custom-domain-cutover.md`
**Governing Plan:** `docs/implementation-plans/hosted-production-cutover-work-order-backlog.md`
**ADR Assessment:** `docs/implementation-plans/hosted-production-cutover-adr-assessment.md`
**Autonomous Delivery Program:** `docs/implementation-plans/ADP-005-hosted-mvp-production-cutover.md`
**Review Record:** `docs/reviews/ES-008-hosted-mvp-production-cutover-review.md`

---

## 1. Purpose

Define the governed cutover scope that takes the accepted MVP release candidate
from repository evidence to an online, single-owner hosted deployment on the
accepted Netlify frontend and Render API/PostgreSQL path.

ES-008 is intentionally a production-cutover specification. Repository
Maintainer acceptance on 2026-07-19 authorizes bounded implementation under
WO-053 through WO-060 and ADP-005. Maintainer acceptance on 2026-07-20 adds
WO-056A for Grafley custom-domain cutover before OAuth finalization. It does
not authorize broader product scope, public launch, enterprise readiness,
multi-user operation, broader Google scopes, or Phase 8 implementation.

## 2. Target Outcome

After ES-008 is accepted and implemented:

- the Atlas web dashboard is deployed on Netlify;
- the Atlas API and PostgreSQL database are provisioned on Render;
- the accepted Grafley product domains are active or explicitly deferred:
  `https://atlas.grafley.com` and `https://api.atlas.grafley.com`;
- production-like environment variables and secrets are configured in provider
  dashboards without committing secret values;
- Google OAuth redirect URIs and client settings match the deployed URLs;
- migrations run against the hosted database after backup and rollback
  expectations are confirmed;
- hosted health, readiness, dashboard smoke, and Gmail/Drive connector checks
  pass;
- rollback and release-withdrawal paths are rehearsed or dry-reviewed;
- a final go/no-go decision either approves the hosted MVP cutover or records
  deferral/rejection with reasons;
- if approved separately, the verified commit can be tagged according to
  release-management rules.

## 3. Governing References

ES-008 is governed by:

- `AGENTS.md`
- `PROJECT.md`
- `docs/governance/release-management.md`
- `docs/architecture/06-deployment-architecture.md`
- `docs/architecture/07-security-architecture.md`
- `docs/architecture/08-data-architecture.md`
- `docs/architecture/10-connector-framework.md`
- `docs/architecture/11-observability.md`
- `docs/implementation-plans/infrastructure-provisioning-strategy.md`
- `docs/implementation-plans/phase-7-deployment-and-migration-readiness.md`
- `docs/implementation-plans/phase-7-environment-configuration-and-secrets-readiness.md`
- `docs/implementation-plans/phase-7-release-runbooks-and-rollback.md`
- `docs/reviews/WO-051-mvp-release-candidate-validation-report.md`
- `docs/reviews/WO-052-mvp-acceptance-and-phase-7-closeout-report.md`
- canonical engineering governance under `docs/governance/`

If cutover pressure conflicts with these references, implementation stops for
an updated Work Order, ADR, or maintainer decision.

## 4. Entry Evidence

| Evidence | Status |
| --- | --- |
| Phase 7 release candidate accepted | Complete under WO-052 |
| Controlled Gmail/Drive evidence | Complete under WO-045 |
| Release candidate validation | Complete under WO-051 |
| Deployment readiness plan | Complete under WO-048 |
| Runbooks and rollback | Complete under WO-050 |
| Production deployment | Netlify and Render provider deployments performed under WO-054 and WO-055; public launch and release tag remain pending |
| Release tag | Not created |
| Hosted environment URLs | Provider-generated Netlify and Render URLs exist; Grafley custom domains accepted with provider CNAME targets pending WO-056A |
| Production secrets | Provider-native Render database and signing values configured; Google OAuth values remain pending; no secret values stored in source |

## 5. Proposed Scope

### 5.1 Production environment and secrets provisioning

- Define exact Netlify and Render environment variables.
- Configure provider-native secrets only after explicit authority.
- Verify redaction, fail-closed readiness, and secret-rotation expectations.
- Do not record secret values in Git, logs, screenshots, PRs, or chat.

### 5.2 Netlify frontend deployment

- Configure the accepted frontend build command and publish path.
- Configure `NEXT_PUBLIC_API_BASE_URL` to the accepted hosted API URL.
- Verify dashboard render, runtime health indicator, and static route output.
- Preserve rollback to previous Netlify deploy.

### 5.3 Render API and PostgreSQL deployment

- Provision or configure the accepted API service and PostgreSQL database.
- Configure Python/runtime/build/start commands.
- Verify `/health/live` and `/health/ready` behavior.
- Confirm logs do not expose secrets, tokens, or full email bodies.

### 5.4 Grafley custom-domain cutover

- Configure `atlas.grafley.com` for the Netlify dashboard.
- Configure `api.atlas.grafley.com` for the Render API.
- Capture provider CNAME target values for Repository Maintainer DNS
  provisioning.
- Verify DNS, TLS, frontend-to-API runtime behavior, and rollback references
  before finalizing Google OAuth redirect URIs when feasible.

### 5.5 Google OAuth production client and redirects

- Configure Gmail and Drive OAuth redirect URIs for the hosted API.
- Preserve the accepted `gmail.modify` and `drive.file` scope posture.
- Do not request `https://mail.google.com/` or broader Drive scopes.
- Verify OAuth behavior only with the authorized owner account.

### 5.6 Migration, backup, restore, and cutover rehearsal

- Confirm a database backup exists or backup path is available before
  migrations.
- Run Alembic migrations against the hosted database only after explicit
  migration authority.
- Record migration head and rollback/corrective-forward options.

### 5.7 Hosted smoke testing and monitoring

- Verify hosted frontend, API, readiness, owner sign-in, connector health,
  manual run path, audit/log signals, and owner alert expectations.
- Use synthetic messages/files only unless a later Work Order explicitly
  authorizes broader live data.
- Record minimized evidence only.

### 5.8 Rollback rehearsal and release withdrawal

- Dry-review or rehearse Netlify rollback, Render service rollback,
  migration recovery, OAuth revocation, Drive cleanup, and release withdrawal.
- Do not move or rewrite tags.
- Do not rely on application rollback as database rollback.

### 5.9 Go/no-go, release tag, and closeout

- Record the maintainer go/no-go decision.
- If approved, document whether a release tag is authorized.
- Create a tag only if the Work Order explicitly authorizes it.
- Close ADP-005 with hosted URLs, validation evidence, rollback posture, and
  residual risk disposition.

## 6. Explicitly Out of Scope

ES-008 does not authorize:

- deployment action outside accepted WO-053 through WO-060, including WO-056A,
  and ADP-005 authority;
- production deployment without explicit provider/action authority;
- release tagging without explicit tag authority;
- production mailbox use;
- public launch or marketing announcement;
- multi-user, RBAC, tenancy, or enterprise readiness;
- broader Google OAuth scopes;
- new hosting, database, monitoring, or secrets providers without ADR review;
- new agent capability, Phase 8 implementation, or workflow-framework adoption;
- storing secrets, OAuth tokens, full Gmail bodies, PHI, clinical content, or
  unrestricted attachment copies in source, logs, screenshots, fixtures, or
  PRs.

## 7. Proposed Work Order Set

| Work Order | Name | Purpose |
| --- | --- | --- |
| WO-053 | Production Environment and Secrets Provisioning | Configure provider-native env/secrets without exposing values. |
| WO-054 | Netlify Frontend Deployment | Deploy and verify the web dashboard on Netlify. |
| WO-055 | Render API and PostgreSQL Deployment | Deploy API service and database on Render. |
| WO-056A | Grafley Custom Domain Cutover | Configure accepted Grafley product domains and DNS handoff before OAuth finalization. |
| WO-056 | Google OAuth Production Client and Redirects | Configure hosted OAuth redirect behavior with accepted scopes. |
| WO-057 | Hosted Migration, Backup, and Restore Readiness | Execute or rehearse hosted migration with backup/rollback evidence. |
| WO-058 | Hosted Smoke Tests and Monitoring Confirmation | Validate hosted app, health, connector, audit, and monitoring signals. |
| WO-059 | Production Rollback and Release Withdrawal Rehearsal | Confirm rollback and provider cleanup paths before go/no-go. |
| WO-060 | Release Tag and Production Closeout | Record go/no-go, optional tag authority, hosted URLs, and closeout. |

## 8. Acceptance Criteria

ES-008 is complete only when:

- ES-008, WO-053 through WO-060, WO-056A, and ADP-005 acceptance is recorded
  before deployment action begins;
- all accepted Work Orders are implemented, validated, reviewed, and merged;
- provider-side configuration evidence is recorded without leaking secrets;
- hosted frontend and API health checks pass;
- migrations are verified at the current Alembic head;
- OAuth redirects work with accepted scopes and authorized account boundaries;
- smoke tests and monitoring checks pass;
- rollback and release-withdrawal paths are reviewed;
- the maintainer records a go/no-go decision;
- release tag and production URL publication occur only if explicitly
  authorized.

## 9. Validation Expectations

Final cutover validation must include:

- GitHub CI on each cutover PR;
- local release validation before provider changes;
- Netlify deploy evidence and dashboard smoke evidence;
- Render API health/readiness evidence;
- PostgreSQL migration head evidence;
- Google OAuth redirect and connector-health evidence;
- Gmail/Drive synthetic workflow evidence if authorized by the relevant Work
  Order;
- secret and log redaction scans;
- rollback and release-withdrawal checklist review.

## 10. Rollback Expectations

Rollback must cover:

- Netlify deploy rollback;
- Render service rollback;
- migration corrective-forward or restore path;
- OAuth credential revocation/rotation;
- Gmail/Drive cleanup for synthetic artifacts;
- release withdrawal communication inside the repository;
- no tag movement or history rewriting.

## 11. Stop-and-Ask Triggers

Stop and request Repository Maintainer direction before proceeding if:

- a required Work Order, provider action, or ADP-005 execution step is not
  authorized;
- a command would provision, deploy, migrate, tag, publish, revoke, rotate,
  delete, or expose production resources without explicit Work Order authority;
- provider dashboards require secret values to be shared in chat or source;
- Google requires broader scopes or external verification beyond accepted
  single-owner posture;
- required CI fails and the fix is outside the current Work Order;
- a production migration, rollback, restore, or release tag is ambiguous;
- a new architecture, security, deployment, data, monitoring, or framework
  decision is required.
