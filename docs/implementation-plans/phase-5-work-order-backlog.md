# Phase 5 Work Order Backlog

**Status:** Accepted - Phase 5 Execution Authorized
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Engineering Specification:** `docs/engineering-specifications/ES-005-agent-framework-and-governance-contracts.md`
**ADR Assessment:** `docs/implementation-plans/phase-5-adr-assessment.md`
**Implementation Authorization:** Granted for WO-027 through WO-035 under ADP-002

---

## 1. Purpose

Define the proposed Work Order sequence for Phase 5 Agent Framework and
Governance Contracts.

This backlog is planning guidance only until the Engineering Specification and
individual Work Orders are accepted. Each Work Order remains the bounded
implementation authority for its own scope, exclusions, validation, rollback,
and stop-and-ask triggers.

## 2. Work Order Map

| Work Order | Name | Depends On | Parallelizable | Status |
| --- | --- | --- | --- | --- |
| WO-027 | Agent Registry and Runtime Contracts | ES-005 accepted | Limited | Implemented Locally - Pending PR/CI/Merge |
| WO-028 | Run Lifecycle and Job Intake Contracts | WO-027 | Limited | Accepted |
| WO-029 | Governed Knowledge Fact Contracts | ES-005 accepted, WO-021, WO-025 | Yes, after dependencies | Accepted |
| WO-030 | Knowledge Question and Answer Lifecycle | WO-029 | Limited | Accepted |
| WO-031 | Approval Decision and Manual-Handling Contracts | ES-005 accepted, WO-021, WO-025 | Yes, after dependencies | Accepted |
| WO-032 | Facts-Used Evidence and Revalidation Contracts | WO-029, WO-031 | No | Accepted |
| WO-033 | Webhook and Audit Event Contract Expansion | WO-029, WO-030, WO-031 | Yes, after event producers exist | Accepted |
| WO-034 | Phase 5 Dashboard Contract Compatibility Pass | WO-027, WO-028, WO-029, WO-031 | Yes, after stable API schemas | Accepted |
| WO-035 | Phase 5 Contract Integration Verification and Closeout | WO-027 through WO-034 | No | Accepted |

## 3. Dependency Waves

| Wave | Work Orders | Purpose | Parallel posture |
| --- | --- | --- | --- |
| Wave 0 | ES-005, ADR assessment, WO acceptance | Governance readiness | Documentation review can happen in parallel; implementation waits |
| Wave 1 | WO-027, WO-029, WO-031 | Establish the major independent contract domains | Can run in parallel after ES-005 acceptance if file boundaries are respected |
| Wave 2 | WO-028, WO-030, WO-033, WO-034 | Build dependent lifecycle, questions, events, and dashboard compatibility | Can split by domain after Wave 1 schemas stabilize |
| Wave 3 | WO-032 | Bind knowledge to approval evidence and revalidation | Serial because it depends on knowledge and approval semantics |
| Wave 4 | WO-035 | Cross-domain verification and closeout | Serial closeout |

## 4. Proposed Work Orders

### WO-027 - Agent Registry and Runtime Contracts

Work Order:

- `docs/work-orders/027-agent-registry-and-runtime-contracts.md`

Objective:

- Define and implement generic agent registration, descriptor, status, health,
  and runtime contract foundations without Gmail behavior.

Likely scope:

- agent registry tables and models;
- descriptor schemas and validation;
- agent status and health routes;
- runtime protocol/interface boundaries;
- authorization and audit for registry reads/changes;
- no connector credentials, tools, or provider execution.

### WO-028 - Run Lifecycle and Job Intake Contracts

Work Order:

- `docs/work-orders/028-run-lifecycle-and-job-intake-contracts.md`

Objective:

- Define and implement generic run lifecycle records and queue-backed job
  intake for manual and scheduled triggers.

Likely scope:

- run and run-step persistence;
- manual run request contract;
- schedule-to-run queue handoff contract;
- cancellation and timeout metadata;
- idempotency for run creation;
- no real agent tool execution.

### WO-029 - Governed Knowledge Fact Contracts

Work Order:

- `docs/work-orders/029-governed-knowledge-fact-contracts.md`

Objective:

- Implement governed fact CRUD, immutable revisions, confirmation, volatility,
  stale reads, soft deletion, validation, authorization, and audit contracts.

Likely scope:

- fact CRUD endpoints;
- fact revision creation;
- confirmation and volatility fields;
- stale volatile fact query;
- prohibited-content validation and minimized audit metadata;
- no Gmail history learning.

### WO-030 - Knowledge Question and Answer Lifecycle

Work Order:

- `docs/work-orders/030-knowledge-question-and-answer-lifecycle.md`

Objective:

- Implement first-class knowledge questions and answers as non-authorizing
  records separate from approvals.

Likely scope:

- question create/read/list/cancel behavior;
- answer submission and validation;
- answer-to-fact creation/update pathway;
- lifecycle states, duplicate handling, and audit;
- no approval clarification reuse.

### WO-031 - Approval Decision and Manual-Handling Contracts

Work Order:

- `docs/work-orders/031-approval-decision-and-manual-handling-contracts.md`

Objective:

- Implement generic approval queue, evidence read, approve/reject,
  edit-then-approve, and manual-handling contracts.

Likely scope:

- approval request persistence if not already sufficient;
- pending queue and evidence read APIs;
- decision submission with concurrency, expiry, idempotency, channel provenance,
  and audit;
- edit-then-approve supersession workflow;
- manual-handling records and reads;
- no Gmail draft or send execution.

### WO-032 - Facts-Used Evidence and Revalidation Contracts

Work Order:

- `docs/work-orders/032-facts-used-evidence-and-revalidation-contracts.md`

Objective:

- Bind approval evidence to exact knowledge fact revisions and fail closed when
  facts change, are deleted, or become stale before execution continuation.

Likely scope:

- typed `facts_used` evidence items;
- decision-context manifest binding;
- revalidation service;
- failure reasons and audit events;
- contract tests across knowledge and approval domains.

### WO-033 - Webhook and Audit Event Contract Expansion

Work Order:

- `docs/work-orders/033-webhook-and-audit-event-contract-expansion.md`

Objective:

- Add signed, minimum-necessary webhook notification contracts and durable audit
  events for Phase 5 approval, manual-handling, knowledge, and run events.

Likely scope:

- event type registry;
- minimized payload schemas;
- webhook enqueue points using the existing delivery foundation;
- audit action names and metadata contracts;
- fake-transport tests only.

### WO-034 - Phase 5 Dashboard Contract Compatibility Pass

Work Order:

- `docs/work-orders/034-phase-5-dashboard-contract-compatibility-pass.md`

Objective:

- Align existing dashboard expectations with stable Phase 5 API contracts
  without completing full dashboard productization.

Likely scope:

- document route/schema compatibility for agents, runs, approvals, audit,
  manual handling, and knowledge;
- replace or mark fixture-only assumptions that conflict with backend
  contracts;
- add typed API client stubs or contract fixtures where useful;
- no full Phase 4 dashboard release claim.

### WO-035 - Phase 5 Contract Integration Verification and Closeout

Work Order:

- `docs/work-orders/035-phase-5-contract-integration-verification-and-closeout.md`

Objective:

- Verify Phase 5 as one coherent generic contract layer using synthetic data
  and produce closeout evidence for Phase 6 entry.

Likely scope:

- integration smoke path across registry, run, knowledge, approval,
  `facts_used`, webhook, audit, and authorization;
- security/privacy negative tests;
- documentation/status alignment;
- residual-risk register and Phase 6 entry criteria.

## 5. Stop-and-Ask Triggers

Stop before implementation if:

- ES-005 is not accepted;
- a Work Order is not accepted;
- ADR assessment finds unresolved architecture or security decisions;
- live credentials, live provider calls, live webhooks, or production resources
  are required;
- implementation would add Gmail-specific behavior;
- implementation would change single-owner, single-reviewer, or single-client
  boundaries.
