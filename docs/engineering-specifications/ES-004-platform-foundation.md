# ES-004 - Platform Foundation

**Status:** Accepted - Implementation Authorized Through WO-015
**Owner:** Repository Maintainer
**Review Owner:** Repository Maintainer
**Date:** 2026-07-17
**Version:** 0.1
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Implementation Authorization:** Granted through WO-015
**Target Release:** Not Assigned
**Related Work Order:** `docs/work-orders/015-platform-foundation.md`
**Review Record:** `docs/reviews/ES-004-platform-foundation-review.md`
**Related ADRs:** `docs/decisions/ADR-003-governed-external-approval-decision-channel.md`, `docs/decisions/ADR-004-governed-external-product-client-contract.md`, `docs/decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md`

---

## 1. Purpose

Define the first backend platform foundation increment for Atlas.

ES-004 translates the accepted architecture for the Backend API, PostgreSQL
system of record, external product client boundary, webhook delivery, and
governed knowledge persistence into a bounded implementation plan.

This specification intentionally builds foundations only. It does not deliver
full operational approvals, fact CRUD semantics, ask-instead-of-guess behavior,
Gmail integration, connector execution, or production deployment.

## 2. Engineering Decision

ES-004 establishes a FastAPI backend workspace with PostgreSQL migrations,
configuration loading, health checks, authentication scaffolding, an external
client boundary, outbound webhook delivery scaffolding, and the initial
governed knowledge persistence model.

The first backend increment must keep Atlas architecture-first and testable:

- Backend foundations are implemented in a new Python application boundary.
- PostgreSQL schema is introduced through migrations, not ad hoc SQL.
- Runtime secrets remain environment-sourced and are never committed.
- External-client authentication and human attribution remain separate.
- Webhook delivery is a notification mechanism only.
- Knowledge persistence is version-ready, but Phase 5 owns the governed CRUD,
  confirmation, volatility, question, answer, evidence, and revalidation
  contracts.

## 3. Intended Outcome

After ES-004 is implemented, Atlas has a reviewable backend foundation that can
support later Platform, Agent Framework, and Gmail Agent increments:

- A FastAPI app can start locally and expose health endpoints.
- PostgreSQL migrations define the initial platform foundation tables.
- Configuration, environment validation, structured errors, and correlation
  IDs have stable conventions.
- The external product client has an authenticated API boundary scaffold.
- Webhook delivery records can be persisted and retried by later work.
- Governed knowledge facts, revisions, questions, and answers have persistence
  foundations without authorizing full behavior.

## 4. Governing References

ES-004 is governed by:

- `AGENTS.md`
- `PROJECT.md`
- `ROADMAP.md`
- `docs/specifications/product-requirements.md`
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
- Canonical engineering governance under `docs/governance/`

If implementation pressure conflicts with these references, the Work Order must
be corrected or a new ADR must be accepted before code proceeds.

## 5. Approved Scope

This specification covers the following foundation areas.

### 5.1 Backend application foundation

- Create a Python backend application boundary using FastAPI.
- Provide app startup, dependency wiring, routing conventions, and structured
  error handling.
- Add health endpoints for liveness and readiness.
- Add a request correlation ID convention and ensure responses include the
  correlation identity.
- Add local development commands and tests for the backend.
- Keep the backend independent from frontend runtime code.

### 5.2 Configuration and secret handling

- Define typed configuration loading for local development and future Render
  deployment.
- Require environment variables for secrets and connection strings.
- Fail startup when required configuration is absent for a selected runtime
  mode.
- Prevent secret values from appearing in logs, errors, fixtures, tests, or
  committed files.

### 5.3 PostgreSQL and migrations

- Introduce SQLAlchemy and Alembic or an equivalent direct Python migration
  stack consistent with the architecture.
- Add migrations for the foundation tables required by this increment.
- Preserve UTC timestamp conventions.
- Use stable identifiers for persisted runtime objects.
- Keep migrations deterministic and reviewable.

### 5.4 Initial persistence domains

Define the minimum persistence foundation for:

- Users and owner identity metadata.
- External product clients and authentication metadata.
- Audit event envelopes.
- Outbound webhook subscriptions.
- Outbound webhook delivery attempts.
- Governed knowledge facts.
- Governed knowledge fact revisions.
- Governed knowledge questions.
- Governed knowledge answers.

The knowledge tables are schema foundations only. Phase 5 owns the full API
contract, validation semantics, fact confirmation workflow, staleness policy,
answer resolution behavior, and facts-used evidence behavior.

### 5.5 API foundation

- Establish versioned API routing conventions.
- Add structured response and error envelopes where appropriate.
- Add authentication dependency scaffolding for first-party dashboard calls and
  external product client calls.
- Add deny-by-default authorization placeholders that fail closed until a later
  Work Order explicitly grants behavior.
- Add OpenAPI metadata that accurately marks implemented and placeholder
  endpoints.

### 5.6 External product client boundary

- Persist external client registration metadata needed for later authenticated
  access.
- Separate client authentication identity from attribution to the single human
  owner and reviewer.
- Add signed or keyed authentication verification scaffolding for external
  client requests.
- Record enough audit metadata to identify the external client and request
  channel.
- Do not expose MushingMule-specific concepts in schemas, route names, or table
  names.

### 5.7 Webhook delivery foundation

- Persist webhook subscriptions and delivery attempts.
- Add outbound delivery service interfaces and tests using local fake
  transports.
- Support correlation IDs, event type, delivery status, attempt count, next
  retry time, and minimized payload storage.
- Preserve authenticated-notification semantics. A webhook event must never be
  treated as authorization or proof that the receiver reconciled state.

### 5.8 Observability and audit foundation

- Add structured logging conventions for backend requests and service events.
- Add audit event envelope persistence for material platform events introduced
  by this increment.
- Redact or omit secret and prohibited content values.
- Add test coverage for correlation IDs, error shape, and redaction behavior.

## 6. Explicitly Out of Scope

ES-004 does not authorize:

- Full fact CRUD endpoint semantics.
- Fact confirmation, volatility, re-confirmation, or staleness behavior.
- Knowledge question creation by an agent.
- Knowledge answer validation or fact learning behavior.
- `facts_used` approval evidence extension.
- Approval decision APIs or approval execution.
- Gmail OAuth, Gmail connector behavior, drafting, sending, or history learning.
- Clinical or protected-health-information classifier implementation.
- Policy Engine implementation.
- Agent Runtime, Scheduler, Worker, or Queue implementation beyond interfaces
  needed for the backend foundation.
- Production deployment, Render infrastructure provisioning, or live database
  creation.
- Multi-user, multi-tenant, multi-client, delegation, quorum, or role expansion.
- Frontend integration with the backend.

## 7. Data Requirements

Implementation must satisfy these data constraints:

- PostgreSQL is the only runtime system-of-record target for the new backend
  persistence model.
- Every persisted table has stable identifiers and UTC timestamps.
- Knowledge facts and fact revisions are distinct records.
- Revisions are immutable after creation except for metadata needed to correct a
  migration or data-integrity defect through a later approved process.
- Questions and answers are distinct from approvals and approval clarification.
- Deletion semantics are represented without destroying evidence-relevant
  revision history.
- Prohibited content categories are represented through safe reason codes, not
  retained prohibited values.
- Retention fields or placeholders exist where later Phase 5 policy needs them,
  but this increment does not select final retention periods.

## 8. Security and Privacy Requirements

Implementation must satisfy these controls:

- Authentication required by default.
- Authorization denied by default for unimplemented operations.
- External-client authentication is separate from human-owner attribution.
- Secrets, API keys, webhook secrets, tokens, and database credentials are
  environment-sourced.
- No secret values are returned by API responses or logged.
- State-changing requests include an idempotency strategy or an explicit
  explanation for why the endpoint is read-only or non-mutating.
- Prohibited knowledge values are rejected or represented by minimized metadata
  before persistence.
- Webhook payloads are minimum necessary.
- All externally supplied values are treated as untrusted and validated before
  use.

## 9. API Requirements

The implementation may expose only foundation endpoints:

- `GET /health/live`
- `GET /health/ready`
- `GET /api/v1/health`
- Authentication probe endpoints only when they do not imply production-ready
  login or authorization behavior.
- Placeholder knowledge, webhook, or external-client routes only when they fail
  closed with explicit `501 Not Implemented` or equivalent structured errors.

Any operational endpoint that creates, updates, deletes, confirms, answers, or
authorizes a domain object requires a later approved Work Order unless it is
strictly necessary to complete this foundation and is called out in the Work
Order acceptance criteria.

## 10. Verification Requirements

The implementing Work Order must provide evidence for:

- Python dependency installation.
- Backend unit tests.
- Migration creation and downgrade/upgrade validation against a local
  PostgreSQL-compatible environment or a documented local substitute.
- Secret scanning over the changed backend and documentation files.
- Frontend baseline checks remain green where the root CI still requires them:
  `npm run typecheck`, `npm run lint`, `npm test`, and `npm run build`.
- Backend health endpoint behavior.
- Structured error and correlation ID behavior.
- Webhook delivery fake-transport tests.
- Knowledge persistence model tests.

## 11. Acceptance Criteria

ES-004 was accepted for implementation on 2026-07-17 because:

- This specification and `WO-015` are reviewed and approved by the repository
  maintainer.
- The Work Order names concrete file scope and excludes Phase 5/6 behavior.
- The selected Python dependency and migration approach are documented.
- The verification plan is executable locally.
- Security, privacy, data, and integration impacts are explicit.
- Any unresolved runtime or deployment decision is assigned to a future ADR,
  Engineering Specification, or Work Order.

## 12. Risks and Controls

| Risk | Control |
| --- | --- |
| Phase 3 grows into full platform behavior | Work Order scope must stop at foundations and fail-closed placeholders |
| External client authentication becomes human authorization | Persist and audit client identity separately from human attribution |
| Knowledge tables imply safe fact usage before policies exist | Keep APIs placeholder-only until Phase 5 defines validation and lifecycle contracts |
| Webhooks are mistaken for authority | Treat webhook delivery as notification only and require later API reconciliation |
| Backend secrets leak during setup | Environment-only secrets, redaction tests, and secret scans |
| New Python stack bypasses existing CI | Work Order must update validation scripts and CI intentionally |

## 13. Completion Criteria

ES-004 is complete when an approved Work Order implements the foundation,
records review evidence, passes required local and CI validation, and merges
through the governed pull-request process.

This specification authorizes implementation only through the bounded WO-015
scope.
