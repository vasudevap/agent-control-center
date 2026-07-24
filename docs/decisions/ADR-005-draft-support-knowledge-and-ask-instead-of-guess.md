# ADR-005 - Draft-Support Knowledge and Ask-Instead-of-Guess

**Status:** Superseded by `ADR-008 - Atlas Agent Visibility and Lifecycle Control Center`
**Date:** 2026-07-17
**Decision Owners:** Architecture and Security Review
**Review Owner:** Repository Maintainer
**Review State:** Architecture and Security Review Complete
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Scope:** External product client contract, governed knowledge, and Gmail drafting behavior
**Related Decisions:** `ADR-002 - Human Approvals Decision Integrity and Continuation`, `ADR-003 - Governed External Approval Decision Channel`, and `ADR-004 - Governed External Product Client Contract`

---

> Historical decision: retained as evidence for the original governed
> knowledge, Gmail drafting, and external-product-client direction. It no
> longer governs the active MVP.

## Context

Accepted ADR-004 completes the external approval loop for one external product
client acting for the single human owner and reviewer. It covers pending
approvals, evidence, agent and run status, approve or reject decisions, and the
existing authenticated webhook events. It does not define the governed business
knowledge used to create a useful draft.

Without that capability, a drafting agent either guesses, creates a generic
acknowledgement, or requires product-specific configuration outside Atlas. None
of those outcomes satisfies the generic platform contract or the requirement to
ask the human when a required fact is missing.

R8 combines the required platform contract and consuming agent behavior. The
platform half without the Gmail agent half creates an unused store. The Gmail
agent half without the platform half creates an unmanaged and unauditable
knowledge path.

MushingMule is the first example of the general external product client. Atlas
must not depend on a MushingMule-specific concept, schema, workflow, deployment
choice, or user experience.

## Decision

Atlas will add one governed draft-support knowledge capability to its control
plane. PostgreSQL remains the runtime system of record. The capability is a
logical backend responsibility and does not require a new deployment container.

R8 remains one requirement with two sequenced parts.

### Part A: External API and Platform Contract

The authenticated Atlas API will expose a generic knowledge contract to the
Atlas dashboard and to one governed external product client acting for the
single human owner.

The contract supports:

- Creating, reading, updating, and deleting a business fact.
- Confirming a fact for the one human owner.
- Marking a fact as volatile and recording `last_confirmed_at`.
- Reading stale volatile facts that require re-confirmation.
- Reading an ask-instead-of-guess question and submitting the human owner's
  answer.
- Reconciling authoritative fact, question, and answer state through the API.

Facts are versioned. Deletion removes a fact from active use, while a fact
revision already cited by approval evidence may be retained under evidence and
audit retention rules. Detailed staleness thresholds and retention periods
belong in the Phase 3 and Phase 5 Engineering Specifications.

Questions and answers are first-class knowledge records. They have their own
identities, lifecycle, provenance, and audit meaning. A question is created
before a draft when a required fact is missing. An answer acts for the same one
human owner, is untrusted input, and may create or update a fact only after
validation.

The external webhook channel adds notification events for:

- `knowledge.question.pending`.
- `knowledge.question.answered`.
- `knowledge.fact.reconfirmation_required`.

These events are authenticated notifications. They confer no authorization and
do not replace authoritative API reconciliation.

### Facts Used in Approval Evidence

Facts used by a draft fit within the existing approval evidence contract. Atlas
will add a typed `facts_used` collection inside the evidence payload. It will
not add a new top-level approval or decision field and will not create a
separate facts-used API.

Each evidence item identifies the exact fact revision used by the draft and
includes the minimum necessary display value, provenance, volatility state, and
confirmation timestamp. The immutable decision-context manifest binds to the
same revision or integrity identity.

If a bound fact changes, is deleted, or becomes stale under its governing
volatility policy before execution, revalidation fails closed when that change
invalidates the draft. Atlas then requires a regenerated draft and new approval
request. An earlier approval cannot authorize changed content.

### Part B: Gmail Agent Behavior

For a message eligible for drafting, the Gmail agent will:

1. Retrieve only governed facts that pass policy and freshness checks.
2. Create an ask-instead-of-guess question when a required fact is missing or
   requires re-confirmation, instead of producing a generic draft.
3. Validate the human answer and persist the resulting fact and immutable fact
   revision only when the knowledge policy permits it.
4. Include the exact fact revisions used by a completed draft in approval
   evidence.
5. Derive candidate facts from history only when the source is a past approved
   send with a confirmed `Sent` outcome.
6. Preserve source provenance for direct answers and history-derived facts.

`Failed` and `Indeterminate` send outcomes are not learning sources because
Atlas cannot establish that their content became a valid completed business
communication.

### Clinical, Secret, and Authorization Boundaries

Clinical and protected-health-information suppression occurs before knowledge
retrieval, question creation, history-learning input assembly, or fact
persistence. A suppressed message and any content derived from it can never be
a knowledge source. The existing `message.held_for_manual_handling` path remains
the only external-client path for that message.

The knowledge store must never contain:

- Secrets.
- Credentials or credential material.
- Protected health information.
- Message content or derived content from a clinically suppressed source.

Inputs are validated before persistence. Rejected prohibited content may
produce minimized audit metadata, but the prohibited value is not retained in
the knowledge store, logs, webhook payloads, or approval evidence.

Knowledge questions and answers are not approvals. They do not approve, reject,
or authorize an action. They are also distinct from approval Request
clarification, which belongs to an already pending approval and seeks missing
decision evidence. The two record types, APIs, webhooks, state transitions, and
audit semantics remain separate.

The capability remains limited to one human owner and reviewer and one governed
external product client. It introduces no users, roles, tenants, additional
reviewers, delegation, quorum, or multiple-client behavior.

## Sequencing

- Phase 3 establishes knowledge persistence, versioning, the generic API
  foundation, external-client authentication, and webhook delivery foundations.
- Phase 5 establishes governed fact CRUD and confirmation, volatility and
  re-confirmation, question and answer records, the `facts_used` evidence
  extension, audit provenance, and webhook contracts.
- Phase 6 implements Gmail-specific asking, answer learning, eligible-history
  learning, facts-used capture, and clinical-source exclusion.

Part A and Part B remain one requirement. Phase sequencing does not authorize
an isolated implementation that leaves either half without its governed
counterpart.

## Consequences

### Positive

- Drafts can rely on explicit, reviewable business facts.
- Missing facts produce a governed question instead of a guess or generic reply.
- The human can see which exact facts supported a pending draft.
- Volatile facts have explicit confirmation state.
- The external contract remains generic and Atlas remains authoritative.

### Trade-offs

- The platform must govern knowledge lifecycle, versioning, provenance,
  retention, and stale-fact behavior.
- Phase 5 approval evidence must support typed fact references and revalidation.
- Question and answer records require a separate lifecycle from approvals.
- History learning requires strict source eligibility and sensitivity controls.

### Risks

- A stale or incorrectly derived fact could produce a misleading draft.
- A weak facts-used binding could show different knowledge from what the draft
  actually used.
- Conflating answers with approval decisions could create an authorization
  bypass.
- A learning pipeline could retain secrets, credentials, clinical content, or
  protected health information if validation occurs too late.
- Product-specific fields could couple Atlas to the first external client.

## Alternatives Considered

### Store knowledge in the external product client

Rejected because it would make the external client authoritative for agent
drafting context and weaken Atlas policy, provenance, audit, and portability.

### Put facts used in a new top-level approval field

Rejected because facts are decision evidence. A parallel top-level field would
duplicate evidence semantics and risk divergence from the decision-context
manifest.

### Treat ask-instead-of-guess as approval clarification

Rejected because no draft or approval exists when the required fact is missing.
Reusing clarification would confuse knowledge acquisition with authorization.

### Learn from every historical draft or send attempt

Rejected because unapproved, failed, indeterminate, or suppressed content is not
a trustworthy source of completed business behavior.

## Deferred Detailed Design

Before implementation, the Phase 3 and Phase 5 Engineering Specifications must
define:

- Logical and physical schemas, versioning, deletion, retention, and migration.
- Fact validation, confirmation, volatility policies, and staleness evaluation.
- API schemas, authorization scopes, idempotency, errors, pagination, and rate
  limits.
- Question and answer lifecycle, timeout, cancellation, and duplicate handling.
- Webhook subscription, payload minimization, retry, ordering, deduplication,
  and reconciliation.
- Facts-used evidence schemas, decision-context manifest binding, and
  revalidation behavior.
- Secret, credential, clinical, and protected-health-information detection and
  fail-closed handling.
- Source provenance, history eligibility, audit events, metrics, alerts, and
  recovery procedures.

## Governance and Acceptance

This ADR is Accepted and provides no implementation authority by itself.

The acceptance review confirmed:

1. Architecture Review confirmation that the knowledge capability remains in
   the Atlas control plane, extends ADR-004 generically, and preserves Phase 3,
   Phase 5, and Phase 6 sequencing.
2. Security Review confirmation of deny-by-default access, single-human
   attribution, prohibited-content exclusion, clinical suppression ordering,
   evidence minimization, audit provenance, and fail-closed behavior.
3. Confirmation that `facts_used` remains typed approval evidence bound to the
   decision-context manifest.
4. Confirmation that knowledge questions and answers remain non-authorizing and
   separate from approval clarification.
5. No unresolved architecture-level or security-level finding remains after
   the canonical Security and Human Approvals architecture corrections.

Implementation still requires approved Phase 3, Phase 5, and
Phase 6 Engineering Specifications or Work Orders that satisfy the Definition
of Ready. This documentation change authorizes no code, schema migration,
endpoint, webhook, agent behavior, or frontend change.
