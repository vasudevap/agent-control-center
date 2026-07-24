# Work Order 067: Heartbeat and Execution Ingestion

**Status:** Accepted - Authorized, blocked on WO-066 completion
**Work Order ID:** WO-067
**Type:** Agent telemetry ingestion
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-24
**Engineering Specification:** [ES-009](../engineering-specifications/ES-009-agent-visibility-and-lifecycle-mvp.md)
**Governing ADP:** [ADP-006](../implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md)
**Prerequisites:** WO-066 accepted and complete
**Review Record:** To be created during implementation

## 1. Purpose

Implement the accepted agent REST telemetry contract for authenticated
heartbeats and agent-reported executions.

## 2. Approved Scope if Accepted

- Implement `POST /api/v1/agents/{agent_id}/heartbeats`.
- Implement `PUT /api/v1/agents/{agent_id}/executions/{execution_id}`.
- Verify bearer credentials with constant-time HMAC comparison.
- Enforce agent/path identity binding and lifecycle rejection.
- Enforce contract version, body size, field bounds, rate limits, replay, and
  idempotency rules.
- Store accepted heartbeat and execution summaries in normalized tables.
- Update safe agent projections for last contact, reported health, version,
  build, and activity time.
- Add redaction and secret-pattern rejection tests.

## 3. Expected File Scope

- ES-009 agent telemetry API router modules
- ES-009 telemetry and credential service modules
- `apps/api/src/atlas_api/core/contracts.py`
- `apps/api/src/atlas_api/core/errors.py`
- `apps/api/src/atlas_api/main.py`
- `apps/api/tests/**`
- reference request examples only if useful for tests

## 4. Explicitly Out of Scope

Health evaluator loops, alert lifecycle, dashboard UI integration, credential
rotation, disconnect/reconnect/archive controls, published SDK packages,
streaming ingestion, OpenTelemetry traces, and Atlas-initiated execution are
out of scope.

## 5. Acceptance Criteria

- Valid heartbeat returns `202` and can transition pending agent to connected.
- Identical heartbeat replay returns the accepted response; conflicting replay
  returns `409`.
- Valid execution upsert returns `201` or `200` according to idempotency state.
- Terminal execution regressions and immutable timestamp conflicts return
  `409`.
- Token/path mismatch returns `403`; missing, unknown, expired, revoked,
  disconnected, or archived credentials fail closed.
- Payload, rate, bounds, contract-version, and secret rejection tests pass.

## 6. Verification

```bash
python -m mypy apps/api/src
python -m ruff check apps/api
python -m pytest apps/api
git diff --check
```

## 7. Rollback Expectations

Telemetry routes can be disabled by source rollback. Stored accepted telemetry
must remain historical evidence and must not be deleted to simulate rollback.

## 8. Stop-and-Ask Triggers

Stop before accepting arbitrary logs/prompts/provider payloads, weakening
credential rejection, introducing streaming or new infrastructure, calling
external agents from Atlas, or using live third-party business data.
