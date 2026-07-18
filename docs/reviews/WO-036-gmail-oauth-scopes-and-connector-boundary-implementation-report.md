# WO-036 Gmail OAuth, Scopes, and Connector Boundary Implementation Report

**Work Order:** [WO-036](../work-orders/036-gmail-oauth-scopes-and-connector-boundary.md)
**Status:** Completed - Merged
**Date:** 2026-07-18
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)
**Governing ADP:** [ADP-003](../implementation-plans/ADP-003-phase-6-gmail-agent-mvp-candidate.md)

## Summary

WO-036 adds the first Gmail/Drive connector boundary for Phase 6. The
implementation registers default Gmail and Google Drive connector descriptors,
enforces the accepted OAuth scopes, creates fake OAuth connection lifecycle
contracts, stores credential references without provider credential material,
exposes signed external-client connector APIs, supports connection health,
revocation, reconnect initiation, and provides operation allowlist checks for
later Gmail Work Orders.

No live Google credentials, live provider calls, personal mailbox access,
Gmail message reads, Drive file writes, drafting, sending, deleting, or
attachment saving were introduced.

## Scope Implemented

- Connector persistence tables:
  - `connector_types`
  - `connector_credential_references`
  - `connector_connections`
  - `connector_oauth_states`
- Default connector descriptors for:
  - Gmail with accepted scope `https://www.googleapis.com/auth/gmail.modify`
  - Google Drive with accepted scope `https://www.googleapis.com/auth/drive.file`
- Explicit rejection of `https://mail.google.com/`.
- OAuth start and callback contracts using fake provider behavior.
- Internal credential-reference records with no provider token value storage.
- Connector list/read, connection list/read, health, revoke, and reconnect API
  routes under `/api/v1`.
- External-client authorization allowlist for connector reads and lifecycle
  actions.
- Connector lifecycle and operation-authorization audit events.
- Focused connector tests covering exact scopes, broad-scope denial, fake OAuth
  callback, redaction, health, revoke, reconnect, and operation denial.

## Files Changed

- `apps/api/alembic/versions/0012_connector_oauth_boundary.py`
- `apps/api/src/atlas_api/api/connectors.py`
- `apps/api/src/atlas_api/core/authorization.py`
- `apps/api/src/atlas_api/core/observability.py`
- `apps/api/src/atlas_api/main.py`
- `apps/api/src/atlas_api/models/__init__.py`
- `apps/api/src/atlas_api/models/connector.py`
- `apps/api/src/atlas_api/services/connectors.py`
- `apps/api/tests/test_connectors.py`

## Validation Commands

Focused connector validation:

```text
cd apps/api
./.venv/bin/python -m pytest tests/test_connectors.py
```

Result:

```text
4 passed, 1 warning
```

Full backend validation:

```text
cd apps/api
./.venv/bin/python -m pytest
./.venv/bin/python -m ruff check .
./.venv/bin/python -m mypy src
```

Result:

```text
89 passed, 1 warning
All checks passed
Success: no issues found in 54 source files
```

Migration validation:

```text
cd apps/api
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas_wo036_migration.db ./.venv/bin/alembic upgrade head
ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas_wo036_migration.db ./.venv/bin/alembic current
```

Result:

```text
0012_connector_oauth (head)
```

Whitespace validation:

```text
git diff --check
```

Result:

```text
Passed
```

Scoped credential/material scan:

```text
rg -n "fake-provider-code|fake-health-code|access_token|refresh_token|oauth_token|https://mail.google.com/" apps/api/src apps/api/tests docs/work-orders/036-gmail-oauth-scopes-and-connector-boundary.md docs/reviews
```

Result:

```text
Matches are limited to negative test assertions, fake authorization-code test
fixtures that are not persisted or returned, the rejected broad-scope constant,
and governance documentation. No provider token value or live credential
material was introduced.
```

## Security and Privacy Evidence

- API responses omit connector credential-reference identifiers.
- OAuth callback does not persist or return authorization codes.
- Credential-reference records store only internal references, key version, and
  status metadata.
- Audit metadata is minimized through the shared sanitizer.
- The accepted Gmail scope is exactly `gmail.modify`.
- The accepted Drive scope is exactly `drive.file`.
- The broad `https://mail.google.com/` scope fails closed with
  `connector_scope_rejected`.
- Connection revocation marks both the connection and credential reference as
  revoked.
- Operation authorization fails closed when a connection is revoked or missing
  required scopes.

## Residual Risks and Deferred Scope

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Fake OAuth provider only | Expected | Controlled-account or live provider use remains WO-044 or separate maintainer authorization. |
| Credential encryption service is represented as reference-only metadata | Accepted for WO-036 | A later security/infrastructure Work Order must select real secret storage before live credentials. |
| Gmail message retrieval is absent | Expected | WO-037 owns eligibility, retrieval, and classification. |
| Drive file writes are absent | Expected | WO-039 owns approved attachment saving. |
| Dashboard surfaces remain contract-compatible only | Expected | WO-043 or a dashboard productization Work Order owns UI integration. |

## Completion State

WO-036 is implemented with local validation complete and is ready for governed
pull-request review. It does not complete the ADP-003 merge gate until PR review
and required CI pass.

## Pull Request and Merge

- Pull request: [#54 - Accept Phase 6 plan and implement Gmail connector boundary](https://github.com/vasudevap/agent-control-center/pull/54)
- Final CI result: Passed
- Merge commit: `2d553cfbd19cf02c2cf7d798b1673fea840ba12e`
- Merge date: `2026-07-18T18:50:56Z`

WO-036 is complete and merged. WO-037 may begin under ADP-003.
