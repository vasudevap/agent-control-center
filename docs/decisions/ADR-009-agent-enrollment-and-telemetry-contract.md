# ADR-009 - Agent Enrollment, Authentication, and Telemetry Contract

**Status:** Accepted
**Date:** 2026-07-23
**Decision Owner:** Repository Maintainer
**Accepted:** 2026-07-23
**Accepted By:** Repository Maintainer
**Scope:** Agent identity, trust establishment, REST telemetry, and credential lifecycle
**Related Decision:** `ADR-008 - Atlas Agent Visibility and Lifecycle Control Center`

---

## Context

ADR-008 places agent runtimes outside Atlas and requires agents to report into
Atlas. The existing API authentication boundary was designed for one globally
configured external product client. It does not provide a credential identity,
scope, rotation lifecycle, or revocation boundary for each enrolled agent.

The new product direction requires a contract that is simple enough to
implement in independently built agents while preserving least privilege,
revocation, replay resistance, idempotency, auditability, and payload
minimization.

## Decision

The owner enrolls agents. Anonymous or unrestricted agent self-registration is
not allowed.

Atlas creates a pending registration and returns:

- a stable `agent_id`;
- the canonical Atlas API base URL;
- a one-time plaintext agent credential;
- the supported API contract version;
- the configured heartbeat expectation.

The plaintext credential is shown once. Atlas stores only a non-reversible
verifier and metadata required for lookup, rotation, revocation, and audit.

An agent calls Atlas over HTTPS. Atlas does not require an agent URL and does
not initiate a network connection to the agent in the MVP.

## Authentication

The MVP will use a high-entropy per-agent bearer credential over TLS:

```http
Authorization: Bearer <agent-credential>
```

Each credential is bound to exactly one `agent_id` and the agent-telemetry
write scope. A credential for one agent must never read or write another
agent's resources.

Atlas stores:

- a public credential identifier;
- a non-reversible credential verifier;
- the bound agent identity;
- status;
- creation, last-used, expiry, rotation, and revocation timestamps;
- audit provenance.

The existing external-client HMAC implementation may remain for historical
compatibility, but it is not the agent authentication model.

## Credential lifecycle

- Initial issuance occurs during owner-authenticated enrollment.
- Rotation issues a new credential once and allows a short, explicit overlap
  period before the former credential expires.
- Disconnect revokes all credentials for the agent.
- Reconnect requires owner-authenticated issuance of a new credential.
- Archive revokes credentials if they are not already revoked.
- Credentials are never returned by list or detail APIs.
- Atlas audit and logs must never contain plaintext credentials.

## REST contract

The minimum agent write contract is:

```text
POST /api/v1/agents/{agent_id}/heartbeats
PUT  /api/v1/agents/{agent_id}/executions/{execution_id}
```

The minimum owner lifecycle contract is:

```text
POST  /api/v1/agents
GET   /api/v1/agents
GET   /api/v1/agents/{agent_id}
PATCH /api/v1/agents/{agent_id}
POST  /api/v1/agents/{agent_id}/credentials/rotate
POST  /api/v1/agents/{agent_id}/disconnect
POST  /api/v1/agents/{agent_id}/archive
```

The exact schemas, error codes, pagination, and compatibility rules are defined
in `docs/specifications/agent-integration-api.md`.

## Heartbeats

A heartbeat is an append-oriented observation. It includes:

- a client-generated event identity;
- agent timestamp;
- contract version;
- agent version and optional build identity;
- environment;
- reported status;
- a bounded collection of structured checks.

Atlas records server receive time independently. Derived liveness uses the
server receive time, not the agent clock.

Atlas must deduplicate a repeated heartbeat event identity for the same agent.
A heartbeat cannot rename the agent, change owner-controlled metadata, grant
permissions, or alter credential state.

## Executions

An execution is created and updated using an agent-generated stable
`execution_id`. The `PUT` operation is idempotent.

An execution report may contain:

- status;
- trigger label;
- started and completed timestamps;
- duration;
- bounded outcome summary;
- normalized error code;
- correlation identity;
- agent version and build identity.

Atlas rejects invalid state regressions and conflicting reuse of an execution
identity.

## Health and alert derivation

Atlas stores three distinct forms of state:

1. Owner-declared metadata.
2. Agent-reported status and checks.
3. Atlas-observed and Atlas-derived state.

Atlas derives `never_seen`, `online`, `late`, and `offline` from authenticated
receipt times and the configured heartbeat expectation. Agent-reported
`healthy`, `degraded`, or `unhealthy` remains visibly separate.

Atlas may create or resolve alerts for:

- missed heartbeat thresholds;
- failed reported checks;
- repeated failed executions;
- version or environment mismatch;
- credential or ingestion abuse.

## Payload controls

Agent telemetry must not contain:

- credentials, secrets, API keys, OAuth tokens, or session values;
- full prompts or model context by default;
- full email, document, attachment, or other business content;
- arbitrary unbounded logs;
- executable code or serialized objects;
- protected health information or other unnecessary sensitive content.

Atlas validates payload size, field length, timestamp tolerance, enumerations,
and structured check counts before persistence.

## Availability and retry behavior

Agents should use bounded exponential backoff for transient failures.
Heartbeats must not accumulate without limit during an Atlas outage; a later
heartbeat can re-establish current liveness. Execution updates are retried using
the same stable execution identity.

Atlas returns structured errors and a correlation identity. `429` and `5xx`
responses are retryable unless the response says otherwise. Authentication,
authorization, validation, lifecycle, and conflict errors are not blindly
retried.

## Security consequences

- A compromised agent credential can submit telemetry only for its bound
  agent.
- Bearer credentials require TLS and careful secret handling in the external
  runtime.
- Atlas cannot prove that reported internal checks are truthful.
- Rate limits, payload limits, audit evidence, and disconnect controls reduce
  but do not eliminate ingestion abuse.
- The owner must stop or remove an external runtime in its hosting environment;
  Atlas credential revocation does not do so.

## Implementation authority

This ADR selects the trust and contract model. It does not authorize code,
schema, production credential, or deployment changes. Those require an
accepted Engineering Specification and Work Orders.

## Revisit triggers

Revisit this decision if:

- machine identity certificates or workload identity become available;
- multiple organizations require isolated issuers;
- bearer credential distribution becomes operationally unacceptable;
- agents require read or command scopes;
- streaming telemetry volume exceeds the REST model;
- regulated workloads require stronger device or workload attestation.
