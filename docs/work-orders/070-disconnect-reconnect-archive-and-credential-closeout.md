# Work Order 070: Disconnect, Reconnect, Archive, and Credential Closeout

**Status:** Completed - Local Validation Passed
**Work Order ID:** WO-070
**Type:** Agent trust lifecycle closeout
**Implementation Authorization:** Granted by Repository Maintainer on 2026-07-24
**Engineering Specification:** [ES-009](../engineering-specifications/ES-009-agent-visibility-and-lifecycle-mvp.md)
**Governing ADP:** [ADP-006](../implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md)
**Prerequisites:** WO-069 completed and merged
**Review Record:** [WO-070 Implementation Report](../reviews/WO-070-disconnect-reconnect-archive-and-credential-closeout-implementation-report.md)

## 1. Purpose

Complete the owner-controlled trust lifecycle: rotation, disconnect, reconnect,
archive, immediate credential rejection, retained history, and UI
confirmation states.

## 2. Approved Scope if Accepted

- Implement credential rotation with exactly 24 hours of overlap.
- Implement disconnect with immediate revocation of all credentials.
- Implement reconnect from disconnected to pending with one-time credential
  issuance.
- Implement archive with credential revocation and default active-view hiding.
- Add owner-confirmation UI for rotation, disconnect, reconnect, and archive.
- Preserve heartbeats, executions, alerts, activity, and audit history.
- Add tests for old/new credential acceptance during overlap and rejection
  after expiry, disconnect, archive, and token/path mismatch.
- Keep all active lifecycle UI under `/control-center/agents/...`; root `/`
  remains the public Atlas landing page.

## 3. Expected File Scope

- ES-009 lifecycle API routers and services
- ES-009 credential service modules
- `apps/api/tests/**`
- `apps/web/src/app/(shell)/agents/**`
- `apps/web/src/lib/dashboard-runtime.ts`
- related frontend tests

## 4. Explicitly Out of Scope

External runtime shutdown, process termination, provider credential revocation,
agent deployment/schedule management, deletion of history, and production
secret entry are out of scope.

## 5. Acceptance Criteria

- Rotate returns a replacement plaintext credential once and sets old
  credential overlap expiry.
- Disconnect immediately rejects subsequent telemetry and states that the
  external runtime may still be running.
- Reconnect issues a new one-time credential and requires a new heartbeat to
  become connected.
- Archive hides the agent from default active views without deleting history.
- Activity and audit evidence are created without plaintext secrets.
- Active frontend controls remain rooted under `/control-center`; no lifecycle
  controls are introduced on the public landing page.

## 6. Verification

```bash
npm run typecheck
npm run lint
npm test
python -m mypy apps/api/src
python -m ruff check apps/api
python -m pytest apps/api
git diff --check
```

## 7. Rollback Expectations

Credential plaintext cannot be recovered by rollback. If lifecycle behavior is
unsafe, disable the affected mutation route and preserve all credential,
telemetry, alert, activity, and audit records.

## 8. Stop-and-Ask Triggers

Stop before attempting to stop an external runtime, exposing stored
credentials, deleting historical evidence, changing identity-provider
behavior, or revoking third-party provider credentials.
