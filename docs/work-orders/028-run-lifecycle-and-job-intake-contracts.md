# Work Order 028: Run Lifecycle and Job Intake Contracts

**Status:** Accepted - Ready After WO-027
**Work Order ID:** WO-028
**Type:** Backend platform contract
**Implementation Authorization:** Granted under ADP-002 on 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing Plan:** [Phase 5 Work Order Backlog](../implementation-plans/phase-5-work-order-backlog.md)
**Architecture Authority:** [Agent Runtime Architecture](../architecture/09-agent-runtime.md), [Observability Architecture](../architecture/11-observability.md)
**Prerequisite:** [WO-027](./027-agent-registry-and-runtime-contracts.md)
**Review Record:** TBD

## 1. Purpose

Implement generic run lifecycle records and queue-backed job intake for manual
and scheduled agent triggers.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Queue payloads | Reference-only payloads; no sensitive source content |
| Run creation | Idempotent where retryable |
| Execution | Job intake and lifecycle records only; no live tool or connector execution |
| Status | Explicit lifecycle states with terminal states and audit |
| Scheduling | Reuse existing scheduler and queue foundations |

## 3. Approved Scope if Accepted

- Run and run-step persistence, models, migrations, and services.
- Manual run request API and schedule-to-run queue handoff.
- Run status, trigger source, correlation ID, idempotency key, timeout,
  cancellation, retry, and failure-reason metadata.
- Audit events and structured logs for run state transitions.
- Tests for duplicate prevention, lifecycle transitions, authorization, and
  no-sensitive-payload constraints.

## 4. Explicitly Out of Scope

Agent business logic, Gmail execution, connector calls, LLM calls, output
generation, approval creation, production scheduler deployment, and frontend
productization are excluded.

## 5. Verification and Completion

Require migration tests, service tests, API contract tests, queue integration
tests, audit/log redaction tests, `ruff`, `mypy`, repository formatting checks,
implementation report, CI, and governed merge.

## 6. Stop-and-Ask Triggers

Stop before executing real agent work, adding sensitive payloads to jobs,
changing queue architecture, introducing provider code, or weakening
idempotency and audit requirements.
