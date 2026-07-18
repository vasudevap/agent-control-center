# WO-025 Observability and Audit Baseline Implementation Report

**Status:** Completed - Pending Merge
**Work Order:** [WO-025: Observability and Audit Baseline](../work-orders/025-observability-and-audit-baseline.md)
**Implemented Branch:** `codex/wo-025-observability-audit`
**Implementation Date:** 2026-07-18
**ADP:** [ADP-001: Phase 3 Foundation Completion Program](../implementation-plans/ADP-001-phase-3-foundation-completion-program.md)

## Summary

Implemented the Phase 3 observability and audit baseline without adding an
external telemetry SDK, hosted observability vendor, alerting platform, or
frontend observability surface.

## Scope Delivered

- Added a standard-library JSON log formatter, structured log helper, UTC log
  timestamp convention, and central allowlist-first metadata sanitizer.
- Extended `audit_events` with channel, action, result, and reason-code fields
  through migration `0007_observability_audit`.
- Added a transaction-aware audit writer service that persists durable audit
  rows separately from operational logs.
- Replaced external-client authorization audit writes with the shared audit
  writer.
- Added queue, scheduler, and webhook audit hook adapters so material state
  changes can write audit events inside the caller's transaction.
- Updated the scheduler one-shot command to persist schedule audit events in
  the same transaction as the schedule sweep.
- Added captured-log/redaction, audit-shape, rollback/failure-policy, queue,
  schedule, and webhook audit tests.
- Corrected merged predecessor Work Order statuses in the Phase 3 backlog and
  Work Order records.

## Explicit Non-Scope Preserved

- No OpenTelemetry, exporter, hosted dashboard, alert routing, log shipping, or
  production retention configuration was introduced.
- No live infrastructure, provider calls, or real credentials were used.
- No Phase 5 knowledge, Gmail, OAuth, or business workflow behavior was added.
- Logs remain operational telemetry and are not treated as audit records.

## Validation

Local validation from the repository root:

```text
apps/api/.venv/bin/python -m pytest apps/api
apps/api/.venv/bin/python -m ruff check apps/api
apps/api/.venv/bin/python -m mypy apps/api/src
```

Result:

- `46 passed`
- `ruff`: all checks passed
- `mypy`: success, no issues in 33 source files

Known local warning:

- FastAPI/Starlette test client emits the pre-existing `httpx` deprecation
  warning from the local dependency set.

## Residual Risk

- PostgreSQL migration upgrade/downgrade evidence is expected from GitHub CI's
  PostgreSQL-backed validation environment.
- The baseline defines internal audit/logging primitives only; production
  retention, dashboards, exporters, and alert routing remain deferred by
  architecture and require later accepted authority.
