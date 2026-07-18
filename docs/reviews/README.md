# Reviews

This directory contains durable review, handoff, and verification records migrated during ES-000.

The Work Order 005 handoff records the final approved application-shell implementation and its three post-review refinements. Accepted design decisions remain canonical under `docs/design/decisions/`; an identical duplicate of DDR-002 from the source review folder was not retained here.

The ES-002 frontend-testing report records the implementation and validation evidence for the approved component-testing baseline.

The Work Order 006 review report records the implementation and validation evidence for the frontend-only Agents Inventory.

The Human Approvals review records preserve the approval basis for ES-003 and
WO-009. The WO-009 design-direction reconciliation and alternate-design mapping
record the completed item-by-item review, and the WO-009 implementation report
records final conformance, validation, evidence, and closeout.

The WO-010, WO-011, and WO-012 authorization reviews record the approved scope,
prototype boundaries, Definition-of-Ready evidence, and required verification
for the remaining Atlas frontend pages.

The WO-011 implementation report records conformance, automated validation,
browser evidence, known limitations, and the governed merge gate for Alerts and
Audit.

The WO-012 implementation report records the final placeholder replacement for
Connectors, Policies, and Settings, including simulation safety, accessibility,
responsive evidence, validation, and the governed merge gate.

The WO-010 implementation report records the completed Runs and Artifacts
delivery. The WO-013 and WO-014 authorization and implementation reports record
the final indicator, responsive-header, simulation-language, title-metadata,
and mobile-action-flow consistency work.

The [ADR-004 review record](./ADR-004-governed-external-product-client-contract-review.md)
records Architecture and Security Review acceptance of the governed external
product client contract. It carries no implementation authority.

The [ADR-005 review record](./ADR-005-draft-support-knowledge-and-ask-instead-of-guess-review.md)
records Architecture and Security Review acceptance of governed draft-support
knowledge and ask-instead-of-guess behavior. It carries no implementation
authority.

The [ES-004 review record](./ES-004-platform-foundation-review.md) records
acceptance of the Phase 3 backend Platform Foundation Engineering
Specification and WO-015 implementation authority.

The [ES-006 review record](./ES-006-gmail-agent-mvp-candidate-review.md)
records acceptance of the Phase 6 Gmail Agent MVP Candidate package, including
OAuth scope posture, WO-036 through WO-044 readiness, ADP-003 guardrails, and
bounded implementation authority.

The [WO-036 implementation report](./WO-036-gmail-oauth-scopes-and-connector-boundary-implementation-report.md)
records the Gmail and Drive connector OAuth boundary, exact scope enforcement,
fake provider lifecycle, credential-reference handling, local validation
evidence, and residual risks.

The [WO-015 implementation report](./WO-015-platform-foundation-implementation-report.md)
records the FastAPI backend foundation, persistence model, migration,
external-client authentication scaffold, webhook delivery scaffold, validation
evidence, and remaining limitations.

The [WO-016 infrastructure provisioning strategy review](./WO-016-infrastructure-provisioning-strategy-review.md)
records the provider-native provisioning strategy, environment model,
PostgreSQL placement, secrets/configuration ownership, backup and rollback
expectations, ADR assessment, and residual risks.

The [WO-017 runtime hardening implementation report](./WO-017-runtime-hardening-implementation-report.md)
records the constraints-based backend dependency workflow, explicit settings
validation, documentation and CI alignment, validation evidence, and the
remaining PostgreSQL environment work for WO-018.

The [WO-018 PostgreSQL hardening implementation report](./WO-018-postgresql-hardening-implementation-report.md)
records the required database URL boundary, ephemeral PostgreSQL 18 CI service,
local command path, validation evidence, and the remaining authentication work
for WO-019.

The [WO-019 owner session implementation report](./WO-019-owner-session-implementation-report.md)
records the provider-neutral verified-identity boundary, opaque hashed session
lifecycle, CSRF/cookie controls, validation evidence, and the remaining
authorization work for WO-020.
