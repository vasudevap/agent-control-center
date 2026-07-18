# ADP-004: Phase 7 Operational MVP Release

**Status:** Accepted - Execution Authorized
**Program ID:** ADP-004
**Type:** Autonomous Delivery Program
**Owner:** Repository Maintainer
**Created:** 2026-07-18
**Execution Window:** Authorized on 2026-07-18
**Engineering Specification:** `docs/engineering-specifications/ES-007-operational-mvp-release-readiness.md`
**Work Order Backlog:** `docs/implementation-plans/phase-7-work-order-backlog.md`

---

## 1. Purpose

Collect the proposed Phase 7 Operational MVP Release Readiness Work Orders into
one sequenced execution program.

This ADP does not replace individual Work Orders. Each Work Order remains the
technical scope authority for its implementation, exclusions, validation gates,
rollback expectations, and stop-and-ask triggers after acceptance.

## 2. Execution Authority

Execution authority is granted by Repository Maintainer acceptance on
2026-07-18.

The Repository Maintainer accepted ES-007, accepted WO-045 through WO-052,
accepted this ADP, and authorized Phase 7 release-readiness implementation.

Even after acceptance, this ADP does not authorize personal mailbox use,
unbounded live Gmail data, public launch, multi-user operation, production
cutover, broader OAuth scopes, or a new architecture decision unless the
applicable Work Order and maintainer release decision explicitly grant that
authority.

## 3. Proposed Work Order Set

| Order | Work Order | Current State | ADP Execution Action | Completion Gate |
| ---: | --- | --- | --- | --- |
| 1 | `WO-045: Controlled-Account Release Verification` | Accepted - Pending Implementation | Execute | Controlled-account evidence executed and cleaned up, or deferral explicitly accepted |
| 2 | `WO-046: Dashboard Productization and Runtime Operations` | Accepted - Pending Implementation | Execute | MVP-critical dashboard workflows use real contracts and pass UI validation |
| 3 | `WO-047: Environment Configuration and Secrets Readiness` | Implemented - Pending PR Review | Review and merge | Required config, OAuth setup, secret handling, redaction, and fail-closed checks documented and verified |
| 4 | `WO-048: Deployment Path and Migration Readiness` | Accepted - Pending Implementation | Execute | Netlify/Render path, migration procedure, backup/restore, and rollback evidence are ready |
| 5 | `WO-049: Monitoring, Health, and Recovery Readiness` | Accepted - Pending Implementation | Execute | Health/readiness, logs, metrics, alerts, and manual recovery paths are adequate for MVP |
| 6 | `WO-050: Release Runbooks and Rollback` | Accepted - Pending Implementation | Execute | Operator runbooks and rollback procedures are reviewed and complete |
| 7 | `WO-051: MVP Release Candidate Validation` | Accepted - Pending Implementation | Execute | Final local, CI, migration, security/privacy, dashboard, fake-provider, and authorized controlled-account evidence recorded |
| 8 | `WO-052: MVP Acceptance and Phase 7 Closeout` | Accepted - Pending Implementation | Execute | Maintainer release decision and residual risk disposition recorded |

## 4. Dependency Sequence

```text
ES-007 accepted + WO-045 through WO-052 accepted + ADP-004 accepted
  -> Wave 1 parallel lanes:
      WO-045 controlled-account evidence
      WO-046 dashboard productization
      WO-047 environment and secrets readiness
    -> Wave 2:
      WO-048 deployment and migration readiness
      WO-049 monitoring, health, and recovery readiness
    -> Wave 3:
      WO-050 runbooks and rollback
    -> Wave 4:
      WO-051 MVP release candidate validation
    -> Wave 5:
      WO-052 MVP acceptance and Phase 7 closeout
```

## 5. Parallel Execution Notes

| Lane | Work Orders | Parallel-safe conditions |
| --- | --- | --- |
| Provider evidence lane | WO-045 | Only after explicit controlled-account authorization; must not use personal or production mailbox data |
| Dashboard lane | WO-046 | Safe if it owns frontend integration and UI evidence without changing backend contracts silently |
| Configuration lane | WO-047 | Safe if it documents and validates config/secrets without provisioning live resources without authority |
| Deployment lane | WO-048 | Limited by configuration decisions and migration controls |
| Operations lane | WO-049, WO-050 | Safe after run, webhook, audit, and deployment signals are stable |
| Release validation lane | WO-051, WO-052 | Serial final evidence and maintainer decision |

Parallel agents must not modify the same migration head, environment contract,
dashboard route, health endpoint, runbook, or release evidence file without
rebasing and reconciling before PR review.

## 6. Stop-and-Ask Triggers

Stop and request Repository Maintainer direction before proceeding if any of
the following occurs:

- ES-007, a required Work Order, or ADP-004 is not accepted;
- required CI fails and the failure is not a narrow, in-scope defect fix;
- implementation requires live infrastructure, production database access,
  production deployment, personal mailbox data, production mailbox data, live
  OAuth credentials, or controlled-account execution outside the accepted
  Work Order boundary;
- provider behavior requires broader Google scopes or changed Gmail behavior;
- implementation would store full Gmail bodies, OAuth token values, secrets,
  clinical content, PHI, or unrestricted attachment copies;
- implementation would weaken authentication, authorization, audit, redaction,
  suppression, approval evidence, webhook minimization, idempotency, or
  fail-closed revalidation;
- a new ADR, Engineering Specification, Work Order, or release decision is
  required.

## 7. Evidence and Reporting

Each Work Order completed under ADP-004 must leave evidence in the repository:

- implementation or readiness report under `docs/reviews/`;
- Work Order status and review-record links kept current;
- local validation command results summarized in the PR;
- GitHub CI result available from the merged PR;
- deployment, configuration, monitoring, security, privacy, rollback, and
  controlled-account evidence where relevant;
- residual risk or deferred scope recorded when relevant.

## 8. Completion Definition

ADP-004 is complete only when:

- WO-045 through WO-052 are implemented, validated, reviewed, and merged;
- release candidate evidence proves the MVP boundary end to end;
- no unresolved safety, security, credential, provider, deployment, rollback,
  or CI blocker remains;
- residual risks are accepted by the Repository Maintainer;
- the MVP release decision is recorded.
