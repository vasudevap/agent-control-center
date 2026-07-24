# WO-066 Owner Enrollment and Agent Credentials Implementation Report

**Work Order:** [WO-066](../work-orders/066-owner-enrollment-and-agent-credentials.md)
**Status:** Completed - Local Validation Passed
**Implemented:** 2026-07-24
**Commit:** This commit

## Summary

WO-066 implements owner-authenticated agent enrollment and one-time credential
issuance on the active dashboard API surface.

The implementation:

- adds agent credential pepper settings and production-like readiness checks;
- generates `atl_agent_<credential_lookup_id>.<secret>` credentials using
  CSPRNG output;
- stores only HMAC-SHA256 verifiers, lookup ids, key ids, fixed telemetry
  scope, and lifecycle timestamps;
- returns plaintext credentials only in the enrollment response;
- adds owner-session, CSRF, idempotency-key, authorization, and audit coverage
  for enrollment and metadata update;
- scopes active dashboard agent list/read/update behavior to the signed-in
  owner;
- preserves the dormant external-client descriptor route rather than replacing
  it in this Work Order.

## Route-Base Alignment

WO-066 adds backend behavior only. It preserves the route-base adoption from
WO-064:

- `/` remains the public landing page;
- `/control-center` remains the canonical authenticated dashboard root;
- active dashboard APIs are consumed by `/control-center` surfaces in later
  frontend Work Orders.

## Scope Alignment

In scope:

- owner create/list/read/update foundation for active agents through the
  dashboard API;
- one-time credential issuance and verifier persistence;
- production-like readiness fail-closed behavior for missing credential pepper
  settings;
- tests proving owner-only access and no plaintext persistence.

Out of scope and not implemented:

- heartbeat ingestion;
- execution ingestion;
- credential rotation;
- disconnect, reconnect, and archive;
- frontend enrollment UI;
- hosted provider secret entry.

## Validation

Local validation:

```text
/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m mypy apps/api/src
Success: no issues found in 67 source files

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m ruff check apps/api
All checks passed!

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m pytest apps/api/tests/test_agent_enrollment_credentials.py apps/api/tests/test_dashboard_facade.py apps/api/tests/test_config.py
29 passed, 1 existing Starlette/httpx deprecation warning

/Users/pv/bootcamp/projects/agent-control-center/apps/api/.venv/bin/python -m pytest apps/api
182 passed, 1 existing Starlette/httpx deprecation warning

git diff --check
pass
```

## Security Notes

- The existing external-client HMAC secret is not used for agent credentials.
- Plaintext agent tokens are not stored in `agent_credentials`, audit metadata,
  or read/update responses.
- Enrollment idempotency fails closed on replay because plaintext credentials
  cannot be safely replayed after issuance.
- Credential settings are redacted in configuration output.

## Rollback

Source rollback disables the new enrollment and metadata update routes.
Rollback cannot recover already-issued plaintext credentials; credential rows
must be retained for audit and investigation.

## Residual Risks

- The active frontend enrollment UI is deferred to WO-069.
- Credential rotation, disconnect, reconnect, archive, and telemetry rejection
  behavior remain deferred to later Work Orders.
