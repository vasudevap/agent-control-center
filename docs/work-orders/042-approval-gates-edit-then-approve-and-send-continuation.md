# Work Order 042: Approval Gates, Edit-Then-Approve, and Send Continuation

**Status:** Completed - Merged
**Work Order ID:** WO-042
**Type:** Backend Gmail approval and continuation behavior
**Implementation Authorization:** Granted under ADP-003 on 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing Plan:** [Phase 6 Work Order Backlog](../implementation-plans/phase-6-work-order-backlog.md)
**Prerequisites:** WO-041 completed and merged; Phase 5 approval and facts-used contracts completed
**Review Record:** [WO-042 Implementation Report](../reviews/WO-042-approval-gates-edit-then-approve-and-send-continuation-implementation-report.md)

## 1. Purpose

Require governed approval before high-risk Gmail actions and continue only
exact, revalidated sends with explicit `Sent`, `Failed`, or `Indeterminate`
outcomes.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Send policy | No automatic send; approval required before every send |
| Exact binding | Approval binds action, recipients, draft content, source message, evidence, facts, and manifest |
| Edit behavior | Human edits create a superseding approval through edit-then-approve |
| Revalidation | Source, draft, connector, actor, expiry, and facts-used must revalidate before continuation |
| Outcome | Every send attempt records `Sent`, `Failed`, or `Indeterminate` |

## 3. Approved Scope if Accepted

- Approval request creation for Gmail send and other high-risk proposed actions.
- Evidence payloads with source references, draft hash, recipient summary,
  minimized content summary, `facts_used`, and decision-context manifest.
- Internal and external approval channel compatibility.
- Edit-then-approve supersession for human-edited draft content.
- Send continuation through the Gmail connector after revalidation passes.
- Outcome classification for provider success, failure, timeout, ambiguous
  provider response, and retry exhaustion.
- Webhook and audit events for approval pending, decision, continuation,
  outcome, denial, and indeterminate state.

## 4. Explicitly Out of Scope

Automatic send, permanent delete, forward, unsubscribe, external sharing,
clinical/PHI override, live Gmail calls, multiple reviewers, delegated approval,
quorum, external-client authorization expansion, and dashboard productization
are excluded.

## 5. Verification and Completion

Require tests for approval creation, evidence minimization, exact content
binding, stale fact fail-closed behavior, expired/concurrent decision denial,
edit supersession, approved send continuation, rejected decision stop, provider
`Sent`/`Failed`/`Indeterminate` outcomes, webhook/audit redaction, `ruff`,
`mypy`, and CI.

## 6. Rollback Expectations

Rollback must preserve approval, decision, continuation, and send outcome
records. If a provider outcome is indeterminate, rollback must not retry
blindly; it must leave the item for manual reconciliation.

## 7. Stop-and-Ask Triggers

Stop before allowing any send without approval, weakening exact binding,
overriding suppression, broadening approval actors, retrying indeterminate sends
without manual reconciliation, or using live Gmail credentials.
