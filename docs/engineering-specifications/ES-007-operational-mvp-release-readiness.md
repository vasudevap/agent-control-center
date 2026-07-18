# ES-007 - Operational MVP Release Readiness

**Status:** Proposed - Review Required
**Owner:** Repository Maintainer
**Review Owner:** Repository Maintainer
**Date:** 2026-07-18
**Version:** 0.1
**Accepted:** Not accepted
**Implementation Authorization:** Not granted
**Target Release:** MVP release
**Related Phase:** Phase 7 - Operational MVP Release
**Prerequisite Engineering Specification:** `docs/engineering-specifications/ES-006-gmail-agent-mvp-candidate.md`
**Related Work Orders:** `docs/work-orders/045-controlled-account-release-verification.md` through `docs/work-orders/052-mvp-acceptance-and-phase-7-closeout.md`
**Governing Plan:** `docs/implementation-plans/phase-7-work-order-backlog.md`
**ADR Assessment:** `docs/implementation-plans/phase-7-adr-assessment.md`
**Autonomous Delivery Program:** `docs/implementation-plans/ADP-004-phase-7-operational-mvp-release.md`
**Review Record:** `docs/reviews/ES-007-operational-mvp-release-readiness-review.md`

---

## 1. Purpose

Define the Phase 7 readiness scope that converts the completed Gmail Agent MVP
Candidate into an operational MVP release candidate for normal single-owner
personal use.

ES-007 is intentionally a release-readiness specification. It does not itself
authorize production deployment, personal mailbox use, live credentials,
provider resource creation, or production cutover. Those actions require
Repository Maintainer acceptance of this package and the explicit authority
called out in the applicable Work Order.

## 2. Phase 7 Outcome

After ES-007 is accepted and implemented:

- the Phase 6 Gmail Agent candidate has controlled-account or explicitly
  accepted substitute evidence;
- the dashboard supports the normal single-owner operational workflow without
  fixture-only behavior for MVP-critical surfaces;
- configuration, secrets, OAuth clients, environment variables, migrations, and
  backup/restore expectations are documented before live use;
- Netlify and Render deployment readiness is verified against the accepted
  architecture without leaking secrets or skipping migration controls;
- health, readiness, logging, metrics, alerting, and manual recovery paths are
  sufficient for initial personal operation;
- runbooks and rollback procedures exist for credential revocation, failed
  sends, failed migrations, deployment rollback, and provider incidents;
- a final MVP release candidate validation proves the release boundary end to
  end;
- residual risks are reviewed and either resolved, deferred, or accepted by the
  Repository Maintainer before MVP acceptance.

## 3. Governing References

ES-007 is governed by:

- `AGENTS.md`
- `PROJECT.md`
- `ROADMAP.md`
- `docs/specifications/product-requirements.md`
- `docs/architecture/04-container-architecture.md`
- `docs/architecture/05-component-architecture.md`
- `docs/architecture/06-deployment-architecture.md`
- `docs/architecture/07-security-architecture.md`
- `docs/architecture/08-data-architecture.md`
- `docs/architecture/09-agent-runtime.md`
- `docs/architecture/10-connector-framework.md`
- `docs/architecture/11-observability.md`
- `docs/architecture/13-human-approvals.md`
- `docs/implementation-plans/infrastructure-provisioning-strategy.md`
- `docs/implementation-plans/mvp-release-boundary-and-phase-gates.md`
- `docs/engineering-specifications/ES-006-gmail-agent-mvp-candidate.md`
- `docs/reviews/WO-044-gmail-agent-mvp-candidate-closeout-report.md`
- `docs/reviews/WO-044-controlled-account-test-plan.md`
- canonical engineering governance under `docs/governance/`

If release pressure conflicts with these references, implementation stops for
an updated Work Order, ADR, or maintainer release decision.

## 4. Entry Evidence

Phase 7 starts from the following repository state:

| Evidence | Status |
| --- | --- |
| Phase 5 generic agent/governance contracts | Completed and merged |
| Phase 6 Gmail Agent MVP Candidate | Completed and merged under ADP-003 |
| Deterministic fake-provider Gmail MVP evidence | Complete |
| Controlled-account plan | Prepared, not executed |
| Production release authority | Not granted |
| Personal mailbox use | Not authorized |
| Dashboard productization | Deferred from Phase 6 |
| Live provider API quirks | Not proven |
| Load, chaos, long-running scheduler evidence | Deferred to Phase 7 readiness |

## 5. Proposed Scope

### 5.1 Controlled-account release verification

- Execute the existing controlled-account plan only after explicit maintainer
  authorization.
- Use synthetic messages and controlled Google resources only.
- Record seed data, execution evidence, cleanup evidence, provider findings,
  and any Work Order changes required before release.
- Preserve the no-personal-mailbox and no-production-mailbox boundary.

### 5.2 Dashboard and operational workflow readiness

- Productize MVP-critical dashboard surfaces for single-owner operation:
  agents, connector state, manual run, scheduled run status, held messages,
  questions, draft evidence, approvals, send outcomes, audit, logs, and health.
- Replace or clearly quarantine fixture-only behavior for MVP-critical paths.
- Preserve existing design-system and accessibility standards.

### 5.3 Environment, configuration, and secrets readiness

- Document required environment variables, owner-only configuration, OAuth
  client setup, secret ownership, rotation, revocation, and redaction checks.
- Verify startup fails closed when required configuration is absent or unsafe.
- Confirm logs, APIs, webhooks, fixtures, and audit payloads do not expose
  tokens, secrets, full Gmail bodies, clinical content, or PHI.

### 5.4 Deployment and migration readiness

- Verify the approved Netlify and Render path, build commands, runtime
  settings, service boundaries, database migration procedure, backup/restore
  expectations, and rollback notes.
- Perform dry-run or non-production verification before any production cutover.
- Document any manual provider-dashboard steps that cannot safely live in
  source.

### 5.5 Monitoring, health, and recovery readiness

- Define MVP health/readiness checks, scheduler/queue visibility, log fields,
  audit coverage, metric signals, alert thresholds, and owner notification
  expectations.
- Add or validate recovery paths for stuck runs, indeterminate sends, provider
  throttling, webhook delivery issues, failed drafts, failed migrations, and
  revoked credentials.

### 5.6 Runbooks and rollback

- Create operator runbooks for deployment, smoke tests, controlled-account use,
  Gmail OAuth revocation, Drive cleanup, migration rollback, deployment
  rollback, incident triage, and release withdrawal.
- Ensure rollback does not rely on application rollback alone for data or
  provider side effects.

### 5.7 Release candidate validation and acceptance

- Run the full local validation suite, GitHub CI, migration checks,
  security/privacy scans, fake-provider E2E tests, controlled-account evidence
  if authorized, and dashboard verification.
- Produce a release candidate report and Phase 7 closeout record with residual
  risk disposition.

## 6. Explicitly Out of Scope

ES-007 does not authorize:

- personal mailbox use;
- production mailbox use before explicit MVP release authority;
- production OAuth client use before explicit release authority;
- unrestricted mailbox scanning or full mailbox replication;
- automatic sends, permanent deletes, forwards, unsubscribes, or external
  sharing without approval;
- clinical or PHI drafting, approvals, questions, actions, or learning;
- live external webhook receivers unless a Work Order explicitly accepts them;
- multi-user, RBAC, tenancy, delegation, quorum, multiple reviewers, or
  multiple external product clients;
- new orchestration frameworks such as LangChain, LangGraph, or Temporal;
- a new hosting provider, secrets manager, database provider, or monitoring
  vendor without ADR review when required;
- public launch, enterprise readiness, or Google verification for a broader
  user population.

## 7. Proposed Work Order Set

| Work Order | Name | Purpose |
| --- | --- | --- |
| WO-045 | Controlled-Account Release Verification | Execute or explicitly defer controlled-account evidence before release. |
| WO-046 | Dashboard Productization and Runtime Operations | Make MVP-critical operator workflows usable against real contracts. |
| WO-047 | Environment Configuration and Secrets Readiness | Lock required config, OAuth setup, redaction, rotation, and fail-closed startup. |
| WO-048 | Deployment Path and Migration Readiness | Verify Netlify/Render readiness, migration procedure, backup/restore, and rollback. |
| WO-049 | Monitoring, Health, and Recovery Readiness | Establish MVP operational signals and manual recovery paths. |
| WO-050 | Release Runbooks and Rollback | Produce operator runbooks for deployment, incidents, provider cleanup, and withdrawal. |
| WO-051 | MVP Release Candidate Validation | Run final evidence suite and produce release candidate report. |
| WO-052 | MVP Acceptance and Phase 7 Closeout | Record release decision, residual risks, and post-MVP boundary. |

## 8. Acceptance Criteria

Phase 7 is complete only when:

- ES-007, WO-045 through WO-052, and ADP-004 are accepted;
- all accepted Work Orders are implemented, validated, reviewed, and merged;
- required CI is green on each release-readiness pull request;
- controlled-account evidence is either executed with cleanup evidence or
  explicitly deferred with accepted residual risk;
- dashboard MVP-critical workflows are not fixture-only;
- secrets and OAuth token values are absent from committed files, logs, APIs,
  webhooks, audit payloads, and fixtures;
- migration, backup, restore, and rollback expectations are documented and
  tested to the extent accepted for MVP;
- health, readiness, monitoring, alerting, and manual recovery paths are
  adequate for single-owner operation;
- the release candidate report identifies known issues and residual risks;
- the Repository Maintainer makes an explicit MVP release decision.

## 9. Validation Expectations

Each Work Order must define its own focused validation. The final release
candidate validation must include, at minimum:

- full backend tests;
- frontend validation for touched dashboard surfaces;
- lint, typecheck, and build commands required by CI;
- Alembic migration verification at the current head;
- Gmail fake-provider end-to-end verification;
- redaction and secret scans over touched source and fixtures;
- controlled-account execution evidence if separately authorized;
- deployment dry-run or provider status evidence for the accepted environment;
- runbook and rollback checklist review.

## 10. Rollback Expectations

Phase 7 rollback must cover source, data, provider, and deployment concerns:

- source rollback uses reviewed revert or corrective forward change;
- release tags are never moved;
- deployment rollback uses Netlify and Render provider rollback mechanisms
  documented in WO-050;
- database rollback includes backup/restore awareness and migration-specific
  notes;
- Gmail/Drive rollback includes revocation and cleanup of controlled resources;
- indeterminate sends are reconciled manually and never retried blindly;
- credentials are rotated or revoked when exposure is suspected.

## 11. Stop-and-Ask Triggers

Stop and request Repository Maintainer direction before proceeding if:

- ES-007, a Work Order, or ADP-004 is not accepted;
- implementation requires live Gmail, Drive, OAuth, Netlify, Render, database,
  webhook, or monitoring credentials outside an accepted Work Order boundary;
- a personal mailbox or production mailbox is requested;
- Google requires broader OAuth scopes, verification, security assessment, or
  behavior changes before MVP use;
- implementation would store full Gmail bodies, OAuth token values, secrets,
  clinical content, PHI, or unrestricted attachment copies;
- implementation would weaken suppression, approval gates, audit, redaction,
  authorization, idempotency, or fail-closed revalidation;
- deployment topology, provider choice, environment count, secrets ownership,
  database provider, or monitoring vendor changes require an ADR;
- required CI fails and the fix is not a narrow in-scope correction;
- residual risk cannot be accepted safely for normal single-owner operation.
