# Work Order 009: Design Direction Reconciliation

**Status:** Reconciliation Review In Progress
**Work Order:** [WO-009 Human Approvals Frontend Experience](../work-orders/009-human-approvals-frontend-experience.md)
**Selected design pull request:** [#9 Adopt Atlas frontend design direction](https://github.com/vasudevap/agent-control-center/pull/9)
**Superseded implementation pull request:** [#8 Implement Human Approvals frontend prototype](https://github.com/vasudevap/agent-control-center/pull/8)
**Date:** 2026-07-15

---

## 1. Decision

The repository owner selected the alternate Atlas frontend as the product's
design direction. Pull request #9 integrated that direction selectively and
was merged to `main` at merge commit `76f362f`. The archived design history is
preserved by the `archive/gui-alternate-design` tag.

Pull request #8 contains an earlier Human Approvals interface and must not be
merged wholesale. Doing so would reintroduce a superseded presentation and
overwrite portions of the selected component vocabulary. Its approved product,
architecture, decision, engineering, Work Order, and readiness-review records
are preserved in the canonical repository by this reconciliation change.

## 2. Preserved authority

The following records remain authoritative for Human Approvals behavior and
future operational implementation:

- Human Approvals Functional Specification, version 1.1.
- Human Approvals Architecture, version 1.0.
- ADR-002 Human Approvals Decision Integrity.
- ES-003 Human Approvals Frontend Experience.
- WO-009 Human Approvals Frontend Experience and its approval review.

The archived alternate design history remains authoritative for the selected
visual and interaction decisions. `docs/design-principles.md` is the binding
implementation guide for that direction.

## 3. Deliberately not preserved

- The superseded application code from pull request #8.
- Screenshots that document the superseded interface.
- The proposed WO-010 GUI correction document, which was never approved and
  targeted the replaced interface.
- The obsolete `alternate examples/` directory.

This is a selective documentation reconciliation, not a merge of pull request
#8.

## 4. Candidate implementation evidence

The selected implementation on `main` appears to provide the following
candidate evidence. Nothing in this list is a completion decision:

- Queue and History views at `/approvals`.
- Canonical approval detail routes.
- Typed, fictional local fixtures.
- Local-only simulated decision controls.
- Persistent prototype disclosure in the collection header and decision
  context.
- Risk, state, review, expiry, and execution-outcome presentation that does
  not depend on color alone.
- Responsive desktop tables and mobile cards.

The Phase 1 integration passed install, typecheck, lint, component tests,
production build, responsive browser review, light-theme review, and dark-theme
review before merge. Required CI passed on pull request #9 and the same checks
passed again from merged `main`.

## 5. Confirmation boundary

WO-009 is not closed by the design integration alone. The repository owner and
implementer will compare the implementation now on `main` with every
applicable WO-009 and ES-003 acceptance criterion using the
[WO-009 Alternate Design Mapping](./WO-009-alternate-design-mapping.md). Items
remain pending until they are reviewed individually.

Any gap found in that review is future frontend work under an approved Work
Order amendment or follow-up Work Order. Real services, persistence,
authentication, policy evaluation, audit writing, runtime continuation, and
external execution remain explicitly out of scope.

## 6. Pull-request disposition

Pull request #8 is obsolete and must not be merged. The authoritative records
and useful implementation details have been reconciled into the selected
design through the mapping review and follow-up pull request #10. Closing PR #8
does not discard its Git history; it only prevents the superseded interface
from being mistaken for the current implementation direction.
