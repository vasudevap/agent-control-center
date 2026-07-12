# Branching Strategy

## Model

Atlas uses lightweight trunk-based development. `main` is always releasable and is the only permanent development branch.

Use one short-lived branch per approved Work Order, Engineering Specification, defect, documentation change, or maintenance task:

- `feat/` — approved product capability
- `fix/` — defect correction
- `chore/` — maintenance, tooling, or governance
- `docs/` — documentation-only work
- `hotfix/` — urgent correction to a releasable baseline

Names should be concise and traceable, for example `chore/es-001-engineering-governance-ci`.

## Rules

- Branch from synchronized `main` and keep the branch narrowly scoped.
- Merge through a pull request after required CI and review evidence pass.
- Do not make routine direct implementation commits to `main` after protection is established.
- Do not force-push or delete `main`.
- Delete merged branches where practical.
- Do not create a GitFlow `develop` branch.
- Do not create a long-lived release branch unless a later approved requirement and ADR justify it.
- Resolve drift by incorporating current `main` without rewriting shared history.

## Emergency work

Urgent work uses a short-lived `hotfix/` branch, the same required CI, and the normal pull-request path. If an external incident makes a standard step impossible, record the exception and compensating review, then complete a retrospective and corrective release record.
