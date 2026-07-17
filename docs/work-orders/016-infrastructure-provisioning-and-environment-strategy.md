# Work Order 016: Infrastructure Provisioning and Environment Strategy

**Status:** Proposed - Review Required
**Work Order ID:** WO-016
**Type:** Architecture and infrastructure planning
**Implementation Authorization:** Not Granted
**Planning Authorization:** Not Granted Until Accepted
**Accepted:** Not Accepted
**Accepted By:** Not Accepted
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Architecture Authority:** [Container Architecture](../architecture/04-container-architecture.md), [Deployment Architecture](../architecture/06-deployment-architecture.md), [Security Architecture](../architecture/07-security-architecture.md), [Data Architecture](../architecture/08-data-architecture.md), [Technology Strategy](../architecture/12-technology-strategy.md)
**Decision Authority:** [ADR-003](../decisions/ADR-003-governed-external-approval-decision-channel.md), [ADR-004](../decisions/ADR-004-governed-external-product-client-contract.md), [ADR-005](../decisions/ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md)
**Review Owner:** Repository Maintainer

---

## 1. Purpose

Resolve the infrastructure provisioning and environment strategy before
additional Phase 3 backend implementation begins.

Atlas should enter implementation with documented decisions for provider
topology, database placement, environment boundaries, secrets ownership,
backup/restore expectations, and provisioning mechanics. Implementation agents
should provision and code against these decisions rather than discovering them
while executing later Work Orders.

## 2. Objective and User Outcome

The repository gains an accepted infrastructure planning baseline that answers:

- which platform provisions each runtime component;
- where PostgreSQL is installed or provisioned for local, test, development,
  and production use;
- whether infrastructure is managed manually, through Render Blueprint,
  Terraform, Pulumi, or another approved approach;
- how secrets and environment variables are owned;
- how backups, restore, migration, rollback, and access controls are expected
  to work at the current project stage;
- whether an `infrastructure/` repository area is introduced now or deferred.

The result should be specific enough for later implementation agents to execute
planned decisions without making architecture or infrastructure choices during
coding.

## 3. Proposed Scope

Acceptance of this Work Order would authorize planning and documentation only.

### 3.1 Provider and provisioning decision

- Confirm the current canonical target of Netlify for the dashboard and Render
  for backend runtime services unless a new ADR is required.
- Evaluate provisioning mechanism options:
  - manual provider dashboard runbook;
  - Render Blueprint;
  - Terraform;
  - Pulumi;
  - deferral with explicit revisit trigger.
- Select a preferred provisioning mechanism for the current project stage.
- Document why rejected options are deferred or rejected.
- Identify whether the selection requires a new ADR.

### 3.2 Environment model

- Define local, test, development, and production environments.
- State whether staging exists now, is explicitly deferred, or is unnecessary
  for the current phase.
- Define promotion expectations between environments.
- Define which environments are allowed to use fake transports, local-only
  credentials, or non-production test data.

### 3.3 PostgreSQL placement and lifecycle

- Define the approved local PostgreSQL path.
- Define the approved automated test database path.
- Define the expected hosted development PostgreSQL location.
- Define the expected hosted production PostgreSQL location.
- Document migration upgrade/downgrade expectations for each environment.
- Document backup, restore, destructive-operation, and retention expectations
  appropriate to the current project stage.

### 3.4 Secrets and configuration ownership

- Define where environment variables are stored for local, CI, development,
  and production.
- Define which values must never be committed.
- Define who may create or rotate provider, database, webhook, and application
  credentials.
- Define whether a dedicated secrets manager is required now or explicitly
  deferred.

### 3.5 Access control and operational guardrails

- Define minimum access controls for Netlify, Render, GitHub, and database
  administration.
- Define the expected MFA and least-privilege posture for provider accounts.
- Define production deployment approval expectations.
- Define rollback and recovery evidence required before production promotion.

### 3.6 Documentation outputs

The planning agent should create or update:

- an infrastructure provisioning strategy document under
  `docs/implementation-plans/`;
- any required ADR if the selected approach changes accepted architecture;
- the Phase 3 master plan and backlog only if this Work Order changes sequence
  or dependencies;
- `README.md`, `PROJECT.md`, or `ROADMAP.md` only if the accepted strategy
  changes project status or repository guidance.

## 4. Explicitly Out of Scope

WO-016 does not authorize:

- creating live Netlify, Render, database, storage, scheduler, worker, or
  production resources;
- provisioning production infrastructure;
- collecting or storing real secrets;
- changing backend runtime code;
- changing frontend runtime code;
- adding migrations;
- adding deployment automation;
- changing the selected Netlify and Render hosting split without an ADR;
- changing Render PostgreSQL as the planned initial hosted database location
  without an ADR;
- implementing authentication, authorization, API contracts, queue, scheduler,
  webhook delivery, observability, Phase 5 knowledge behavior, or Phase 6 Gmail
  behavior.

## 5. Required File Scope

The planning agent may create or modify:

- `docs/work-orders/016-infrastructure-provisioning-and-environment-strategy.md`
- `docs/implementation-plans/`
- `docs/decisions/` if an ADR is required
- `docs/architecture/` only if canonical architecture needs a narrow update
  consistent with accepted decisions
- `README.md`, `PROJECT.md`, and `ROADMAP.md` only if status or guidance must
  be updated
- `docs/reviews/` for a review record

The planning agent must not modify application source code, migrations,
provider configuration files, live infrastructure, or secret-bearing files.

## 6. Planning Requirements

The resulting strategy must include:

- a decision summary;
- current accepted architecture baseline;
- option matrix with trade-offs;
- selected approach and rationale;
- rejected or deferred options and revisit triggers;
- environment matrix;
- database placement matrix;
- secrets and configuration ownership;
- backup, restore, retention, rollback, and destructive-operation controls;
- provider access-control expectations;
- implementation prerequisites for WO-017 and WO-018;
- explicit statement of whether an ADR is required.

The strategy should consult current official provider documentation before
finalizing provider-specific recommendations. If network access or provider
documentation is unavailable, the planning agent must record the limitation and
avoid provider-specific assertions that cannot be verified.

## 7. Security and Privacy Requirements

- No secrets, credentials, tokens, `.env` files, provider account identifiers,
  database URLs, API keys, OAuth credentials, or private operational details may
  be committed.
- The strategy must preserve least privilege and deny by default.
- Production access must require explicit maintainer approval.
- Production deployment must remain separately authorized.
- Provider access and database administration must be treated as privileged
  operations.
- Backup and restore guidance must avoid exposing sensitive data in examples.

## 8. Verification Plan

The planning PR must include evidence for:

- `git diff --check`
- strict secret-pattern scan over changed files
- review of current canonical architecture references
- provider documentation review or an explicit limitation if unavailable
- confirmation that no application code, migrations, live provider resources,
  or secrets were changed

Frontend and backend test suites are not required unless this planning work
changes executable project files.

## 9. Acceptance Criteria

WO-016 is ready for completion only when:

- this Work Order is accepted by the repository maintainer;
- the infrastructure provisioning strategy document exists;
- the strategy clearly selects or defers the provisioning mechanism;
- the environment model is documented;
- PostgreSQL placement is documented for local, test, development, and
  production expectations;
- secrets, configuration, access controls, backups, restore, migration,
  rollback, and destructive-operation expectations are documented;
- any required ADR is proposed or accepted before dependent implementation
  proceeds;
- later Work Orders can reference the strategy rather than deciding
  infrastructure during implementation;
- validation evidence is recorded;
- a review record captures residual risks and follow-up work;
- the branch merges through the approved pull-request process.

## 10. Stop-and-Ask Triggers

The planning agent must stop and ask before proceeding if:

- provider documentation conflicts with accepted architecture;
- the selected provisioning mechanism requires a new tool, account, paid
  service, or repository structure not already accepted;
- production resources would need to be created to answer a planning question;
- real secrets, provider tokens, or database credentials are needed;
- the strategy would change Netlify, Render, or Render PostgreSQL decisions;
- the strategy would require a new top-level repository directory;
- the planning work reveals a security, privacy, cost, or operational risk that
  should be accepted explicitly before documentation proceeds.

## 11. Review Notes

This Work Order is proposed for review. It does not authorize implementation,
live provisioning, deployment, or creation of provider resources.
