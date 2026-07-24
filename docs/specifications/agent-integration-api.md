# Atlas Agent Integration API

**Status:** Accepted Product Contract
**Version:** 1.0
**Date:** 2026-07-23
**Governing Decisions:** `ADR-008` and `ADR-009`
**Implementation Status:** Not implemented

## 1. Purpose

This specification defines the minimum REST contract used by externally
operated agents to report health and executions to Atlas.

It is implementation authority only when cited by an accepted Engineering
Specification and Work Order.

## 2. Base contract

- Production base URL: `https://api.atlas.grafley.com`
- API prefix: `/api/v1`
- Media type: `application/json`
- Timestamps: RFC 3339 UTC
- Character encoding: UTF-8
- Success and error envelopes follow `api-contract-conventions.md`.
- Every response includes `X-Correlation-Id`.
- Clients may supply `X-Correlation-Id`; Atlas validates or replaces it.

## 3. Authentication

Agent write requests use:

```http
Authorization: Bearer <agent-credential>
```

The credential is bound to one agent. Atlas returns:

- `401` for missing, malformed, unknown, expired, or revoked credentials;
- `403` when a valid credential is not authorized for the requested agent or
  operation;
- `409` when lifecycle or idempotency state conflicts;
- `422` for schema-valid JSON with invalid field values;
- `429` when an ingestion limit is exceeded.

Authentication failures must not reveal whether another agent exists.

## 4. Owner lifecycle API

Owner endpoints use the existing owner session, CSRF, authorization, and
same-origin controls.

### 4.1 Create enrollment

```http
POST /api/v1/agents
```

Request:

```json
{
  "slug": "invoice-monitor",
  "display_name": "Invoice Monitor",
  "description": "Checks incoming invoices for processing failures.",
  "environment": "production",
  "monitoring_mode": "heartbeat",
  "heartbeat_interval_seconds": 60,
  "tags": ["finance", "operations"],
  "repository_url": "https://github.com/example/invoice-monitor",
  "deployment_url": "https://example-host.invalid/services/invoice-monitor",
  "expected_version": "1.0.0"
}
```

Response data:

```json
{
  "agent_id": "agt_01J...",
  "lifecycle_status": "pending",
  "atlas_api_url": "https://api.atlas.grafley.com",
  "contract_version": "1.0",
  "credential": "atl_agent_...",
  "credential_expires_at": null,
  "heartbeat_interval_seconds": 60
}
```

`credential` is returned once and is never available through a read endpoint.

### 4.2 List and read

```text
GET /api/v1/agents
GET /api/v1/agents/{agent_id}
```

List supports cursor pagination and filters for lifecycle, observed health,
reported health, environment, tag, alert state, and free-text search.

### 4.3 Update owner metadata

```http
PATCH /api/v1/agents/{agent_id}
```

Only owner-controlled fields may be changed. Telemetry and derived fields are
read-only.

### 4.4 Rotate credential

```http
POST /api/v1/agents/{agent_id}/credentials/rotate
```

Requires an `Idempotency-Key`. The response returns the replacement plaintext
credential once and the expiry of the former credential's overlap period.

### 4.5 Disconnect

```http
POST /api/v1/agents/{agent_id}/disconnect
```

Requires an `Idempotency-Key`. The operation revokes all credentials, ends
health evaluation, preserves history, and returns:

```json
{
  "agent_id": "agt_01J...",
  "lifecycle_status": "disconnected",
  "credentials_revoked": 2,
  "external_runtime_stopped": false
}
```

### 4.6 Archive

```http
POST /api/v1/agents/{agent_id}/archive
```

Archive revokes active credentials and hides the agent from default active
queries. It does not delete history.

## 5. Heartbeat API

```http
POST /api/v1/agents/{agent_id}/heartbeats
```

Request:

```json
{
  "event_id": "evt_01J...",
  "contract_version": "1.0",
  "sent_at": "2026-07-23T18:42:00Z",
  "agent_version": "1.4.2",
  "build_sha": "4fd982a",
  "environment": "production",
  "reported_status": "healthy",
  "checks": [
    {
      "name": "provider_access",
      "status": "healthy",
      "latency_ms": 18,
      "error_code": null
    }
  ]
}
```

Constraints:

- `event_id` is unique per agent.
- `checks` contains at most 20 items.
- Check names and error codes are bounded identifiers.
- Free-form check payloads are not accepted.
- Atlas uses server receive time for liveness.
- The accepted response may be replayed for an identical duplicate.
- Reuse of an event identity with different content returns `409`.

Response status is `202 Accepted`:

```json
{
  "data": {
    "event_id": "evt_01J...",
    "agent_id": "agt_01J...",
    "accepted_at": "2026-07-23T18:42:01Z",
    "lifecycle_status": "connected",
    "observed_health": "online"
  },
  "meta": {
    "correlation_id": "corr_01J..."
  }
}
```

## 6. Execution API

```http
PUT /api/v1/agents/{agent_id}/executions/{execution_id}
```

Request:

```json
{
  "contract_version": "1.0",
  "status": "failed",
  "trigger": "schedule",
  "started_at": "2026-07-23T18:30:00Z",
  "completed_at": "2026-07-23T18:31:12Z",
  "duration_ms": 72000,
  "summary": "Provider did not respond before the configured timeout.",
  "error_code": "PROVIDER_TIMEOUT",
  "correlation_id": "agent-correlation-92",
  "agent_version": "1.4.2",
  "build_sha": "4fd982a"
}
```

Allowed statuses:

```text
queued -> running -> succeeded
                  -> failed
                  -> cancelled
                  -> skipped
```

Agents may report a terminal execution in one request. Atlas rejects a
terminal-to-running regression or conflicting immutable timestamps.

The request is idempotent for the same agent, execution identity, and
representation. Atlas returns `201` when first created and `200` when an
existing execution is updated or replayed.

## 7. Read APIs

Owner-authenticated dashboard reads include:

```text
GET /api/v1/executions
GET /api/v1/executions/{execution_id}
GET /api/v1/alerts
GET /api/v1/alerts/{alert_id}
POST /api/v1/alerts/{alert_id}/acknowledge
GET /api/v1/activity
```

These paths expose Atlas-owned projections and do not accept agent
credentials.

## 8. Retry contract

| Response | Agent behavior |
| --- | --- |
| `200`, `201`, `202` | Accepted; do not retry except on local uncertainty with the same identity |
| `400`, `401`, `403`, `404`, `409`, `422` | Do not blindly retry; correct configuration or payload |
| `408`, `429`, `500`, `502`, `503`, `504` | Retry with bounded exponential backoff and jitter |

Agents must cap retry queues. Old heartbeats may be dropped; the newest
heartbeat establishes current liveness. Execution updates retain their stable
identity until accepted or explicitly abandoned.

## 9. Payload minimization

The maximum request body for an MVP telemetry operation is 64 KiB.

The API rejects fields or values that appear to contain secrets. The agent is
responsible for redacting summaries before transmission. Atlas may apply
additional server-side redaction and store a rejection audit event without
storing the rejected sensitive value.

## 10. Compatibility

- Contract version `1.0` is required in agent telemetry.
- Additive optional response fields do not break compatibility.
- Removing fields, changing meanings, or narrowing accepted states requires a
  new major contract version.
- Atlas may accept more than one major version during a documented migration
  window.
- Unsupported versions return a structured `426 Upgrade Required` response.

## 11. OpenAPI and client examples

Implementation must publish the accepted routes in Atlas OpenAPI and include
at least:

- a curl integration example;
- a plain Python example with no framework dependency;
- a TypeScript example;
- contract tests proving a third-party client can integrate without importing
  Atlas server packages.
