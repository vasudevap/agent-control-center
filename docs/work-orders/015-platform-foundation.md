# Work Order 015: Platform Foundation

**Status:** Completed Pending Merge
**Work Order ID:** WO-015
**Type:** Backend platform foundation
**Implementation Authorization:** Granted
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Governing Engineering Specification:** [ES-004 Platform Foundation](../engineering-specifications/ES-004-platform-foundation.md)
**Architecture Authority:** [Container Architecture](../architecture/04-container-architecture.md), [Security Architecture](../architecture/07-security-architecture.md), [Data Architecture](../architecture/08-data-architecture.md), [Human Approvals Architecture](../architecture/13-human-approvals.md)
**Decision Authority:** [ADR-003](../decisions/ADR-003-governed-external-approval-decision-channel.md), [ADR-004](../decisions/ADR-004-governed-external-product-client-contract.md), [ADR-005](../decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md)
**Review Authority:** [ES-004 Review](../reviews/ES-004-platform-foundation-review.md)
**Review Owner:** Repository Maintainer

---

## 1. Purpose

Implement the first backend platform foundation for Atlas after the accepted
ADR-005 governance milestone.

This Work Order prepares the repository for backend implementation while
preserving the architecture boundary between foundation plumbing and later
operational behavior.

## 2. Objective and User Outcome

The repository gains a production-shaped backend foundation that a maintainer
can run, test, migrate, and review locally. The foundation supports later
implementation of governed external APIs, webhook delivery, approvals,
knowledge contracts, and the Gmail Agent without coupling Atlas to a
client-specific product model.

## 3. Approved Scope

Implementation is limited to the following accepted scope.

### 3.1 Backend workspace

- Create a backend application boundary under the existing repository
  structure.
- Add FastAPI app startup, routing, dependency wiring, and health endpoints.
- Add typed configuration loading and safe startup validation.
- Add structured error handling and request correlation ID handling.
- Add backend unit-test infrastructure.

### 3.2 Persistence and migrations

- Add a Python database stack and migration tool consistent with ES-004.
- Add initial migrations for users, external clients, audit event envelopes,
  webhook subscriptions, webhook delivery attempts, knowledge facts, knowledge
  fact revisions, knowledge questions, and knowledge answers.
- Add tests or migration checks proving the migration path is executable.

### 3.3 External client and webhook foundations

- Add external-client authentication scaffolding that fails closed by default.
- Persist external-client identity metadata without attributing it as the human
  owner.
- Add outbound webhook subscription and delivery-attempt persistence.
- Add local fake-transport tests for webhook delivery behavior.

### 3.4 Knowledge persistence foundation

- Add schema and model foundations for governed facts, revisions, questions,
  and answers.
- Preserve version-ready and provenance-ready fields.
- Keep operational APIs placeholder-only unless explicitly required for health
  or test scaffolding.

### 3.5 Repository integration

- Add backend scripts or documented commands for local install, test, lint, and
  migration validation.
- Update root package or CI configuration only when required to keep the
  repository validation path accurate.
- Update README, PROJECT, and relevant docs if implementation changes the
  current baseline.

## 4. Explicitly Out of Scope

WO-015 does not authorize:

- Full `/api/knowledge` CRUD behavior.
- Fact confirmation, volatility, staleness, or re-confirmation workflows.
- Knowledge question creation from an agent run.
- Knowledge answer validation, learning, or fact updates.
- Approval APIs, decision APIs, execution, or runtime continuation.
- `facts_used` evidence payloads or decision-context manifest changes.
- Gmail OAuth, Gmail connector behavior, drafting, sending, or learning.
- Policy Engine implementation.
- Scheduler, worker, queue, or connector runtime implementation.
- Frontend integration with the backend.
- Production Render deployment or live database provisioning.
- MushingMule-specific routes, tables, fields, or terminology.
- Multiple users, multiple reviewers, multiple product clients, tenants,
  delegation, quorum, or role expansion.

## 5. Required File Scope

The implementing engineer may create or modify:

- A backend application workspace under the existing repository structure.
- Python dependency, lint, typecheck, and test configuration needed for that
  backend workspace.
- Migration configuration and migration files.
- Backend unit and migration tests.
- Root scripts or CI workflow files required to run the new backend validation.
- `README.md`, `PROJECT.md`, `ROADMAP.md`, and canonical documentation needed
  to reflect the new backend foundation.
- A review or implementation report under `docs/reviews/`.

No frontend source files are in scope unless a documentation or test command
requires a narrow repository-integration change.

## 6. Functional Requirements

- Health endpoints return structured status without exposing secrets.
- Readiness indicates whether required runtime dependencies are configured for
  the selected mode.
- Every API response that represents an error includes a correlation ID.
- Unimplemented operational routes fail closed and do not mutate state.
- External-client authentication scaffolding rejects absent or invalid
  credentials.
- Webhook delivery attempts can be represented without sending live network
  traffic in tests.
- Knowledge persistence models enforce fact/revision/question/answer
  separation.

## 7. Security and Privacy Requirements

- No secrets, `.env` files, tokens, API keys, credentials, or generated local
  database files may be committed.
- Logs and errors must not include secret values.
- External-client identity must not be treated as human reviewer identity.
- Knowledge content is treated as untrusted input.
- Prohibited-content handling must store reason metadata only, not prohibited
  values.
- Webhook payloads must be minimized and must not include authorization
  semantics.

## 8. Verification Plan

The implementation PR must include evidence for:

- Backend unit tests.
- Migration upgrade validation and, where supported, downgrade validation.
- Backend lint and type checks if introduced.
- `npm run typecheck`
- `npm run lint`
- `npm test`
- `npm run build`
- Secret scan over changed backend and documentation files.
- Local health endpoint behavior.
- Structured error/correlation ID behavior.
- Webhook fake-transport behavior.
- Knowledge persistence model behavior.

If a check cannot run locally because a dependency is unavailable, the PR must
record the exact blocker, the command attempted, and the compensating evidence.

## 9. Acceptance Criteria

WO-015 is complete only when:

- ES-004 and this Work Order are accepted by the repository maintainer.
- The backend foundation exists and can be run locally.
- Initial migrations define the approved foundation tables.
- Health endpoints, structured errors, and correlation IDs are tested.
- External-client authentication scaffolding fails closed.
- Webhook delivery persistence and fake-transport tests are present.
- Knowledge persistence foundations exist without operational Phase 5 behavior.
- Documentation reflects the new backend baseline.
- Required local checks and GitHub CI pass.
- A review or implementation report records scope, validation, risks, and
  remaining follow-up work.
- The branch merges through the approved pull-request process.

## 10. Review Notes

This Work Order has been implemented on a short-lived branch. Completion is
final when the implementation report, required validation, GitHub CI, and
governed pull-request merge are complete.
