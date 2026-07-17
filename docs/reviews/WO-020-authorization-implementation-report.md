# WO-020 Authorization Implementation Report

**Work Order:** [WO-020 Authorization and External-Client Identity Boundary](../work-orders/020-authorization-and-external-client-identity-boundary.md)
**Implementation Branch:** `codex/wo-020-authorization-identity`
**Implementation Status:** Complete - Merged
**Report Date:** 2026-07-17

## Summary

WO-020 introduces the first explicit authorization boundary and replaces the
temporary shared header secret with replay-resistant external-client request
authentication.

- Authorization is typed by actor kind, actor identifier, channel, resource,
  action, and optional risk/environment context. It denies by default.
- The only initial allow rule is the explicitly scoped external-client
  authentication probe. Human and service actors are not silently converted
  into external clients.
- External requests now use HMAC-SHA256 over method, canonical path/query,
  timestamp, nonce, and SHA-256 body digest. Signature comparison is constant
  time and accepts lowercase hexadecimal signatures only.
- Current and next environment-owned key identifiers support bounded rotation;
  unknown keys fail closed. No verification keys are stored in PostgreSQL.
- Accepted nonces are persisted with a client/key scoped unique constraint,
  expire after ten minutes, and prevent replay. A request fails closed if its
  persistent nonce store is unavailable.
- Authentication and authorization outcomes create metadata-only audit events
  with correlation IDs; signatures and secret values are never recorded.

## Scope Preserved

The implementation does not introduce multi-client tenancy, RBAC, OAuth,
business permissions, rate limiting, live credentials, provider provisioning,
or frontend work.

## Validation

- Backend pytest: 27 passed.
- Ruff and mypy passed.
- `git diff --check` passed.
- PostgreSQL 18 Alembic validation, frontend regression checks, secret scan,
  and required CI passed before merge.

## Next Work Order

After this branch is merged, proceed to WO-021 to establish the versioned API
envelope, pagination, validation, idempotency, and error contract.
