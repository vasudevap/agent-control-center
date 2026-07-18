# WO-028 Run Lifecycle and Job Intake Contracts Implementation Report

**Status:** Implemented Locally - Pending PR, CI, and Merge
**Work Order:** [WO-028: Run Lifecycle and Job Intake Contracts](../work-orders/028-run-lifecycle-and-job-intake-contracts.md)
**Implemented Branch:** `codex/wo-028-run-lifecycle-job-intake`
**Implementation Date:** 2026-07-18
**Engineering Specification:** [ES-005: Agent Framework and Governance Contracts](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**ADP:** [ADP-002: Phase 5 Agent Framework and Governance Contracts](../implementation-plans/ADP-002-phase-5-agent-framework-and-governance-contracts.md)

## Summary

Implemented generic run lifecycle records and queue-backed manual job intake
without adding agent business logic, Gmail execution, connector calls, LLM
calls, output generation, approval creation, production scheduler deployment, or
frontend productization.

## Scope Delivered

- Added migration `0011_run_lifecycle` for `agent_runs` and `agent_run_steps`.
- Added run lifecycle model fields for status, trigger source, correlation ID,
  idempotency key, queue job reference, timeout, retry count, failure reason,
  and lifecycle timestamps.
- Added manual run creation API using the existing signed external-client
  boundary.
- Reused the existing queue foundation to enqueue an `agent.run` job with
  reference-only metadata: `run_id`, `agent_id`, and `trigger_source`.
- Added run list, read, and cancel APIs.
- Added explicit authorization for run read/create/cancel actions and durable
  audit events for API state transitions.
- Added tests for idempotent run creation, unsupported agent rejection, queue
  payload minimization, read/list/cancel lifecycle behavior, authorization
  boundary, and OpenAPI security.

## Explicit Non-Scope Preserved

- No real agent execution, connector action, Gmail API call, LLM call, output
  generation, approval creation, or production scheduler deployment was added.
- Queue payloads remain reference-only and contain no source content.
- Scheduled run creation remains limited to compatibility with the existing
  scheduler/queue foundations; production scheduler deployment remains out of
  scope.

## Validation

Local validation from `apps/api`:

```text
./.venv/bin/python -m pytest
./.venv/bin/python -m ruff check .
./.venv/bin/python -m mypy src
git diff --check
```

Result:

- `67 passed`
- `ruff`: all checks passed
- `mypy`: success, no issues in 46 source files
- `git diff --check`: passed

Known local warning:

- FastAPI/Starlette test client emits the pre-existing `httpx` deprecation
  warning from the local dependency set.

## Residual Risk

- PostgreSQL migration upgrade/downgrade evidence is expected from GitHub CI's
  backend migrations step.
- Worker execution and run-step progression remain intentionally unimplemented
  until a later accepted work order authorizes concrete runtime behavior.
