# Work Order 029: Governed Knowledge Fact Contracts

**Status:** Implemented Locally - Pending PR, CI, and Merge
**Work Order ID:** WO-029
**Type:** Backend governance contract
**Implementation Authorization:** Granted under ADP-002 on 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing Plan:** [Phase 5 Work Order Backlog](../implementation-plans/phase-5-work-order-backlog.md)
**Architecture Authority:** [Data Architecture](../architecture/08-data-architecture.md), [ADR-005](../decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md)
**Prerequisite:** ES-005 accepted; Phase 3 backend foundation complete
**Review Record:** [WO-029 Implementation Report](../reviews/WO-029-governed-knowledge-fact-contracts-implementation-report.md)

## 1. Purpose

Implement governed business fact contracts for CRUD, immutable revisions,
confirmation, volatility, staleness, soft deletion, validation, authorization,
and audit.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Source of truth | PostgreSQL |
| Revisions | Immutable once created except approved defect correction paths |
| Deletion | Removes facts from active use without destroying evidence-relevant history |
| Prohibited content | Reject before persistence and retain only minimized reason metadata |
| Gmail | No Gmail history learning or message-derived facts |

## 3. Approved Scope if Accepted

- Fact and fact-revision service behavior over the Phase 3 persistence
  foundation.
- Fact create/read/update/delete API contracts.
- Confirmation, volatility, `last_confirmed_at`, stale volatile fact reads, and
  source provenance fields.
- Authorization, idempotency, pagination, filtering, audit, and OpenAPI tests.
- Secret, credential, clinical, and protected-health-information rejection
  tests using synthetic values.

## 4. Explicitly Out of Scope

Knowledge questions and answers, approval evidence `facts_used`, Gmail-derived
learning, LLM extraction, live provider data, production retention selection,
and frontend productization are excluded.

## 5. Verification and Completion

Require migration tests, fact service/API tests, prohibited-content tests,
authorization negative tests, audit tests, OpenAPI tests, `ruff`, `mypy`,
repository formatting checks, implementation report, CI, and governed merge.

## 6. Stop-and-Ask Triggers

Stop before storing prohibited values, learning from Gmail/history, weakening
revision immutability, using hard deletes for evidence-bearing data, or adding
retention periods without accepted authority.
