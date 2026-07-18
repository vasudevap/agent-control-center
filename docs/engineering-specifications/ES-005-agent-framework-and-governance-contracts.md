# ES-005 - Agent Framework and Governance Contracts

**Status:** Proposed - Governance Review Required
**Owner:** Repository Maintainer
**Review Owner:** Repository Maintainer
**Date:** 2026-07-18
**Version:** 0.1
**Accepted:** Not Accepted
**Implementation Authorization:** Not Granted
**Target Release:** MVP-enabling pre-MVP foundation
**Related Work Orders:** `docs/work-orders/027-agent-registry-and-runtime-contracts.md` through `docs/work-orders/035-phase-5-contract-integration-verification-and-closeout.md`
**Governing Plan:** `docs/implementation-plans/phase-5-work-order-backlog.md`
**Autonomous Delivery Program:** `docs/implementation-plans/ADP-002-phase-5-agent-framework-and-governance-contracts.md`
**Related ADRs:** `docs/decisions/ADR-002-human-approvals-decision-integrity.md`, `docs/decisions/ADR-003-governed-external-approval-decision-channel.md`, `docs/decisions/ADR-004-governed-external-product-client-contract.md`, `docs/decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md`

---

## 1. Purpose

Define the Phase 5 engineering scope for generic agent framework and governance
contracts.

ES-005 turns the completed Phase 3 backend foundation into executable platform
contracts for agent registration, run lifecycle, approval decision APIs,
manual-handling state, governed knowledge, facts-used evidence, revalidation,
webhook events, and audit behavior.

This specification is intentionally generic. It does not authorize Gmail OAuth,
Gmail message processing, live provider calls, live webhooks, production
deployment, or product-specific MushingMule fields.

## 2. Engineering Decision

Phase 5 implements the control-plane contracts that Phase 6 Gmail behavior will
consume.

The platform must:

- keep Atlas authoritative for agent state, approvals, knowledge, audit, and
  execution outcomes;
- preserve one owner, one human reviewer, and one governed external product
  client;
- require authentication by default and authorization by explicit action;
- use PostgreSQL as the runtime system of record;
- expose API contracts through `/api/v1` using existing response, error,
  pagination, correlation, and idempotency conventions;
- record material state transitions as durable audit events;
- emit only signed, minimum-necessary webhook notifications through the
  existing webhook delivery foundation;
- treat all external input, human answers, and model output as untrusted.

## 3. Intended Outcome

After ES-005 is implemented, Atlas has a reviewable generic contract layer that
can support the first Gmail Agent MVP candidate:

- Agents can be registered, described, health-checked, and selected through
  stable backend contracts.
- Runs can be created through manual or scheduled triggers without executing a
  Gmail-specific workflow.
- Approval queue, evidence retrieval, approve/reject, and edit-then-approve
  contracts exist for internal and external decision channels.
- Manual-handling records and events exist for suppressed messages without
  creating approvable actions.
- Knowledge facts, fact revisions, confirmations, volatility state, stale
  reads, questions, and answers are governed through API and audit contracts.
- `facts_used` evidence binds drafts to exact fact revisions and fails closed
  when relevant knowledge changes before execution.
- Contract and integration tests prove the generic behavior with synthetic data.

## 4. Governing References

ES-005 is governed by:

- `AGENTS.md`
- `PROJECT.md`
- `ROADMAP.md`
- `docs/specifications/product-requirements.md`
- `docs/architecture/03-system-context.md`
- `docs/architecture/04-container-architecture.md`
- `docs/architecture/05-component-architecture.md`
- `docs/architecture/07-security-architecture.md`
- `docs/architecture/08-data-architecture.md`
- `docs/architecture/09-agent-runtime.md`
- `docs/architecture/10-connector-framework.md`
- `docs/architecture/11-observability.md`
- `docs/architecture/13-human-approvals.md`
- `docs/decisions/ADR-002-human-approvals-decision-integrity.md`
- `docs/decisions/ADR-003-governed-external-approval-decision-channel.md`
- `docs/decisions/ADR-004-governed-external-product-client-contract.md`
- `docs/decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md`
- `docs/implementation-plans/phase-5-adr-assessment.md`
- canonical engineering governance under `docs/governance/`

If implementation pressure conflicts with these references, the Work Order must
be corrected or a new ADR must be accepted before code proceeds.

## 5. Approved Scope if Accepted

### 5.1 Agent registry and runtime contracts

- Define persisted agent registration metadata.
- Define agent descriptors, capabilities, risk level, health, status, version,
  allowed tools, required connectors, and configuration schema references.
- Add controlled runtime contract interfaces without adding a Gmail agent.
- Preserve registry separation from connector credentials and execution tools.

### 5.2 Run lifecycle and job intake

- Define generic run records, run steps, run status transitions, trigger source,
  correlation identity, idempotency, cancellation, timeout, and retry metadata.
- Connect manual and scheduled run requests to the existing queue foundation.
- Keep queue payloads reference-based and free of sensitive content.
- Do not execute live agent tools or provider actions.

### 5.3 Governed knowledge facts

- Implement fact CRUD behavior over the Phase 3 knowledge persistence
  foundation.
- Preserve immutable fact revisions.
- Support confirmation, volatility, stale volatile fact reads, soft deletion,
  source provenance, validation, audit, and authorization.
- Reject or minimize prohibited values before persistence.

### 5.4 Knowledge questions and answers

- Implement first-class question and answer lifecycle contracts.
- Keep questions and answers separate from approvals and approval
  clarification.
- Validate human answers before converting them into fact changes.
- Emit safe notification events for pending questions and answered questions.

### 5.5 Approval decision API and manual handling

- Implement generic pending-approval queue reads, evidence reads, decision
  submission, approve/reject behavior, concurrency controls, expiry behavior,
  and exact-content binding.
- Implement edit-then-approve as a governed supersession workflow.
- Implement manual-handling records and reads for suppressed items that are not
  approvals.
- Preserve channel provenance for `Internal` and `External` decision paths.

### 5.6 Facts-used evidence and revalidation

- Add typed `facts_used` evidence items inside the approval evidence payload.
- Bind each item to an exact fact revision or integrity identity.
- Revalidate bound fact state before execution continuation.
- Fail closed if fact deletion, volatility staleness, or revision change
  invalidates the approved draft.

### 5.7 Webhook and audit contracts

- Emit authenticated webhook notifications for approval pending, approval
  decided, message held for manual handling, knowledge question pending,
  knowledge question answered, fact reconfirmation required, and run state
  transitions where needed.
- Keep webhook payloads minimum necessary and non-authoritative.
- Record durable audit events for material state changes and denied attempts.
- Preserve existing log redaction and correlation conventions.

### 5.8 Verification and closeout

- Add contract tests for all API schemas, state transitions, authorization
  negative paths, idempotency, concurrency, audit events, and webhook payloads.
- Add an integration closeout smoke path using synthetic data only.
- Update API documentation, work-order status, implementation reports, and
  residual-risk records.

## 6. Explicitly Out of Scope

ES-005 does not authorize:

- Gmail OAuth, Gmail API calls, Gmail message reads, drafting, sending, labels,
  history learning, or provider credentials.
- Live external webhook delivery.
- Production deployment or live Render/Netlify resource provisioning.
- Multi-user, RBAC, multi-tenant, delegation, quorum, multiple reviewers, or
  multiple external product clients.
- MushingMule-specific route names, schemas, tables, or product concepts.
- LangChain, LangGraph, Temporal, or a new orchestration framework.
- LLM provider integration or model prompt implementation.
- Policy Engine implementation beyond contract checks required by generic
  approval, knowledge, and manual-handling behavior.
- Frontend productization except for API contract compatibility documentation.

## 7. Data Requirements

Implementation must satisfy these data constraints:

- PostgreSQL remains the runtime system of record.
- Every persisted table has stable identifiers and UTC timestamps.
- Mutable business state and immutable evidence-bearing revisions remain
  separate.
- Deletion uses soft-delete or inactive-state semantics when audit or evidence
  retention matters.
- Questions, answers, approvals, approval clarification, manual-handling
  records, and facts remain distinct persisted concepts.
- Queue, webhook, and audit payloads store references and minimized metadata,
  not full sensitive source content.
- Idempotency keys are persisted for state-changing external or retryable
  operations where duplicate execution would change state.
- Retention fields may be added, but final retention periods require separate
  release or security review if not already accepted.

## 8. Security and Privacy Requirements

Implementation must satisfy these controls:

- Authentication required by default.
- Authorization denied by default for every operation until explicitly granted.
- External-client authentication is distinct from human-owner attribution.
- The single human owner/reviewer constraint is preserved.
- Webhook notifications do not authorize or prove state reconciliation.
- Approval decisions fail closed when evidence, state, expiry, revision, actor,
  channel, or audit requirements are invalid.
- Knowledge inputs reject secrets, credentials, protected health information,
  and content derived from clinically suppressed sources.
- API responses, logs, webhooks, audit metadata, and test fixtures must not
  expose secrets, OAuth tokens, credentials, full email bodies, or prohibited
  values.
- State-changing requests must define idempotency or explicitly document why
  idempotency is unnecessary.

## 9. API Requirements

Phase 5 API work must use the Phase 3 contract foundation:

- `/api/v1` route namespace for operational routes.
- `{ "data": ..., "meta": ... }` success envelopes where applicable.
- `{ "error": { "code", "message", "correlation_id", "details"? } }` errors.
- opaque cursor pagination for list endpoints.
- explicit filtering and sorting allowlists.
- `Idempotency-Key` on state-changing endpoints that can be retried.
- OpenAPI tags, examples, security declarations, and schema tests.

The exact route map belongs in the implementation Work Orders. Route names must
remain generic and must not encode Gmail or MushingMule as platform concepts.

## 10. Validation Requirements

Each implementing Work Order must define focused validation. The Phase 5 package
as a whole must pass:

- backend unit tests;
- backend integration tests using PostgreSQL;
- API contract and OpenAPI tests;
- authorization negative-path tests;
- idempotency and concurrency tests for state-changing flows;
- webhook signature and minimized-payload tests;
- audit persistence and rollback/failure tests;
- redaction and prohibited-content regression tests;
- `ruff`, `mypy`, and repository formatting checks;
- GitHub CI before merge.

## 11. Rollback Expectations

Each Work Order must identify rollback boundaries. Database migrations must be
reviewable and reversible where practical. If a migration cannot safely
downgrade without data loss, the Work Order must say so before implementation
and provide a compensating rollback plan.

Because this phase creates contract foundations, rollback must preserve API
compatibility for already-merged generic contracts or explicitly mark a
contract as not yet released.

## 12. Stop-and-Ask Triggers

Stop and request Repository Maintainer direction before proceeding if:

- implementation needs Gmail credentials, live provider calls, live external
  webhooks, or production infrastructure;
- a new architecture, security, data, framework, deployment, or multi-user
  decision appears necessary;
- the work would introduce Gmail-specific or MushingMule-specific platform
  concepts;
- the single-owner, single-reviewer, or single-external-client boundary would
  change;
- tests reveal an approval authorization bypass, audit loss, sensitive-data
  exposure, or fail-open behavior;
- a Work Order needs broader scope than ES-005 allows.

## 13. Acceptance Criteria

ES-005 is ready for implementation only when:

- the Repository Maintainer accepts this specification;
- `docs/implementation-plans/phase-5-adr-assessment.md` confirms sufficient ADR
  coverage or any required ADRs are accepted;
- Phase 5 Work Orders are accepted with explicit dependencies and validation;
- ADP-002 is accepted if uninterrupted multi-Work-Order execution is desired;
- no unresolved Definition of Ready blocker remains.

## 14. Review Notes

This specification is proposed planning authority only. It should be reviewed
before any Phase 5 implementation begins.
