# Work Order 071: Hosted Reference-Agent Verification and ADP Closeout

**Status:** Accepted - Authorized, blocked on WO-070 completion
**Work Order ID:** WO-071
**Type:** Hosted MVP verification and program closeout
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-24
**Engineering Specification:** [ES-009](../engineering-specifications/ES-009-agent-visibility-and-lifecycle-mvp.md)
**Governing ADP:** [ADP-006](../implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md)
**Prerequisites:** WO-070 accepted and complete
**Review Record:** To be created during implementation

## 1. Purpose

Validate the completed Agent Visibility MVP through hosted deployment,
migration evidence, independent reference clients, and ADP closeout.

## 2. Approved Scope if Accepted

- Run hosted migration verification for the ES-009 schema.
- Provide three independent clients: curl, plain Python, and TypeScript.
- Verify enrollment, first heartbeat, health loss, recovery, failed check,
  successful execution, failed execution, repeated-failure alert, rotation,
  overlap expiry, disconnect rejection, reconnect, and archive.
- Capture hosted frontend and API evidence without exposing secrets.
- Run the complete ES-009 local validation command set before first push.
- Record review/closeout evidence under `docs/reviews/`.
- Update ADP-006, Work Order, README, ROADMAP, and handoff status records.

## 3. Expected File Scope

- reference client examples under an accepted existing docs or test location
- `docs/reviews/**`
- `docs/implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md`
- `docs/work-orders/071-hosted-reference-agent-verification-and-adp-closeout.md`
- `README.md`
- `ROADMAP.md`
- `docs/handoff.md`
- related tests or smoke scripts if introduced by accepted scope

## 4. Explicitly Out of Scope

Public launch, release tagging, new provider resources, production business
data use, published SDK packages, runtime control, external scheduling, and
deferred connector/Gmail/Drive/approval/policy/knowledge features are out of
scope unless separately accepted.

## 5. Acceptance Criteria

- Three independent clients integrate without importing Atlas server packages.
- Hosted evidence proves live frontend and API behavior for the ES-009
  success criteria.
- No secret values, owner subject values, provider credentials, or bearer
  tokens are recorded in documentation, logs, screenshots, or PR text.
- ADP-006 and Work Order statuses accurately reflect completion or any
  residual risks.
- Required local validation and CI evidence are recorded.

## 6. Verification

Run the full ES-009 command set:

```bash
npm ci
npm run typecheck
npm run lint
npm test
npm run build
python -m pip install -c apps/api/constraints.txt -e "apps/api[dev]"
python -m mypy apps/api/src
python -m ruff check apps/api
python -m pytest apps/api
cd apps/api
ATLAS_API_DATABASE_URL="$ATLAS_API_DATABASE_URL" python -m alembic upgrade head
ATLAS_API_DATABASE_URL="$ATLAS_API_DATABASE_URL" python -m alembic downgrade base
```

## 7. Rollback Expectations

Closeout must document source rollback, deployment rollback, migration forward
repair posture, and any residual risks. Hosted rollback or public release
actions require separate explicit authorization if they go beyond accepted Work
Order scope.

## 8. Stop-and-Ask Triggers

Stop before public launch, release tagging, provider writes not already
authorized, production business data use, exposing secrets, changing hosting
topology, or weakening CI/rollback requirements.
