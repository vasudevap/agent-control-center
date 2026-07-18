# Work Order 041: Draft Generation and Facts-Used Evidence

**Status:** Accepted - Implementation Authorized
**Work Order ID:** WO-041
**Type:** Backend Gmail draft behavior
**Implementation Authorization:** Granted under ADP-003 on 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing Plan:** [Phase 6 Work Order Backlog](../implementation-plans/phase-6-work-order-backlog.md)
**Prerequisites:** WO-038 and WO-040 completed and merged

## 1. Purpose

Generate and create Gmail drafts only after eligibility, suppression, policy,
connector, and governed-knowledge checks pass, while binding exact fact
revisions into approval evidence.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Draft creation | Creates Gmail drafts only; never sends |
| Knowledge use | Uses only fresh governed facts and exact fact revisions |
| Evidence | Adds `facts_used` inside approval evidence and decision-context manifest |
| Model output | Treat as untrusted; schema and prohibited-content validation required |
| Message persistence | Store draft references, hashes, and minimized metadata, not full message bodies |

## 3. Approved Scope if Accepted

- Draft input assembly with minimum necessary source message context.
- Draft generation service boundary and prompt/config references.
- Strict schema validation for generated draft output.
- Prohibited-content and policy validation before Gmail draft creation.
- Gmail draft creation through fake-provider-backed connector operations.
- Draft provider references, content hash, evidence summary, and `facts_used`
  capture for later approval creation.
- Audit events for draft generation attempts, denials, creation, and validation
  failures.

## 4. Explicitly Out of Scope

Automatic send, approval decision submission, send continuation, edit-then-
approve, history learning, live Gmail calls, storing full message bodies,
suppressed-source drafting, dashboard productization, and new LLM framework
adoption are excluded.

## 5. Verification and Completion

Require tests for successful draft creation, no-send guarantee, missing/stale
fact denial, exact `facts_used` revision capture, decision-context manifest
binding, prohibited output rejection, suppressed-source denial, idempotent draft
creation, provider failure normalization, audit redaction, `ruff`, `mypy`, and
CI.

## 6. Rollback Expectations

Rollback must preserve draft provider references and hashes for already-created
drafts. If draft records are migrated, downgrade behavior must avoid losing
approval evidence needed for pending decisions.

## 7. Stop-and-Ask Triggers

Stop before sending email, using stale or unbound facts, retaining full message
body content, bypassing validation, adding a new LLM framework, drafting from a
suppressed source, or using live Gmail credentials.
