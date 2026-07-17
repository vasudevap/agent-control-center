# Decisions

Accepted architecture and design decisions outrank working guidance and recommendations.

- Approved design decision records live under `docs/design/decisions/`.
- `atlas-design-decision-log.md` is the migrated index from the former Claude implementation workspace.

The migrated index is preserved for provenance and does not create new architecture decisions.

## Architecture Decisions

- [`ADR-001 - Frontend Component Testing`](./ADR-001-frontend-component-testing.md) - Accepted; selects the development-time component-testing baseline required to resolve the Work Order 006 frontend testing gap.
- [`ADR-002 - Human Approvals Decision Integrity`](./ADR-002-human-approvals-decision-integrity.md) - Accepted; separates exact human authorization from execution and preserves explicit indeterminate outcomes.
- [`ADR-003 - Governed External Approval Decision Channel`](./ADR-003-governed-external-approval-decision-channel.md) - Accepted; extends the approval trust boundary to an authenticated external control plane acting for one human reviewer.
- [`ADR-004 - Governed External Product Client Contract`](./ADR-004-governed-external-product-client-contract.md) - Accepted; establishes the authenticated API and webhooks as the governed contract for one external product client, including non-approval manual-handling notification for policy-suppressed messages.
- [`ADR-005 - Draft-Support Knowledge and Ask-Instead-of-Guess`](./ADR-005-draft-support-knowledge-and-ask-instead-of-guess.md) - Accepted; extends the generic external product client contract with governed draft-support facts, facts-used evidence, non-authorizing questions and answers, and Gmail agent asking and learning behavior.
