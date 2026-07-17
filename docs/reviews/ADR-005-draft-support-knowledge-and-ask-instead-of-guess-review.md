# ADR-005 Draft-Support Knowledge and Ask-Instead-of-Guess Review Record

**Status:** Pending Architecture and Security Review
**Decision Record:** `docs/decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md`
**Review Owner:** Repository Maintainer
**Date Routed:** 2026-07-17
**Date Reviewed:** Not reviewed
**Reviewed By:** Not assigned beyond the decision owners

## Review Objective

Determine whether ADR-005 should be accepted, revised, or rejected as the
generic Atlas contract for governed draft-support knowledge and the Gmail
agent's ask-instead-of-guess and learning behavior.

## Scope Routed for Review

- One requirement with a Phase 3 and Phase 5 platform half and a Phase 6 Gmail
  agent half.
- Governed business facts with CRUD, confirmation, volatility, and
  re-confirmation.
- First-class knowledge questions and answers for the single human owner.
- A typed `facts_used` collection inside existing approval evidence.
- Learning from validated answers and eligible confirmed sends.
- Exclusion of secrets, credentials, protected health information, and any
  suppressed clinical source.
- One generic external product client with no client-specific concepts.

## Required Architecture Review

Architecture Review must confirm:

1. Atlas remains authoritative for knowledge, approvals, policy, execution, and
   audit evidence.
2. The knowledge capability is a logical control-plane responsibility and does
   not require a new deployment container at this decision stage.
3. The external contract remains generic and limited to one external product
   client acting for one human owner and reviewer.
4. `facts_used` fits within the existing approval evidence contract and remains
   bound to the decision-context manifest.
5. Knowledge questions and answers remain separate from approvals and approval
   clarification.
6. Phase 3, Phase 5, and Phase 6 responsibilities form one sequenced R8
   requirement.

## Required Security Review

Security Review must confirm:

1. External access is deny by default and client authentication remains
   distinct from attribution to the one human owner.
2. Secrets, credentials, protected health information, and suppressed-source
   content are rejected before knowledge-store persistence.
3. Clinical suppression occurs before retrieval, question generation, or any
   history-learning input is assembled.
4. Webhooks are minimized notifications and confer no authorization.
5. Answers are untrusted inputs and cannot become facts without validation.
6. Stale or changed facts cause fail-closed revalidation when they invalidate a
   bound draft.
7. Audit provenance is sufficient without retaining prohibited content.

## Acceptance Path

1. Complete Architecture Review and record findings in this review record.
2. Complete Security Review and record findings in this review record.
3. Revise ADR-005 and canonical architecture for any required changes.
4. Record the Repository Maintainer's accept, revise, or reject decision.
5. If accepted, update ADR-005 status, review metadata, the decision index, and
   architecture status references in the same governed documentation change.
6. Create and approve the applicable Phase 3, Phase 5, and Phase 6 Engineering
   Specifications or Work Orders before any implementation begins.

## Current Decision

No acceptance decision has been recorded. ADR-005 remains Proposed and provides
no implementation authority.
