# Work Order 068: Health Evaluator and Alert Lifecycle

**Status:** Accepted - Authorized, blocked on WO-067 completion
**Work Order ID:** WO-068
**Type:** Derived health and alert lifecycle
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-24
**Engineering Specification:** [ES-009](../engineering-specifications/ES-009-agent-visibility-and-lifecycle-mvp.md)
**Governing ADP:** [ADP-006](../implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md)
**Prerequisites:** WO-067 accepted and complete
**Review Record:** To be created during implementation

## 1. Purpose

Implement Atlas-derived observed health, reported health projection, alert
conditions, and evaluator freshness without adding a new worker platform.

## 2. Approved Scope if Accepted

- Implement the ES-009 in-process evaluator loop gated by
  `ATLAS_API_AGENT_HEALTH_EVALUATOR_ENABLED`.
- Acquire and refresh the `agent-health-evaluator` database lease.
- Apply online, late, offline, never-seen, not-monitored, disconnected, and
  archived health rules from ES-009.
- Open, deduplicate, acknowledge, and auto-resolve ES-009 alert conditions.
- Record material health, alert, and telemetry rejection activity.
- Expand readiness and monitoring payloads for evaluator freshness.
- Add repeat-run, lease contention, transition, and alert deduplication tests.

## 3. Expected File Scope

- ES-009 health evaluator service modules
- ES-009 alert service modules
- ES-009 activity service modules
- `apps/api/src/atlas_api/api/routes.py`
- `apps/api/src/atlas_api/api/dashboard.py` only for readiness/monitoring
  compatibility where needed
- `apps/api/src/atlas_api/core/config.py`
- `apps/api/src/atlas_api/main.py`
- `apps/api/tests/**`

## 4. Explicitly Out of Scope

New Render services, queues, schedulers, orchestration frameworks, outbound
webhooks, notifications, frontend alert UI rewrite, and production
deployment/configuration are out of scope.

## 5. Acceptance Criteria

- Evaluator safely reruns without duplicate active alerts.
- Lease behavior prevents concurrent writers from corrupting health state.
- Missed heartbeat, failed check, repeated failure, version mismatch,
  environment mismatch, and security-ingestion alerts follow ES-009 keys and
  lifecycle.
- Acknowledgement does not resolve source conditions.
- Readiness exposes stale evaluator state without falsely reporting health.

## 6. Verification

```bash
python -m mypy apps/api/src
python -m ruff check apps/api
python -m pytest apps/api
git diff --check
```

## 7. Rollback Expectations

Disable the evaluator and show stale freshness rather than reporting false
health. Alert and activity history must remain intact.

## 8. Stop-and-Ask Triggers

Stop before adding a new worker/provider resource, sending outbound
notifications, weakening alert/audit history, changing health thresholds
outside ES-009, or treating agent-reported health as observed liveness.
