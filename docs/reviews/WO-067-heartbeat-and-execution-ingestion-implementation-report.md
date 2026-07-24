# WO-067 Heartbeat and Execution Ingestion Implementation Report

**Work Order:** [WO-067](../work-orders/067-heartbeat-and-execution-ingestion.md)
**Status:** Completed - Local Validation Passed
**Implemented:** 2026-07-24
**Commit:** This commit

## Summary

WO-067 implements the accepted agent telemetry ingestion contract for
externally operated agents.

The implementation:

- adds `POST /api/v1/agents/{agent_id}/heartbeats`;
- adds `PUT /api/v1/agents/{agent_id}/executions/{execution_id}`;
- authenticates agent bearer credentials through the WO-066 per-agent HMAC
  verifier service;
- enforces agent/path identity binding and rejects disconnected or archived
  agents;
- validates contract version, bounded fields, heartbeat check count, request
  size header, synthetic secret-like content, replay, idempotency, terminal
  regression, immutable started timestamp, and per-minute rate limits;
- stores accepted heartbeats and execution summaries in the WO-065 normalized
  tables;
- updates safe agent projections for first connection, last heartbeat, last
  activity, reported health, version, and build.

## Route-Base Alignment

WO-067 is backend/API-only and preserves the active-surface split adopted by
WO-064:

- `/` remains the public Atlas landing page;
- `/control-center` remains the canonical authenticated dashboard root;
- `/api/v1/agents/{agent_id}/heartbeats` and
  `/api/v1/agents/{agent_id}/executions/{execution_id}` are agent credential
  ingestion routes, not user-facing dashboard pages;
- later frontend Work Orders must consume live telemetry through
  `/control-center/...` surfaces rather than restoring root dashboard pages.

## Scope Alignment

In scope:

- bearer credential verification against the non-recoverable verifier store;
- active-surface-visible agent lookup and credential-to-agent path binding;
- lifecycle fail-closed behavior for disconnected and archived agents;
- heartbeat replay detection using a persisted event fingerprint;
- execution upsert idempotency by
  `(agent_id, external_execution_id, representation_hash)`;
- global telemetry limit of 60 requests per credential per minute, with
  heartbeats additionally capped at 30 requests per credential per minute;
- fail-closed rejection of arbitrary extra telemetry fields.

Out of scope and not implemented:

- derived observed-health evaluation;
- alert opening, acknowledgement, and resolution;
- dashboard UI integration;
- disconnect, reconnect, archive, credential rotation, and overlap windows;
- streaming ingestion, OpenTelemetry trace ingestion, SDK publishing, or
  Atlas-initiated agent execution.

## Validation

Local validation:

```text
/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m mypy apps/api/src
Success: no issues found in 68 source files

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m ruff check apps/api/src/atlas_api/api/agent_registry.py apps/api/src/atlas_api/services/agent_telemetry.py apps/api/tests/test_agent_telemetry_ingestion.py
All checks passed!

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m pytest apps/api/tests/test_agent_telemetry_ingestion.py
11 passed, 1 existing Starlette/httpx deprecation warning

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m pytest apps/api/tests/test_agent_visibility_schema.py apps/api/tests/test_agent_enrollment_credentials.py apps/api/tests/test_agent_telemetry_ingestion.py
23 passed, 1 existing Starlette/httpx deprecation warning

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m pytest apps/api
193 passed, 1 existing Starlette/httpx deprecation warning

npm run lint
pass

npm test
108 passed across 26 web test files

npm run build
pass

npm run typecheck
pass after `npm run build` generated the checked `.next/types` files

git diff --check
pass

Touched-file secret scan
pass
```

## Security Notes

- Agent ingestion does not use the external-product-client HMAC secret.
- Plaintext credentials remain one-time values and are never stored by the new
  telemetry routes.
- Rejected credential, path mismatch, lifecycle, replay, idempotency, rate, and
  secret-like payload cases fail closed.
- The secret rejection test constructs a synthetic secret-like value at runtime
  so no real credential is committed.

## Rollback

Source rollback disables the ingestion routes. Accepted telemetry rows remain
historical evidence and must not be deleted to simulate rollback.

## Residual Risks

- Health evaluation and alert derivation are deferred to WO-068.
- Live dashboard presentation of accepted telemetry is deferred to WO-069.
- Lifecycle controls and credential rotation/closeout are deferred to WO-070.
