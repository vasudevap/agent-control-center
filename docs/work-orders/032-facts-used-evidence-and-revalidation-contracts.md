# Work Order 032: Facts-Used Evidence and Revalidation Contracts

**Status:** Implemented Locally - Pending PR, CI, and Merge
**Work Order ID:** WO-032
**Type:** Backend cross-domain governance contract
**Implementation Authorization:** Granted under ADP-002 on 2026-07-18
**Engineering Specification:** [ES-005](../engineering-specifications/ES-005-agent-framework-and-governance-contracts.md)
**Governing Plan:** [Phase 5 Work Order Backlog](../implementation-plans/phase-5-work-order-backlog.md)
**Architecture Authority:** [ADR-002](../decisions/ADR-002-human-approvals-decision-integrity.md), [ADR-005](../decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md)
**Prerequisites:** [WO-029](./029-governed-knowledge-fact-contracts.md), [WO-031](./031-approval-decision-and-manual-handling-contracts.md)
**Review Record:** [WO-032 Implementation Report](../reviews/WO-032-facts-used-evidence-and-revalidation-contracts-implementation-report.md)

## 1. Purpose

Bind approval evidence to exact governed fact revisions and revalidate those
facts before execution continuation.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Evidence shape | `facts_used` is typed approval evidence, not a top-level approval field |
| Binding | Evidence references exact fact revisions or integrity identities |
| Revalidation | Fail closed when a relevant fact is stale, deleted, changed, or invalid |
| Scope | Generic contract only; no Gmail draft generation |
| Audit | Revalidation pass/fail produces durable audit evidence |

## 3. Approved Scope if Accepted

- `facts_used` evidence schemas inside the existing evidence payload.
- Decision-context manifest binding for fact revision identities.
- Revalidation service and failure reason codes.
- Tests covering changed, deleted, stale, prohibited, and unchanged fact
  scenarios.
- Audit, OpenAPI, and authorization tests for evidence and revalidation paths.

## 4. Explicitly Out of Scope

Gmail draft generation, LLM prompt assembly, connector execution, facts-used UI
productization, new approval field topology, and production retention policy
selection are excluded.

## 5. Verification and Completion

Require cross-domain contract tests, revalidation negative tests, audit tests,
schema tests, `ruff`, `mypy`, repository formatting checks, implementation
report, CI, and governed merge.

## 6. Stop-and-Ask Triggers

Stop before allowing stale or changed facts to continue execution, adding a
parallel approval field, weakening evidence binding, or introducing
Gmail-specific draft semantics.
