# Phase 7 Monitoring, Health, and Recovery Readiness

**Status:** Implemented - Pending Review
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Work Order:** [WO-049](../work-orders/049-monitoring-health-and-recovery-readiness.md)
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)

---

## 1. Purpose

Define the MVP monitoring, health, alert, and manual recovery boundary for
normal single-owner operation.

This record uses existing health endpoints, structured logs, audit records,
run state, webhook delivery records, connector health, and provider outcomes.
It does not adopt OpenTelemetry, a hosted monitoring vendor, automated
remediation, or an on-call process.

## 2. Health and Readiness Signals

| Signal | Source | MVP readiness expectation | Alert posture |
| --- | --- | --- | --- |
| API liveness | `/health/live` | Returns process, service, and environment status | Alert if unavailable for 5 minutes after deployment |
| API readiness | `/health/ready` | Returns stable problem codes for missing release-critical configuration | Alert before release if not `ready` in production-like environments |
| Database readiness | `/health/ready`, migration evidence, runtime errors | Database URL configured and migrations at expected head | Alert on connection or migration failure |
| Queue readiness | Queue records and run intake tests | Jobs can be created and claimed through PostgreSQL-backed queue | Alert on repeated stuck or failed job claims |
| Scheduler readiness | `atlas-schedule-sweep` command and schedule audit events | Sweep creates due runs without duplicate occurrences | Alert if no successful sweep occurs in the expected window |
| Connector health | Connector health endpoint and connection status | Gmail and Drive connections are approved, healthy, and not revoked | Alert on revoked, missing-scope, or unhealthy connection |
| Webhook delivery | Webhook delivery attempts and audit events | Notifications remain minimized and retry/failure state is visible | Alert on repeated permanent failures |
| Gmail/Drive provider errors | Normalized connector outcomes and audit | Rate limits, auth errors, and provider failures are reason-coded | Alert on repeated throttling, auth failure, or indeterminate send |
| Suppression guardrail | Manual-handling records and audit | Clinical/PHI sources produce holds only | Alert on any downstream action from suppressed source |

## 3. MVP Metrics

The MVP can derive the following metrics from existing state without a new
metrics vendor:

| Metric | Source | Initial threshold |
| --- | --- | --- |
| Failed runs | Run status records | More than 2 consecutive failed Gmail runs |
| Stuck runs | Run status and timestamps | Running or queued longer than 30 minutes |
| Pending approvals | Approval state | Any send approval pending longer than 24 hours |
| Held messages | Manual-handling records | Daily review, immediate review for clinical/PHI hold |
| Indeterminate sends | Gmail send outcome records | Any indeterminate outcome requires manual reconciliation |
| Webhook permanent failures | Webhook attempt records | Any permanent failure requires owner review |
| Credential revocations | Connector connection status | Immediate reconnect or intentional-disable decision |
| Provider throttling | Normalized provider errors | Repeated throttling in one run or across 2 consecutive runs |
| Migration/runtime failure | CI, deploy logs, readiness | Any production-like failure blocks release or promotion |

Thresholds are intentionally conservative for single-owner MVP operation.

## 4. Log and Audit Requirements

Logs must include:

- timestamp;
- component;
- severity;
- correlation ID;
- run ID when a run is involved;
- safe reason codes for provider/configuration failures.

Logs, alerts, webhooks, and audit metadata must not include:

- OAuth token values;
- database URLs;
- HMAC secrets;
- Google OAuth client secrets;
- full Gmail bodies;
- clinical content or PHI;
- unrestricted attachment content.

Audit remains the durable accountability record for connector lifecycle,
classification, suppression, low-risk actions, questions, drafts, approvals,
sends, webhook events, and denied actions.

## 5. Manual Recovery Procedures

| Failure mode | Recovery path |
| --- | --- |
| API not live | Inspect Render service status and latest deploy; roll back app deploy if needed |
| API not ready | Review stable readiness problem codes; correct missing provider-native environment values |
| Migration failed | Stop promotion; inspect Alembic version, restore/backup state, and corrective migration plan |
| Scheduler missed window | Run `atlas-schedule-sweep` once from approved context after database and duplicate-prevention checks |
| Queue stuck | Inspect queued/running jobs and run records; avoid duplicate execution unless idempotency is proven |
| Gmail connection revoked | Mark connector unhealthy, reconnect through approved OAuth flow, and audit the lifecycle |
| Provider throttling | Pause or reduce run frequency; retry only idempotent low-risk operations according to recorded state |
| Webhook failures | Treat webhooks as notifications; reconcile through Atlas API and retry only delivery attempts |
| Indeterminate send | Check Gmail account manually; record outcome before any further action |
| Suppression anomaly | Stop Gmail Agent runs; inspect audit and manual-handling records; do not approve or learn from source |

## 6. Deferred Post-MVP Monitoring

The following remain deferred until requirements justify them:

- OpenTelemetry SDK/exporter deployment;
- hosted log or metrics vendor adoption;
- distributed tracing;
- synthetic uptime monitoring;
- automated incident paging;
- automated remediation;
- load and chaos testing beyond MVP readiness;
- multi-user support operations.

## 7. Release Gate

Before WO-051 release candidate validation, the maintainer should be able to
answer:

- Is `/health/live` available in the target environment?
- Is `/health/ready` `ready` with no release-critical configuration problems?
- Are Gmail and Drive connector states healthy or intentionally disabled?
- Can failed runs, stuck runs, held messages, pending approvals, webhook
  failures, and indeterminate sends be found from Atlas records?
- Are manual recovery procedures complete enough for single-owner use?
