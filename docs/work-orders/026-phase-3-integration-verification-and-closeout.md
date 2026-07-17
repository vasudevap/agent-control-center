# Work Order 026: Phase 3 Integration Verification and Closeout

**Status:** Proposed - Review Required
**Work Order ID:** WO-026
**Type:** Integration verification and governance closeout
**Implementation Authorization:** Not Granted
**Accepted:** Not Accepted
**Accepted By:** Not Accepted
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Prerequisites:** WO-016 through WO-025 completed and merged

## 1. Purpose

Verify Phase 3 as one coherent backend foundation, resolve only closeout defects,
and produce the governed Phase 5 handoff without implementing Phase 5 behavior.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Environment | GitHub Actions PostgreSQL 18 is the authoritative automated integration environment; local PostgreSQL evidence is optional compensating evidence. |
| Smoke path | Migrate database; verify health/readiness; exercise owner session boundary with fake verifier; authenticate/authorize signed external request; enqueue/claim/complete a job; trigger one interval schedule; generate signed fake webhook; persist audit and inspect redacted correlated logs. |
| External effects | None: fake verifier, fake webhook transport, synthetic data, no providers, no live agent execution. |
| Defect policy | Fix only defects required for accepted WO-016–WO-025 conformance; new capability becomes a new work order. |
| Gate | Any authentication bypass, authorization allow-by-default, migration failure, duplicate job/schedule trigger, unsigned webhook, audit loss, or secret leak blocks closeout. |
| Handoff | Closeout report, residual-risk register, architecture/backlog/status alignment, and explicit Phase 5 entry criteria. |

## 3. Approved Scope if Accepted

- A deterministic integration test/harness using existing public service
  boundaries and PostgreSQL 18.
- Cross-component correlation and audit evidence assertions.
- Security/privacy negative-path verification and strict secret scan.
- Documentation/status/index corrections and narrow defect fixes discovered by
  the integration test.
- Phase 3 closeout report listing delivered capabilities, deferred limitations,
  known warnings, and recommended Phase 5 work-order sequence.

## 4. Explicitly Out of Scope

New product capability, live infrastructure/provider calls, frontend-backend
integration, real OAuth, production readiness certification, load/chaos testing,
Phase 5 knowledge CRUD, approval workflow implementation, or Gmail behavior are
excluded.

## 5. Verification and Completion

All WO-016–WO-025 PRs must be merged first. The complete local/CI suite,
PostgreSQL migration round trip, integration smoke path, security negative
tests, secret scan, documentation link/status scan, and GitHub CI must pass.
Phase 3 closes only after the final report and PR merge.

## 6. Stop-and-Ask Triggers

Stop if closeout requires architecture change, live credentials/resources,
business behavior, provider integration, data migration, or more than a narrow
defect correction. Record the finding and propose a follow-up work order.

## 7. Review Notes

Planning only; implementation remains unauthorized until accepted.
