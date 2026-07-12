# Pull-Request and Review Process

## Required description

Every pull request uses the repository template and includes a summary, linked governing artifact, in-scope and out-of-scope boundaries, architecture/product/UX/security/privacy/data/integration impacts, validation evidence, documentation updates, visual evidence where relevant, risks, limitations, and rollback considerations.

## Scope and evidence

Unrelated refactors and dependency upgrades do not ride with feature work. Authors provide reproducible command results and explain any not-applicable check. UI changes include screenshots or equivalent visual evidence plus responsive and accessibility review. Decisions and canonical documentation change in the same pull request when required.

## Review expectations

Review verifies the approved objective and acceptance criteria, architecture and design compliance, security and privacy implications, data and integration boundaries, test/validation sufficiency, documentation, secret/generated-file hygiene, and release impact. Required CI must pass; failed or pending required CI prohibits merge.

The project currently has one maintainer, so governance does not require an approving-review count that the maintainer cannot satisfy. Self-review is still explicit and evidence-based.

## Merge methods

- Use a normal merge commit for milestones, Work Orders, Engineering Specifications, and meaningful multi-commit branches.
- Squash merging is acceptable for a small atomic maintenance or documentation change when intermediate commits have no durable value.
- Do not rebase shared branches or force-push `main`.

## Exceptions and emergency fixes

Use `hotfix/` for urgent fixes. Preserve CI and a pull request whenever GitHub is available. Any deviation records the cause, risk, compensating checks, approver, and follow-up. Never use an emergency to conceal scope, bypass a security control, or merge known failing CI.
