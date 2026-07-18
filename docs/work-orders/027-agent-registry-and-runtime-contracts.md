# Work Order 027: Agent Registry and Runtime Contracts

**Status:** Completed - Merged
**Work Order ID:** WO-027
**Type:** Backend platform contract
**Implementation Authorization:** Granted under ADP-002 on 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing Plan:** [Phase 5 Work Order Backlog](../implementation-plans/phase-5-work-order-backlog.md)
**Architecture Authority:** [Agent Runtime Architecture](../architecture/09-agent-runtime.md), [Security Architecture](../architecture/07-security-architecture.md)
**Prerequisite:** ES-005 accepted
**Review Record:** [WO-027 Implementation Report](../reviews/WO-027-agent-registry-and-runtime-contracts-implementation-report.md)

## 1. Purpose

Implement the generic agent registry and runtime contract foundation required
before Atlas can execute concrete agents.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Scope | Generic agent metadata, descriptor, health, status, and runtime interfaces only |
| Runtime | Plain Python contracts; no LangChain, LangGraph, Temporal, or provider framework |
| Provider behavior | No Gmail or live connector execution |
| Secrets | Descriptors and configuration schemas must not contain secrets |
| Identity | Preserve one-owner, one-reviewer, one-external-client architecture |

## 3. Approved Scope if Accepted

- Agent registry persistence, models, and migrations.
- Agent descriptor schemas for capabilities, version, risk level, allowed tools,
  required connectors, schedule support, manual-run support, and configuration
  schema references.
- Agent list/read/status/health API contracts.
- Runtime protocol or service interfaces that future agents must satisfy.
- Authorization, audit, OpenAPI, and contract tests for registry operations.

## 4. Explicitly Out of Scope

Gmail agent logic, connector credentials, provider SDK calls, tool execution,
LLM calls, scheduling execution, production deployment, multi-user behavior,
and frontend productization are excluded.

## 5. Verification and Completion

Require focused unit/integration tests, migration tests, OpenAPI contract tests,
authorization negative-path tests, audit evidence tests, `ruff`, `mypy`,
repository formatting checks, implementation report, CI, and governed merge.

## 6. Stop-and-Ask Triggers

Stop before adding a workflow framework, provider-specific fields, live
credentials, multi-user concepts, broad runtime execution behavior, or any
contract that contradicts ES-005 or accepted ADRs.
