# Definition of Done

Work is done only when the following items are satisfied as applicable:

- Approved scope is implemented and exclusions remain untouched.
- Acceptance criteria are satisfied with reviewable evidence.
- `npm ci`, `npm run typecheck`, `npm run lint`, and `npm run build` pass for the current web baseline.
- Existing automated tests pass where a real test suite exists; new behavior has appropriate tests once test infrastructure is approved.
- UI work completes responsive, theme, keyboard, accessibility, and design review.
- Architecture and design compliance are explicitly reviewed.
- Security, privacy, data, and integration impacts are addressed.
- Canonical documentation and decision records are updated.
- An implementation, handoff, or review report is complete for significant work.
- Required CI passes and the branch is merged through the approved pull-request and merge process.
- Release notes and version updates are complete when the change is included in a release.
- No secrets, environment files, dependency directories, build output, caches, or accidental generated artifacts are committed.
- The merged baseline is validated when required, and remaining limitations have owners or tracked issues.
