# Decisions

Accepted architecture and design decisions outrank working guidance and recommendations.

- Approved design decision records live under `docs/design/decisions/`.
- `atlas-design-decision-log.md` is the migrated index from the former Claude implementation workspace.

The migrated index is preserved for provenance and does not create new architecture decisions.

## Architecture Decisions

- [`ADR-001 - Frontend Component Testing`](./ADR-001-frontend-component-testing.md) - Accepted; selects the development-time component-testing baseline required to resolve the Work Order 006 frontend testing gap.
- [`ADR-002 - Human Approvals Decision Integrity`](./ADR-002-human-approvals-decision-integrity.md) - Accepted for a possible future approval capability; outside the active MVP.
- [`ADR-003 - Governed External Approval Decision Channel`](./ADR-003-governed-external-approval-decision-channel.md) - Superseded by ADR-008; retained as historical evidence.
- [`ADR-004 - Governed External Product Client Contract`](./ADR-004-governed-external-product-client-contract.md) - Superseded by ADR-008; retained as historical evidence.
- [`ADR-005 - Draft-Support Knowledge and Ask-Instead-of-Guess`](./ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md) - Superseded by ADR-008; retained as historical evidence.
- [`ADR-006 - Browser-Mediated Google OAuth Callback Surface`](./ADR-006-browser-mediated-google-oauth-callback-surface.md) - Accepted for the implemented connector OAuth surface; connector management is outside the active MVP.
- [`ADR-007 - Google OIDC Owner Identity Enrollment`](./ADR-007-google-oidc-owner-identity-enrollment.md) - Accepted; isolates Google-verified owner-subject enrollment from the Gmail/Drive connector OAuth lane.
- [`ADR-008 - Atlas Agent Visibility and Lifecycle Control Center`](./ADR-008-atlas-agent-visibility-control-center.md) - Accepted; establishes the active Atlas product boundary for externally operated agents.
- [`ADR-009 - Agent Enrollment, Authentication, and Telemetry Contract`](./ADR-009-agent-enrollment-and-telemetry-contract.md) - Accepted; establishes owner-created enrollment, per-agent credentials, push telemetry, and lifecycle trust controls.
