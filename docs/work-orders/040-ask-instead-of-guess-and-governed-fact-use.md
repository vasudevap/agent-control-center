# Work Order 040: Ask-Instead-of-Guess and Governed Fact Use

**Status:** Implemented - Pending PR Review
**Work Order ID:** WO-040
**Type:** Backend Gmail knowledge behavior
**Implementation Authorization:** Granted under ADP-003 on 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing Plan:** [Phase 6 Work Order Backlog](../implementation-plans/phase-6-work-order-backlog.md)
**Prerequisites:** WO-037 and WO-038 completed and merged; Phase 5 knowledge contracts completed
**Review Record:** [WO-040 Implementation Report](../reviews/WO-040-ask-instead-of-guess-and-governed-fact-use-implementation-report.md)

## 1. Purpose

Connect Gmail draft prerequisites to governed knowledge so the agent asks for
missing or stale required facts instead of producing a generic or guessed draft.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Missing facts | Create a governed knowledge question before draft generation |
| Stale volatile facts | Require reconfirmation or a new answer before use |
| Answer trust | Treat human answers as untrusted until validated |
| Suppressed sources | Never create questions, answers, facts, or learned candidates |
| Approval separation | Questions and answers remain non-authorizing and separate from approvals |

## 3. Approved Scope if Accepted

- Gmail draft-scenario required-fact mapping.
- Governed fact retrieval with freshness, volatility, confirmation, and policy
  checks.
- Knowledge question creation for missing or stale required facts.
- Answer validation and fact revision creation through existing Phase 5
  contracts.
- Safe provenance metadata linking answer-derived facts to the triggering
  Gmail source reference without retaining full message content.
- Webhook and audit events for question and answer lifecycle events.

## 4. Explicitly Out of Scope

Draft generation, Gmail draft creation, send approval, send continuation,
history learning from approved sends, clinical/PHI content retention, approval
clarification reuse, live provider calls, and dashboard productization are
excluded.

## 5. Verification and Completion

Require tests for missing facts, stale volatile facts, fresh fact use, answer
validation, prohibited answer rejection, suppressed-source exclusion, distinct
question versus approval semantics, webhook/audit minimization, `ruff`, `mypy`,
and CI.

## 6. Rollback Expectations

Rollback must preserve existing Phase 5 fact/question/answer records. If
Gmail-specific provenance fields are added, they must remain safe references
without message bodies and be reversible or documented.

## 7. Stop-and-Ask Triggers

Stop before generating generic drafts for missing facts, using stale facts,
persisting prohibited content, learning from suppressed sources, conflating
questions with approvals, or storing full Gmail message content.
