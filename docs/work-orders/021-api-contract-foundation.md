# Work Order 021: API Contract Foundation

**Status:** Accepted - Implementation Authorized
**Work Order ID:** WO-021
**Type:** Backend API foundation
**Implementation Authorization:** Granted
**Accepted:** 2026-07-17
**Accepted By:** Repository Maintainer
**Governing Plan:** [Phase 3 Platform Foundation Master Plan](../implementation-plans/phase-3-platform-foundation-master-plan.md)
**Architecture Authority:** [Phase 3 Target Architecture](../implementation-plans/phase-3-platform-foundation-target-architecture.md), [Security Architecture](../architecture/07-security-architecture.md)
**Prerequisite:** [WO-020](./020-authorization-and-external-client-identity-boundary.md)

## 1. Purpose

Standardize the versioned HTTP contract before broad operational endpoints are
implemented.

## 2. Decisions Fixed Before Implementation

| Concern | Decision |
| --- | --- |
| Versioning | Operational routes remain under `/api/v1`; unversioned liveness/readiness remain infrastructure endpoints. |
| Success shape | Operational success responses use `{ "data": ..., "meta": ... }`; `meta` carries correlation/pagination details only when applicable. |
| Error shape | Preserve `{ "error": { "code", "message", "correlation_id", "details"? } }`; details are typed, optional, and non-secret. |
| Pagination | Opaque cursor; default `limit=50`, maximum `100`; no page-number or raw database-key contract. |
| Filtering/sorting | Explicit allowlists per resource; unknown fields reject rather than being ignored. |
| Idempotency | `Idempotency-Key` is 16–128 visible ASCII characters; validation and request-fingerprint interface only. Persistence is added by a work order implementing a state-changing endpoint. |
| Rate-limit contract | Standard `429` error plus `Retry-After`; enforcement infrastructure is deferred. |
| Time/IDs | UTC RFC 3339 timestamps and opaque string identifiers. |
| OpenAPI | Stable tags, schemas, security declarations, examples, and explicit deprecated markers. |

## 3. Approved Scope if Accepted

- Shared response/error/pagination/filter/idempotency schemas and helpers.
- Contract-safe validation limits for query/body/header inputs.
- OpenAPI grouping and contract tests for existing health, probe, and
  fail-closed placeholder routes.
- Consistent correlation ID propagation and no production stack traces.
- README and API convention documentation suitable for later work-order agents.

## 4. Explicitly Out of Scope

Business CRUD, authentication/authorization redesign, idempotency record tables,
rate-limit enforcement, CORS/deployment changes, generated SDKs, GraphQL,
frontend integration, or Phase 5 knowledge behavior are excluded.

## 5. Verification and Completion

Require schema/contract/OpenAPI tests, all repository validation, secret scan,
CI, implementation report, and governed merge. Snapshot tests must verify
semantics without making harmless OpenAPI ordering brittle.

## 6. Stop-and-Ask Triggers

Stop before breaking an accepted external contract, adding a new protocol or
code generator, introducing business endpoints, or persisting idempotency data.

## 7. Review Notes

Accepted as part of the consolidated Phase 3 planning package. Implement only
after WO-020 has merged.
