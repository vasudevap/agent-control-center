# ADR-005 Draft-Support Knowledge and Ask-Instead-of-Guess Review Record

**Status:** Accepted
**Decision Record:** `docs/decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md`
**Review Owner:** Repository Maintainer
**Date Routed:** 2026-07-17
**Technical Review Date:** 2026-07-17
**Technical Review Prepared By:** Codex architecture and security review
**Decision Authority:** Repository Maintainer
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer

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

## Architecture Review Findings

- **Authoritative control plane:** Pass. Atlas owns fact, revision, question,
  answer, approval, policy, execution, and audit state. The external product
  client remains a presentation and interaction surface.
- **Container responsibility:** Pass. The knowledge capability is a logical
  Backend API and PostgreSQL control-plane responsibility. No new deployment
  container or framework is introduced by this decision.
- **Generic contract and scope:** Pass. Contracts use generic fact, question,
  answer, evidence, and external-product-client terminology. MushingMule is
  only the first example client. The one-client and one-human constraint is
  preserved.
- **Approval evidence integrity:** Pass. `facts_used` is typed evidence rather
  than a parallel approval field and is bound to exact fact revisions through
  the ADR-002 decision-context manifest.
- **Lifecycle separation:** Pass. Ask-instead-of-guess occurs before a draft
  exists and remains distinct from approval, approve or reject decisions, and
  approval Request clarification.
- **Sequencing:** Pass. Phase 3 owns persistence, authentication, API, and
  webhook foundations; Phase 5 owns governed contracts and approval evidence;
  Phase 6 owns Gmail-specific asking, learning, and facts-used capture.
- **Canonical architecture consistency:** Pass after review correction. The
  Human Approvals acceptance criteria now explicitly cover R8 authority,
  lifecycle separation, exact-revision evidence, fail-closed revalidation,
  prohibited-content ordering, and eligible learning sources.

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

## Security Review Findings

- **Authentication, attribution, and authorization:** Pass for architecture
  acceptance. External-client authentication remains separate from attribution
  to the one human owner, and resource/action access is deny by default. The
  concrete mechanisms remain required Phase 3 and Phase 5 design.
- **Prohibited-content exclusion:** Pass after review correction. The canonical
  security architecture now identifies governed knowledge as a protected asset
  and requires pre-persistence rejection of secrets, credentials, protected
  health information, and suppressed-source content.
- **Clinical suppression ordering:** Pass. Suppression precedes retrieval,
  question creation, history-learning input assembly, and fact persistence.
  The minimized manual-hold path remains the only external-client result.
- **Webhook authority:** Pass. Knowledge webhooks are authenticated,
  minimum-necessary notifications. They neither authorize actions nor replace
  authoritative API reconciliation.
- **Untrusted answers and learning sources:** Pass. Answers require validation
  before fact mutation. History learning is restricted to approved sends with
  confirmed `Sent` outcomes; `Failed` and `Indeterminate` outcomes are excluded.
- **Fail-closed revalidation:** Pass. Evidence binds exact fact revisions. A
  changed, deleted, or stale fact that invalidates a draft requires regeneration
  and a new approval request.
- **Audit and retention minimization:** Pass for architecture acceptance.
  Material knowledge lifecycle and validation outcomes require durable
  provenance, while prohibited values are excluded from logs, webhooks, audit
  payloads, evidence, and retained knowledge content.

## Review Corrections Applied

The review identified one blocking documentation gap: R8 controls existed in
the product, data, and approval documents but were not explicit in the canonical
security architecture. The review updates:

- `docs/architecture/07-security-architecture.md` with the knowledge protected
  asset, trust boundary, prohibited-content controls, approval binding,
  validation, audit, retention, monitoring, threat, and test requirements.
- `docs/architecture/13-human-approvals.md` with explicit R8 architecture
  acceptance criteria and the accepted-ADR prerequisite for implementation.

No unresolved architecture-level or security-level finding remains after these
corrections.

## Review Limitations and Required Detailed Design

The technical review does not select database schemas, authentication methods,
authorization scopes, staleness thresholds, retention periods, detection
implementations, webhook retry policies, rate limits, or recovery procedures.
Those are mandatory Phase 3 and Phase 5 Engineering Specification decisions and
must receive their own security and privacy review before implementation.

## Acceptance Path

1. Complete Architecture Review and record findings in this review record.
2. Complete Security Review and record findings in this review record.
3. Revise ADR-005 and canonical architecture for any required changes.
4. Record the Repository Maintainer's accept, revise, or reject decision.
5. If accepted, update ADR-005 status, review metadata, the decision index, and
   architecture status references in the same governed documentation change.
6. Create and approve the applicable Phase 3, Phase 5, and Phase 6 Engineering
   Specifications or Work Orders before any implementation begins.

## Technical Review Recommendation

**Recommend Accept.** All required architecture and security review questions
pass at the architecture-decision level after the documented canonical
architecture corrections. Deferred detailed design is explicit, and ADR-005
continues to provide no implementation authority by itself.

## Current Decision

ADR-005 is **Accepted** on 2026-07-17 by the Repository Maintainer.

The acceptance basis is:

1. All required Architecture Review findings pass.
2. All required Security Review findings pass at the architecture-decision
   level.
3. The canonical security and Human Approvals architecture corrections resolve
   the only review finding.
4. Deferred detailed design remains explicit and requires separately approved
   Phase 3, Phase 5, and Phase 6 execution artifacts.
5. Acceptance authorizes the architecture direction but no code, schema,
   endpoint, webhook, agent behavior, or frontend implementation.
