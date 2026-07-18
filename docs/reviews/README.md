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

The [WO-037 implementation report](./WO-037-gmail-message-eligibility-retrieval-and-classification-implementation-report.md)
records the Gmail message eligibility, fake retrieval, minimized persistence,
classification, fail-closed review behavior, validation evidence, and residual
risks.

The [WO-038 implementation report](./WO-038-clinical-and-phi-suppression-guardrail-implementation-report.md)
records the clinical and PHI suppression guardrail, minimized manual-handling
records, webhook and audit evidence, downstream denial tests, and residual
risks.

The [WO-039 implementation report](./WO-039-low-risk-mailbox-actions-and-attachment-saving-implementation-report.md)
records low-risk Gmail label/archive and attachment-save behavior, fake
Gmail/Drive providers, idempotent action-operation evidence, suppression
denials, provider failure normalization, validation evidence, and residual
risks.

The [WO-040 implementation report](./WO-040-ask-instead-of-guess-and-governed-fact-use-implementation-report.md)
records Gmail draft-scenario required facts, ask-instead-of-guess question
creation, stale volatile fact handling, answer validation, suppressed-source
exclusion, webhook/audit evidence, and residual risks.

The [WO-041 implementation report](./WO-041-draft-generation-and-facts-used-evidence-implementation-report.md)
records fake-provider Gmail draft creation, generated-output validation,
draft persistence, exact `facts_used` evidence, decision-context bindings,
idempotency, no-send guarantees, validation evidence, and residual risks.

The [WO-042 implementation report](./WO-042-approval-gates-edit-then-approve-and-send-continuation-implementation-report.md)
records Gmail send approval creation, edit supersession compatibility, approved
send continuation, fact and draft revalidation, send outcome records,
idempotency, validation evidence, and residual risks.

The [WO-043 implementation report](./WO-043-gmail-agent-operational-reconciliation-implementation-report.md)
records Gmail Agent descriptor registration, manual and scheduled run packet
wiring, run-step summaries, minimized webhook producers, audit evidence,
dashboard/external-client compatibility, validation evidence, and residual
risks.

The [WO-044 closeout report](./WO-044-gmail-agent-mvp-candidate-closeout-report.md)
records the Gmail Agent MVP Candidate fake-provider end-to-end evidence,
security/privacy negative evidence, controlled-account test plan state,
residual risks, validation evidence, and release-decision readiness boundary.

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
