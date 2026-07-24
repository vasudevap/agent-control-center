# Atlas Agent Visibility MVP Product Requirements

**Status:** Accepted
**Version:** 1.0
**Date:** 2026-07-23
**Product Owner:** Repository Maintainer
**Governing Decisions:** `ADR-008` and `ADR-009`

## 1. Product definition

Atlas is a single-owner agent visibility and lifecycle control center for
agents built and operated elsewhere.

Atlas gives the owner one place to:

- enroll agents;
- establish and revoke their Atlas credentials;
- see which agents are connected, late, offline, or reporting degradation;
- review agent-reported executions and failures;
- receive and resolve operational alerts;
- see versions, environments, build identities, and recent activity;
- disconnect or archive an agent without losing history.

Atlas does not deploy, schedule, execute, pause, resume, or terminate external
agent runtimes in the MVP.

## 2. Problem statement

Independently built agents tend to expose inconsistent operational signals.
Their owner lacks a common answer to basic questions:

- Which agents still exist?
- Which agents are reporting?
- Which version is running?
- Which agents are late or offline?
- What failed recently?
- Which failures require attention?
- Which agents are still trusted to send data?
- How can an agent be disconnected without erasing its history?

Atlas standardizes those answers without requiring ownership of the agents'
runtime, hosting platform, provider integrations, or internal architecture.

## 3. Primary user

The initial user is one authenticated owner who builds or commissions agents
and operates them across external environments.

The MVP does not introduce teams, roles, organizations, tenants, delegated
administration, or multiple owners.

## 4. Product principles

1. **Visibility before control.** Atlas must report what it knows without
   claiming authority it does not possess.
2. **Trust is explicit.** Every agent has an individual credential and
   revocable Atlas relationship.
3. **Observed and reported state differ.** Atlas receipt time and derived
   health are not replaced by agent self-assessment.
4. **History survives disconnection.** Operational evidence is retained when
   trust ends.
5. **One contract, many agents.** Integration must not require agent-specific
   Atlas code.
6. **Minimum telemetry.** Agents send structured operational metadata, not
   secrets or business content.
7. **Safe by default.** Enrollment is owner-created, credentials are
   least-privilege, and inactive capabilities remain out of the product path.

## 5. Active domain

| Object | Purpose |
| --- | --- |
| Agent | Owner-managed registration and stable Atlas identity |
| Agent credential | Secret used by one agent to submit telemetry |
| Heartbeat | Authenticated liveness and bounded health report |
| Execution | Agent-reported unit of work and outcome |
| Alert | Atlas-created operational attention item |
| Activity event | Material enrollment, credential, health, alert, execution, disconnect, and archive history |
| Owner session | Authenticated first-party Atlas access |

## 6. Information architecture

The active primary navigation is:

1. Overview
2. Agents
3. Executions
4. Alerts
5. Activity

Approvals, Connectors, Policies, Artifacts, Knowledge, Settings, and
Atlas-initiated Runs are not active MVP destinations.

## 7. Functional requirements

### 7.1 Owner identity

- The owner must authenticate through the accepted Google OIDC boundary.
- Owner sessions must retain existing secure cookie, expiry, revocation, and
  CSRF protections.
- Agent credentials must never authenticate a human dashboard session.

### 7.2 Agent enrollment

- The owner can create a pending agent registration.
- Required owner fields are name, slug, environment, monitoring mode, and
  heartbeat expectation when heartbeat monitoring is selected.
- Optional owner fields include description, tags, repository reference,
  deployment reference, and expected version.
- Atlas generates a stable `agent_id`.
- Atlas issues a one-time credential and never displays it again.
- Atlas supplies a copyable configuration example containing Atlas URL,
  agent ID, credential placeholder, and contract version.
- The first accepted heartbeat transitions a pending registration to
  connected.

### 7.3 Agent credentials

- Credentials are individually attributable to one agent.
- Atlas stores no recoverable plaintext credential.
- The owner can rotate a credential.
- Rotation provides a short, explicit overlap window.
- The owner can revoke all credentials by disconnecting the agent.
- Credential creation, rotation, use, rejection, expiry, and revocation
  generate security-appropriate evidence without exposing secrets.

### 7.4 Heartbeats

- A connected agent can send authenticated heartbeats.
- Atlas records both the agent timestamp and server receive timestamp.
- Each heartbeat has a stable event identity for deduplication.
- A heartbeat may report version, build identity, environment, status, and a
  bounded set of structured checks.
- A heartbeat cannot alter owner-controlled registration fields.
- Atlas rejects credentials that do not match the path agent.
- Atlas rejects telemetry from disconnected or archived agents.

### 7.5 Executions

- Agents can create or update an execution using a stable agent-generated
  execution identity.
- Atlas accepts queued, running, succeeded, failed, cancelled, and skipped
  reported outcomes where the contract permits them.
- Execution updates are idempotent.
- Atlas rejects invalid state regressions or conflicting identity reuse.
- Executions may include bounded summaries and normalized error codes.
- Atlas does not accept unrestricted logs, prompts, provider content, or
  secrets through this contract.
- Atlas never presents a reported execution as a job it dispatched.

### 7.6 Health

- Atlas derives connection health from authenticated receipt time.
- Continuous heartbeat monitoring supports `never_seen`, `online`, `late`,
  and `offline`.
- Agent self-assessment supports `unknown`, `healthy`, `degraded`, and
  `unhealthy`.
- Observed and reported health are displayed separately.
- Activity-only agents show last activity and execution state without a false
  continuous-online claim.
- Disconnecting an agent stops missed-heartbeat evaluation.

### 7.7 Alerts

- Atlas opens an alert when a heartbeat misses its configured threshold.
- Atlas can open an alert for a failed reported check.
- Atlas can open an alert for repeated failed executions.
- Atlas deduplicates repeated alert conditions.
- Atlas records first seen, last seen, severity, source, reason, and current
  status.
- Atlas automatically resolves recoverable health alerts when the condition
  clears.
- The owner may acknowledge an alert without falsely resolving the underlying
  condition.

### 7.8 Agent detail

Agent Detail must show:

- lifecycle and credential state;
- observed connection health;
- reported health;
- version, build identity, and environment;
- last accepted heartbeat;
- expected heartbeat and next lateness threshold;
- recent executions;
- open and recently resolved alerts;
- material activity;
- repository and deployment references where configured.

It must not show simulated pause, resume, run, connector, approval, policy, or
tool controls.

### 7.9 Disconnect, reconnect, and archive

- Disconnect revokes all agent credentials.
- Disconnect rejects subsequent telemetry.
- Disconnect preserves heartbeats, executions, alerts, and activity.
- The UI must state that the external runtime may still be running.
- Reconnect requires a new owner-issued credential.
- Archive removes the agent from default active views without deleting
  history.
- Archived agents cannot submit telemetry.

### 7.10 Activity and audit

- The owner can read material lifecycle and operational activity.
- Activity includes enrollment, first connection, credential lifecycle,
  health transitions, execution outcomes, alerts, disconnect, reconnect, and
  archive.
- Security-sensitive evidence remains in the durable audit domain.
- Routine dashboard reads should not create noisy material activity.
- Audit records are not editable or deletable through the product.

## 8. Non-functional requirements

### 8.1 Security

- TLS is required outside local development.
- Agent credentials are high entropy, shown once, stored using a
  non-reversible verifier, and redacted everywhere.
- Authentication and authorization fail closed.
- Credentials are bound to one agent and telemetry-write scope.
- Ingestion is rate- and size-limited.
- Inputs are schema validated and treated as untrusted.

### 8.2 Reliability

- Heartbeat ingestion is idempotent by event identity.
- Execution reporting is idempotent by agent and execution identity.
- Agents receive structured retry guidance.
- A health evaluator may run repeatedly without duplicating open alerts.
- Database changes include forward migration and rollback expectations.

### 8.3 Performance

- Normal list and detail reads should complete within one second at MVP scale,
  excluding hosting cold starts.
- A valid telemetry report should normally be accepted within two seconds.
- The initial target is up to 100 registered agents and 100,000 retained
  execution summaries without architectural redesign.

### 8.4 Privacy and minimization

- Telemetry is metadata-first.
- Full prompts, messages, documents, attachments, provider payloads, tokens,
  and arbitrary logs are prohibited by default.
- Error summaries are bounded and redacted.
- Retention is explicit and can be revised through a later accepted decision.

### 8.5 Accessibility and responsiveness

- Active workflows support keyboard operation and visible focus.
- Status is never conveyed by color alone.
- Tables have usable mobile representations.
- Loading, empty, error, stale, disconnected, and archived states are explicit.

## 9. MVP exclusions

The active MVP excludes:

- Atlas-hosted agent execution;
- manual run or cancel commands;
- scheduling and orchestration;
- agent source or deployment management;
- connector and provider credential management;
- Gmail or Drive operations;
- approval workflows;
- policy evaluation;
- governed knowledge;
- artifact content;
- prompt and model tracing;
- cost management;
- outbound webhook delivery;
- multi-user and multi-tenant operation;
- remote process termination;
- multi-agent collaboration.

Excluded code may remain dormant until separately removed or reactivated.

## 10. Success criteria

The MVP succeeds when:

1. The owner can enroll an agent and receive a one-time credential.
2. An independently deployed agent can connect without Atlas-specific server
   code.
3. A valid heartbeat makes the agent visibly connected.
4. Missed heartbeats create and later resolve an alert.
5. Agent-reported and Atlas-observed health are visibly distinct.
6. An agent can idempotently report a successful or failed execution.
7. Agent Detail shows live registration, health, version, execution, alert,
   and activity data.
8. Credential rotation succeeds without exposing stored plaintext.
9. Disconnect immediately prevents additional accepted telemetry while
   retaining history.
10. Three independently built agents integrate through the same published
    contract and no agent-specific Atlas route or schema.
11. Synthetic fixture records are not required for normal production use.
12. The active navigation contains only Overview, Agents, Executions, Alerts,
    and Activity.

## 11. Future capabilities

Future decisions may add desired-state commands, schedules, approvals,
connectors, policies, artifacts, knowledge, runtime deployment, or external
product clients. None are implied or authorized by this PRD.

## 12. Acceptance

This specification supersedes
`docs/specifications/product-requirements.md` for active product work.
Historical implementation remains governed by the documents and commits under
which it was delivered.
