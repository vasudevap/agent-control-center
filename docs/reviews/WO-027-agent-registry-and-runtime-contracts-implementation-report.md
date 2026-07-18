# WO-027 Agent Registry and Runtime Contracts Implementation Report

**Status:** Implemented Locally - Pending PR, CI, and Merge
**Work Order:** [WO-027: Agent Registry and Runtime Contracts](../work-orders/027-agent-registry-and-runtime-contracts.md)
**Implemented Branch:** `codex/mvp-release-boundary-phase-gates`
**Implementation Date:** 2026-07-18
**Engineering Specification:** [ES-005: Agent Framework and Governance Contracts](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**ADP:** [ADP-002: Phase 5 Agent Framework and Governance Contracts](../implementation-plans/ADP-002-phase-5-agent-framework-and-governance-contracts.md)

## Summary

Implemented the generic agent registry and runtime contract foundation without
adding Gmail behavior, connector credentials, provider SDK calls, tool
execution, LLM calls, scheduling execution, production resources, or frontend
productization.

## Scope Delivered

- Added `agent_registrations` persistence through migration
  `0008_agent_registry_contracts`.
- Added SQLAlchemy metadata for agent descriptors, status, health, capabilities,
  allowed tools, required connectors, run-support flags, risk level, and
  configuration schema references.
- Added secret-bearing descriptor validation for agent configuration schemas.
- Added non-executing runtime protocol dataclasses for future concrete agents.
- Added signed external-client `/api/v1/agents` list, read, status, and health
  contracts using the existing success envelope and OpenAPI HMAC security
  declaration.
- Added explicit deny-by-default authorization allow rules only for low-risk
  agent-registry read actions.
- Added durable audit events for successful registry reads and denied registry
  attempts.
- Added focused tests for metadata separation, descriptor validation, signed API
  access, audit evidence, status/health separation, runtime descriptor shape,
  and OpenAPI security.

## Explicit Non-Scope Preserved

- No Gmail agent workflow, Gmail OAuth, Gmail API calls, connector credentials,
  provider SDK calls, tool execution, LLM calls, schedule execution, production
  deployment, multi-user behavior, RBAC, or frontend productization was added.
- Agent descriptors reference required connectors and allowed tools, but they do
  not store credentials or authorize tool execution.
- The runtime contract remains a plain Python protocol and does not introduce
  LangChain, LangGraph, Temporal, or another workflow framework.

## Validation

Local validation from `apps/api`:

```text
./.venv/bin/python -m pytest
./.venv/bin/python -m pytest tests/test_agent_registry.py
./.venv/bin/python -m ruff check .
./.venv/bin/python -m mypy src
git diff --check
```

Result:

- `53 passed`
- `tests/test_agent_registry.py`: `6 passed`
- `ruff`: all checks passed
- `mypy`: success, no issues in 37 source files
- `git diff --check`: passed

Known local warning:

- FastAPI/Starlette test client emits the pre-existing `httpx` deprecation
  warning from the local dependency set.

## Residual Risk

- PostgreSQL migration upgrade/downgrade evidence is expected from GitHub CI or
  a PostgreSQL-backed validation environment.
- Human dashboard authentication is not implemented yet, so the WO-027 read API
  is exposed only through the existing signed external-client boundary.
- WO-028 must use these registry contracts without adding concrete agent tool
  execution.
