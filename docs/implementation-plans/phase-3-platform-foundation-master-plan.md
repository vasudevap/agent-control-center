# Phase 3 Platform Foundation Master Plan

**Status:** Draft - Planning Review Required
**Owner:** Repository Maintainer
**Review Owner:** Repository Maintainer
**Date:** 2026-07-17
**Planning Scope:** Phase 3 Platform Foundation
**Implementation Authorization:** Not Granted

---

## 1. Purpose

Define the complete Phase 3 implementation program before additional code is
written.

This plan coordinates the architecture, sequencing, work-order backlog,
dependency gates, verification model, and future agent execution packets needed
to implement the remaining Platform Foundation safely.

The preferred project approach is to finish implementation decisions before
implementation begins. Future agents should provision and code against accepted
architecture, infrastructure, persistence, and security decisions rather than
choosing those details while executing a Work Order.

## 2. Current Baseline

Completed baseline:

- WO-015 is complete.
- `apps/api` exists as the FastAPI backend foundation.
- Backend CI includes dependency install, mypy, Ruff, pytest, and Alembic
  upgrade/downgrade.
- The first migration defines users, external product clients, audit envelopes,
  webhook subscriptions, webhook delivery attempts, knowledge facts, knowledge
  fact revisions, knowledge questions, and knowledge answers.
- Health endpoints, structured errors, correlation IDs, fail-closed
  external-client authentication scaffolding, and local webhook fake transport
  exist.

Not yet implemented:

- Infrastructure provisioning strategy.
- Real PostgreSQL environment strategy.
- Backend dependency locking or constraints.
- Runtime logging baseline.
- Dashboard authentication sessions.
- Authorization policy checks.
- External-client credential lifecycle.
- Operational API contracts.
- Queue and scheduler.
- Runtime agent workers.
- Production deployment.
- Phase 5 knowledge behavior.
- Phase 6 Gmail agent behavior.

## 3. Phase 3 Completion Target

Phase 3 is complete when Atlas has a production-shaped platform foundation that
can support later Agent Framework and Gmail Agent work without redesign.

Target capabilities:

- Infrastructure and environment provisioning decisions are documented before
  any live resource is created.
- Backend runtime configuration and dependency management are deterministic.
- PostgreSQL is the authoritative configured persistence target, with local and
  CI migration validation.
- Health, readiness, structured errors, correlation IDs, logging, and audit
  envelopes have stable backend conventions.
- Owner-only dashboard authentication and session handling are ready for
  frontend integration.
- External product client authentication has a governed credential lifecycle.
- Authorization scaffolding denies by default and can protect all future API
  groups.
- API conventions cover versioning, pagination, idempotency, error envelopes,
  validation, and OpenAPI hygiene.
- Queue and scheduler foundations can create, claim, retry, and inspect jobs
  without executing agent business behavior.
- Webhook delivery foundations support subscription management, retry,
  signature verification, deduplication, and reconciliation status.
- Phase 3 integration verification proves the foundation works end to end at
  the platform level.

## 4. Non-Goals

Phase 3 does not implement:

- Gmail OAuth or Gmail connector operations.
- Gmail classification, archiving, labels, drafts, sending, or history
  learning.
- Full governed knowledge CRUD, confirmation, volatility, stale-fact
  re-confirmation, answer learning, or `facts_used`.
- Approval decision execution or action dispatch.
- Real agent runs beyond platform records and queue/scheduler foundations.
- Multi-user, multi-tenant, quorum, delegation, or multiple external-client
  behavior.
- Production deployment cutover unless a later accepted Work Order explicitly
  authorizes it.

## 5. Governing References

- `AGENTS.md`
- `PROJECT.md`
- `ROADMAP.md`
- `docs/architecture/03-system-context.md`
- `docs/architecture/04-container-architecture.md`
- `docs/architecture/05-component-architecture.md`
- `docs/architecture/06-deployment-architecture.md`
- `docs/architecture/07-security-architecture.md`
- `docs/architecture/08-data-architecture.md`
- `docs/architecture/09-agent-runtime.md`
- `docs/architecture/10-connector-framework.md`
- `docs/architecture/11-observability.md`
- `docs/architecture/12-technology-strategy.md`
- `docs/architecture/13-human-approvals.md`
- `docs/decisions/ADR-003-governed-external-approval-decision-channel.md`
- `docs/decisions/ADR-004-governed-external-product-client-contract.md`
- `docs/decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md`
- `docs/engineering-specifications/ES-004-platform-foundation.md`
- `docs/work-orders/015-platform-foundation.md`
- `docs/governance/definition-of-ready.md`
- `docs/governance/definition-of-done.md`
- `docs/governance/pull-request-and-review-process.md`

## 6. Implementation Strategy

Phase 3 should proceed as a sequence of small, mergeable, reviewable increments.
Each increment must have:

- one accepted Work Order;
- one short-lived branch;
- a narrow implementation scope;
- explicit exclusions;
- automated tests;
- local validation evidence;
- CI validation;
- a review or implementation report;
- a governed pull request.

Future agents should not receive broad instructions such as "implement Phase
3." They should receive one Work Order and one execution packet at a time.

Implementation packets must not ask agents to decide provider topology,
database placement, provisioning mechanism, or environment boundaries during
coding. If those choices are not already documented and accepted, the next
increment must be a planning or architecture Work Order.

## 7. Sequencing

Recommended sequence:

1. WO-016 - Infrastructure provisioning and environment strategy.
2. WO-017 - Backend runtime and dependency hardening.
3. WO-018 - PostgreSQL environment and migration hardening.
4. WO-019 - Owner authentication and session foundation.
5. WO-020 - Authorization and external-client identity boundary.
6. WO-021 - API contract foundation.
7. WO-022 - Webhook delivery hardening.
8. WO-023 - Queue foundation.
9. WO-024 - Scheduler foundation.
10. WO-025 - Observability and audit baseline.
11. WO-026 - Phase 3 integration verification and closeout.

Rationale:

- Infrastructure and environment decisions should be explicit before runtime,
  persistence, deployment, or provisioning work begins.
- Runtime and dependency determinism must come before larger backend work.
- PostgreSQL and migrations must stabilize before auth, queue, scheduler, and
  operational tables expand.
- Authentication comes before authorization.
- API conventions come before broad endpoint implementation.
- Webhook hardening can start after external-client identity is stable.
- Queue must exist before scheduler.
- Observability and audit baseline should be available before closeout and
  before Phase 5/6 expand operational behavior.

## 8. Parallelization Rules

Only parallelize after dependencies are merged to `main`.

Potential later parallel work:

- WO-022 Webhook Delivery Hardening can run in parallel with WO-023 Queue
  Foundation after WO-020 and WO-021 are merged.
- WO-025 Observability and Audit Baseline can run alongside WO-024 Scheduler
  Foundation after queue records and correlation conventions are stable.

Do not parallelize:

- WO-016 and WO-017.
- WO-017 and WO-018.
- WO-019 and WO-020.
- WO-023 and WO-024.
- Any Phase 5 knowledge contract work before Phase 3 closeout.

## 9. Architecture Decision Gates

Create an ADR before implementation if a Work Order needs to:

- change the selected Netlify and Render hosting split;
- change Render PostgreSQL as the planned initial hosted database location;
- choose an infrastructure-as-code or provisioning mechanism that materially
  changes deployment ownership or repository structure;
- replace FastAPI, SQLAlchemy, Alembic, or PostgreSQL;
- introduce Redis or another non-PostgreSQL queue as the first queue backend;
- introduce a dedicated secrets manager before deployment requirements demand
  one;
- introduce OAuth provider-specific behavior beyond the owner-only session
  foundation;
- alter the accepted single-human, single-external-client boundary;
- expand to production deployment or multi-environment infrastructure;
- move governed knowledge behavior from Phase 5 into Phase 3.

## 10. Agent Execution Model

Future implementation agents should use the packet format in
`docs/implementation-plans/agent-execution-packet-template.md`.

Agent packets must include:

- objective;
- accepted Work Order;
- governing docs;
- allowed files;
- explicit exclusions;
- sequencing dependencies;
- required checks;
- required evidence;
- stop-and-ask triggers.

The packet is not an implementation authority by itself. The accepted Work
Order remains the authority.

## 11. Phase 3 Done Criteria

Phase 3 is done only when:

- WO-016 through WO-026, or accepted replacements, are complete.
- Infrastructure provisioning and environment decisions are documented before
  live resource provisioning.
- The backend can run locally with deterministic dependency installation.
- Database migrations are validated against the approved local strategy and a
  PostgreSQL-compatible path.
- Authentication and authorization scaffolds deny by default.
- External-client access is authenticated and auditable.
- Queue and scheduler foundations exist and are tested.
- Webhook delivery foundation supports retry, deduplication, signatures, and
  reconciliation status.
- Observability and audit baselines are documented and tested.
- All scope exclusions remain untouched.
- GitHub CI passes.
- A Phase 3 closeout review records residual risks and Phase 5 handoff
  prerequisites.

## 12. Immediate Next Governance Action

Review this plan and the related Phase 3 target architecture and work-order
backlog.

Once accepted, create and accept WO-016 only. Do not batch-authorize all future
work orders at once; keep later increments independently reviewable. WO-016
should resolve infrastructure provisioning and environment strategy before
additional backend implementation begins.
