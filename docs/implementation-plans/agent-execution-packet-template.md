# Agent Execution Packet Template

Use this template when assigning a future implementation agent to a single
accepted Work Order.

Do not use this packet to bypass repository governance. The accepted Work Order
is the implementation authority.

---

## Packet Header

**Task Name:** `<short task name>`
**Recommended Codex Setting:** `<Model> · <Effort> · <Speed>`
**Branch:** `codex/<work-order-slug>`
**Base Branch:** `main`
**Pull Request Mode:** Draft until local validation and self-review complete

## Objective

Implement `<Work Order ID and title>` exactly as accepted.

## Governing Documents

- `AGENTS.md`
- `<accepted Engineering Specification>`
- `<accepted Work Order>`
- `<related architecture documents>`
- `<related ADRs>`
- `docs/governance/definition-of-ready.md`
- `docs/governance/definition-of-done.md`
- `docs/governance/pull-request-and-review-process.md`

## Allowed File Scope

The agent may create or modify:

- `<explicit paths>`

The agent must not modify:

- `<explicit exclusions>`

## Explicit Exclusions

The agent must not implement:

- `<out-of-scope behavior>`

## Required Implementation Notes

- Preserve deny-by-default behavior.
- Preserve existing public contracts unless the Work Order explicitly changes
  them.
- Keep secrets out of source, logs, tests, docs, and fixtures.
- Use existing backend patterns before adding abstractions.
- Add tests proportional to risk.
- Record any implementation limitation in the review report.

## Required Checks

Run and record:

- `git diff --check`
- strict secret-pattern scan over changed files
- backend tests relevant to the change
- backend lint/typecheck when backend files change
- migration upgrade/downgrade when migrations change
- `npm run typecheck`
- `npm run lint`
- `npm test`
- `npm run build`

If a check cannot run, record:

- exact command;
- failure reason;
- compensating evidence;
- whether the blocker must stop the PR.

## Required Evidence

The PR must include:

- scope summary;
- exclusions preserved;
- validation evidence;
- migration evidence when applicable;
- security/privacy considerations;
- residual risks;
- next recommended Work Order.

## Stop-and-Ask Triggers

Stop and ask before proceeding if:

- the Work Order scope conflicts with accepted architecture;
- implementation requires a new framework, deployment service, or persistent
  external dependency;
- the agent needs to store or handle real secrets;
- the task requires production deployment;
- tests reveal behavior that would expand into Phase 5 or Phase 6;
- unrelated user changes overlap with required files;
- a destructive action is needed.

## PR Title

`<imperative title>`

## PR Body Skeleton

```markdown
## Summary

- ...

## Governing Work Order

- ...

## Scope

- ...

## Exclusions Preserved

- ...

## Validation

- ...

## Risks and Follow-Up

- ...
```
