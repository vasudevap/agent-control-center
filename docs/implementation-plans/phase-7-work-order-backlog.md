# Phase 7 Work Order Backlog

**Status:** Accepted - Phase 7 Execution Authorized
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Engineering Specification:** `docs/engineering-specifications/ES-007-operational-mvp-release-readiness.md`
**ADR Assessment:** `docs/implementation-plans/phase-7-adr-assessment.md`
**Implementation Authorization:** Granted for WO-045 through WO-052 under ADP-004

---

## 1. Purpose

Define the proposed Work Order sequence for Phase 7 Operational MVP Release
Readiness.

This backlog records the accepted Work Order sequence for Phase 7 Operational
MVP Release Readiness. Each Work Order remains the bounded implementation
authority for its own scope, exclusions, validation, rollback expectations, and
stop-and-ask triggers.

## 2. Work Order Map

| Work Order | Name | Depends On | Parallelizable | Status |
| --- | --- | --- | --- | --- |
| WO-045 | Controlled-Account Release Verification | ES-007 accepted, WO-044 closeout | Limited | Accepted - Pending Implementation |
| WO-046 | Dashboard Productization and Runtime Operations | ES-007 accepted, WO-043 contracts | Yes | Accepted - Pending Implementation |
| WO-047 | Environment Configuration and Secrets Readiness | ES-007 accepted, WO-036, WO-044 | Limited | Implemented - Pending PR Review |
| WO-048 | Deployment Path and Migration Readiness | WO-047 readiness draft | Limited | Implemented - Pending PR Review |
| WO-049 | Monitoring, Health, and Recovery Readiness | WO-043, WO-047 | Yes | Implemented - Pending PR Review |
| WO-050 | Release Runbooks and Rollback | WO-047, WO-048, WO-049 | Limited | Accepted - Pending Implementation |
| WO-051 | MVP Release Candidate Validation | WO-045 through WO-050 | No | Accepted - Pending Implementation |
| WO-052 | MVP Acceptance and Phase 7 Closeout | WO-051 | No | Accepted - Pending Implementation |

## 3. Dependency Waves

| Wave | Work Orders | Purpose | Parallel posture |
| --- | --- | --- | --- |
| Wave 0 | ES-007, ADR assessment, WO review, ADP-004 acceptance | Governance readiness | Documentation review can happen in parallel; implementation waits |
| Wave 1 | WO-045, WO-046, WO-047 | Provider evidence, dashboard readiness, and configuration/secrets readiness | Controlled-account execution is gated by explicit authorization; dashboard and config docs can proceed in parallel |
| Wave 2 | WO-048, WO-049 | Deployment/migration readiness and operational signals | Can proceed after configuration assumptions are stable |
| Wave 3 | WO-050 | Runbooks and rollback | Uses deployment and monitoring findings |
| Wave 4 | WO-051 | Release candidate validation | Serial final evidence package |
| Wave 5 | WO-052 | MVP acceptance and Phase 7 closeout | Serial maintainer release decision |

## 4. Proposed Work Orders

### WO-045 - Controlled-Account Release Verification

Work Order:

- `docs/work-orders/045-controlled-account-release-verification.md`

Objective:

- Execute the WO-044 controlled-account test plan if explicitly authorized, or
  record a maintainer-accepted deferral before release candidate validation.

### WO-046 - Dashboard Productization and Runtime Operations

Work Order:

- `docs/work-orders/046-dashboard-productization-and-runtime-operations.md`

Objective:

- Productize MVP-critical single-owner dashboard workflows against real backend
  contracts for agents, runs, connectors, approvals, questions, held messages,
  outcomes, logs, audit, and health.

### WO-047 - Environment Configuration and Secrets Readiness

Work Order:

- `docs/work-orders/047-environment-configuration-and-secrets-readiness.md`

Objective:

- Define and verify required environment variables, OAuth client setup,
  provider-native secret storage, redaction, revocation, rotation, and
  fail-closed configuration behavior.

### WO-048 - Deployment Path and Migration Readiness

Work Order:

- `docs/work-orders/048-deployment-path-and-migration-readiness.md`

Objective:

- Verify the accepted Netlify/Render deployment path, build/runtime settings,
  migration procedure, backup/restore expectations, and rollback evidence
  before production cutover.

### WO-049 - Monitoring, Health, and Recovery Readiness

Work Order:

- `docs/work-orders/049-monitoring-health-and-recovery-readiness.md`

Objective:

- Establish MVP health, readiness, log, metric, alert, scheduler, queue,
  webhook, provider-error, and manual recovery expectations.

### WO-050 - Release Runbooks and Rollback

Work Order:

- `docs/work-orders/050-release-runbooks-and-rollback.md`

Objective:

- Produce operator runbooks and rollback procedures for deployment, migration,
  OAuth revocation, Drive cleanup, provider incidents, indeterminate sends, and
  release withdrawal.

### WO-051 - MVP Release Candidate Validation

Work Order:

- `docs/work-orders/051-mvp-release-candidate-validation.md`

Objective:

- Run the final release candidate evidence suite and produce the MVP release
  candidate validation report.

### WO-052 - MVP Acceptance and Phase 7 Closeout

Work Order:

- `docs/work-orders/052-mvp-acceptance-and-phase-7-closeout.md`

Objective:

- Record the maintainer release decision, residual risk disposition, accepted
  MVP boundary, and post-MVP entry conditions.

## 5. Stop-and-Ask Triggers

Stop before implementation if:

- ES-007, ADP-004, or the relevant Work Order is not accepted;
- live credentials, live provider resources, production deployment, production
  database access, or controlled-account execution are required without
  explicit authorization;
- a personal mailbox or production mailbox is requested;
- provider requirements force broader OAuth scopes or changed Gmail behavior;
- implementation would store full Gmail bodies, OAuth tokens, secrets,
  clinical content, PHI, or unrestricted attachment copies;
- implementation would weaken clinical/PHI suppression, approval gates, audit,
  redaction, authorization, webhook minimization, idempotency, or fail-closed
  revalidation;
- implementation requires a new architecture, security, data, deployment,
  framework, monitoring, or release decision;
- CI fails and the needed fix is outside the current Work Order.

## 6. Acceptance Boundary

This accepted backlog authorizes release-readiness implementation under
ADP-004. Production release still requires an explicit maintainer release
decision in WO-052.
