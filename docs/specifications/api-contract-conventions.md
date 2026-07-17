# Atlas API Contract Conventions

**Status:** Implemented for platform foundation routes
**Authority:** [WO-021 API Contract Foundation](../work-orders/021-api-contract-foundation.md)
**Last Updated:** 2026-07-17

## Scope

These conventions apply to operational HTTP routes under `/api/v1`. Unversioned
`/health/live` and `/health/ready` are infrastructure endpoints and retain
their minimal infrastructure response shapes.

## Success Responses

Operational success responses use a stable envelope:

```json
{
  "data": {},
  "meta": {
    "correlation_id": "opaque-correlation-id"
  }
}
```

`data` contains resource data only. `meta` is optional and contains only
correlation, pagination, or other contract metadata; it does not contain
secrets, credentials, or authorization decisions.

## Error Responses

Errors use this shape:

```json
{
  "error": {
    "code": "stable_machine_code",
    "message": "Safe user-facing summary.",
    "correlation_id": "opaque-correlation-id",
    "details": {}
  }
}
```

`details` is optional, typed, and non-secret. Validation errors report safe
field locations and codes, never rejected values or stack traces. Rate-limit
responses use HTTP `429` and a `Retry-After` header; enforcement is deferred.

## Query and Request Conventions

- Pagination uses an opaque cursor; clients must not depend on its encoding.
- `limit` defaults to `50` and may not exceed `100`.
- Each resource must declare an explicit filtering/sorting allowlist. Unknown
  fields fail with a contract error and are never ignored.
- State-changing routes must validate `Idempotency-Key` as 16–128 visible ASCII
  characters and derive a method/path/body request fingerprint before any
  persistence work. WO-021 introduces no idempotency storage.
- Times are UTC RFC 3339 values and IDs are opaque strings.

## Documentation and Compatibility

OpenAPI groups routes by stable tags and documents the external HMAC security
boundary. New endpoints must be versioned, use these envelopes, add contract
tests, and avoid changing an accepted contract without a new approved decision
and migration plan.
