# WO-070 Disconnect, Reconnect, Archive, and Credential Closeout Implementation Report

**Work Order:** [WO-070](../work-orders/070-disconnect-reconnect-archive-and-credential-closeout.md)
**Status:** Completed - Local Validation Passed
**Implemented:** 2026-07-24
**Commit:** This commit

## Summary

WO-070 completes the owner-controlled agent trust lifecycle for the Agent
Visibility MVP.

The implementation:

- adds owner-authenticated dashboard mutation routes for credential rotation,
  disconnect, reconnect, and archive;
- rotates telemetry credentials with an exactly 24-hour overlap window for the
  previously active credential;
- immediately revokes active and overlap credentials on disconnect and archive;
- returns a new one-time plaintext credential only from rotate and reconnect
  mutation responses;
- moves disconnected agents back to pending on reconnect until a new heartbeat
  is accepted;
- hides archived agents from default active owner views while preserving agent,
  heartbeat, execution, alert, activity, and audit history;
- records lifecycle activity and audit evidence without plaintext credential
  material;
- adds live-only lifecycle controls to the Agent Detail surface under
  `/control-center/agents/...`.

## Route-Base Alignment

WO-070 adopts the ADP-006 route-base correction as current authority:

- `/` remains the public Atlas landing page;
- `/control-center` remains the canonical authenticated active product shell;
- lifecycle controls are available only on the live Agent Detail surface under
  `/control-center/agents/[agentId]`;
- no lifecycle control, credential display, or authenticated dashboard behavior
  is added to the public landing page.

## API Behavior

New owner dashboard mutation routes:

- `POST /api/v1/dashboard/agents/{agent_id}/credentials/rotate`
- `POST /api/v1/dashboard/agents/{agent_id}/disconnect`
- `POST /api/v1/dashboard/agents/{agent_id}/reconnect`
- `POST /api/v1/dashboard/agents/{agent_id}/archive`

All routes require an owner session, CSRF validation, and an idempotency key.
The routes are authorized through the dashboard owner authorization boundary
and write audit records for successful lifecycle mutations.

Credential verification now accepts credentials in active status and accepts
overlap credentials only until their overlap expiry. Expired overlap
credentials are rejected. Disconnected and archived agents reject telemetry
because all active and overlap credentials are revoked before the state change
is committed.

## Frontend Behavior

The live Agent Detail page adds a Lifecycle Controls card that:

- explains that Atlas controls the enrolled identity and telemetry credential,
  not the external runtime process;
- asks for owner confirmation before rotate, disconnect, reconnect, or archive;
- disables invalid lifecycle transitions in the current state;
- shows one-time credentials only when returned by rotate or reconnect;
- updates the displayed lifecycle state after each successful mutation.

## Validation

Local validation:

```text
.venv/bin/python -m ruff check apps/api
All checks passed!

.venv/bin/python -m mypy apps/api/src
Success: no issues found in 72 source files

.venv/bin/python -m pytest apps/api
208 passed, 1 existing Starlette/httpx deprecation warning

npm run lint --workspace apps/web
pass

npm run typecheck --workspace apps/web
pass

npm test --workspace apps/web
110 passed across 26 web test files

npm run build --workspace apps/web
pass

git diff --check
pass

Secret-pattern scan
pass after reviewing matches as pre-existing redaction tests, Gmail connector
variable names, CSS risk-token class names, and existing documentation text;
no WO-070 plaintext credential or runtime secret was added.
```

Focused lifecycle coverage:

- credential rotation accepts old and new tokens during the 24-hour overlap and
  rejects the old token after overlap expiry;
- disconnect rejects subsequent telemetry for the prior credential;
- reconnect issues a replacement one-time credential and requires heartbeat to
  become connected;
- archive revokes credentials, hides the agent from default active owner views,
  preserves records, and rejects subsequent telemetry;
- frontend lifecycle client calls use the expected `/api/v1/dashboard/agents`
  mutation paths with CSRF and idempotency headers;
- live Agent Detail rotation displays the one-time token returned by the
  mutation response.

## Security Notes

- Plaintext credentials are generated only for one-time mutation responses and
  are not exposed through read paths, audit records, or activity records.
- Stored verifiers remain HMAC values using the configured credential pepper.
- Disconnect and archive revoke Atlas telemetry credentials only; Atlas does
  not claim to stop, pause, delete, deploy, schedule, or otherwise control the
  external agent runtime.
- Archived agents are hidden from default active owner views without deleting
  historical evidence.

## Rollback

If lifecycle behavior is unsafe, disable the affected dashboard mutation route
while preserving all agent, credential, telemetry, alert, activity, and audit
records. Credential plaintext cannot be recovered by rollback.

## Residual Risks

- Hosted reference-agent verification and final ADP closeout remain WO-071
  scope.
- Production hosted verification was intentionally not performed in WO-070;
  WO-071 owns hosted curl, Python, and TypeScript client evidence.
