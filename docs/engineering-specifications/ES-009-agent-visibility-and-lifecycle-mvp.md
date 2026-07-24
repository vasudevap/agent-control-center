# ES-009 - Agent Visibility and Lifecycle MVP

**Status:** Accepted
**Owner:** Repository Maintainer
**Review Owner:** Repository Maintainer
**Date:** 2026-07-24
**Version:** 0.2
**Implementation Authorization:** Granted for ADP-006 and WO-064 through WO-071 by Repository Maintainer on 2026-07-24.
**Governing Decisions:** `ADR-008`, `ADR-009`, and `DDR-003`
**Governing Plan:** `docs/implementation-plans/atlas-agent-visibility-mvp-reset.md`

## 1. Purpose

Translate the accepted Agent Visibility MVP direction into an implementable
engineering boundary.

ES-009 must retire the active product's execution-platform implications while
preserving reusable foundations and historical evidence.

## 2. Intended outcome

After implementation:

- the owner enrolls and manages individual agent trust relationships;
- external agents authenticate with per-agent credentials;
- agents report heartbeats and executions through the accepted REST contract;
- Atlas derives connection health and operational alerts;
- active dashboard surfaces are live and free of normal production fixture
  fallback;
- disconnect, reconnect, and archive preserve history;
- dormant capabilities no longer appear in the active product path;
- three independent reference agents prove contract generality.

## 3. Governing references

- `AGENTS.md`
- `PROJECT.md`
- `ROADMAP.md`
- `docs/decisions/ADR-008-atlas-agent-visibility-control-center.md`
- `docs/decisions/ADR-009-agent-enrollment-and-telemetry-contract.md`
- `docs/design/decisions/DDR-003-agent-visibility-mvp-information-architecture.md`
- `docs/specifications/atlas-agent-visibility-mvp-requirements.md`
- `docs/specifications/agent-integration-api.md`
- `docs/architecture/14-agent-visibility-mvp-target-architecture.md`
- `docs/design/12-agent-visibility-mvp-experience.md`
- `docs/implementation-plans/atlas-agent-visibility-mvp-reset.md`
- canonical governance under `docs/governance/`

## 4. Proposed scope

### 4.1 Active surface and route disposition

- Reduce primary navigation to Overview, Agents, Executions, Alerts, and
  Activity.
- Remove simulated operational controls from active routes.
- Define explicit disposition for every current dashboard and API route.
- Keep dormant capability routes inaccessible from normal product navigation.
- Disable synthetic smoke seeding from normal production behavior.
- Remove production fixture fallback from active pages.

### 4.2 Agent registration

- Extend or replace the current registration persistence with active MVP
  fields.
- Add owner-authenticated create, read, list, and metadata-update operations.
- Implement pending, connected, disconnected, and archived lifecycle rules.
- Preserve stable IDs and historical references.

### 4.3 Agent credentials

- Add normalized `agent_credentials` persistence.
- Generate high-entropy credentials using an accepted cryptographic source.
- Return plaintext only at issuance and rotation.
- Store non-reversible verifiers.
- Bind credentials to one agent and telemetry-write scope.
- Implement last-use, expiry, rotation-overlap, revocation, and audit state.
- Implement rotate, disconnect, reconnect, and archive credential effects.

### 4.4 Heartbeat ingestion

- Implement the accepted heartbeat route and schema.
- Authenticate and bind the agent identity.
- Validate contract version, event identity, timestamps, checks, sizes, and
  prohibited values.
- Deduplicate identical replay and reject conflicting replay.
- Record agent send and Atlas receive time separately.
- Update last-contact projection without mutating owner fields.

### 4.5 Execution ingestion

- Implement the accepted idempotent execution route.
- Persist agent-scoped external execution identities.
- Enforce transition, timestamp, terminal-state, and immutable-field rules.
- Store bounded summaries and normalized error codes.
- Preserve correlation and version/build metadata.
- Make clear in API and UI that Atlas did not dispatch the execution.

### 4.6 Health evaluator

- Implement `heartbeat` and `activity_only` monitoring modes.
- Define exact tolerance and offline threshold formulas.
- Use server receive time for liveness.
- Acquire a database-backed evaluation lease.
- Process bounded batches and support safe rerun.
- Materialize observed and reported health separately.
- Record material transitions and evaluator freshness.

### 4.7 Alert lifecycle

- Implement stable condition keys.
- Open and deduplicate missed-heartbeat, failed-check, repeated-failure,
  version mismatch, environment mismatch, and security-ingestion conditions.
- Support open, acknowledged, and resolved states.
- Automatically recover eligible conditions.
- Preserve first and last seen evidence.
- Ensure acknowledgment does not resolve the source condition.

### 4.8 Activity and audit

- Add an owner-facing material activity projection.
- Preserve durable audit as a separate domain.
- Stop treating routine successful reads as material activity.
- Record credential and lifecycle actions without plaintext or rejected
  sensitive values.

### 4.9 Active dashboard integration

- Implement live Overview, Agents, Agent Detail, Executions, Alerts, and
  Activity.
- Resolve Agent Detail using live agent identity.
- Implement enrollment and one-time credential copy.
- Implement rotation, disconnect, reconnect, and archive confirmations.
- Implement required loading, empty, first-use, error, stale, partial,
  disconnected, and archived states.

### 4.10 Monitoring and readiness

- Expand readiness to include database access and required configuration.
- Expose evaluator freshness.
- Add telemetry acceptance/rejection and alert metrics.
- Preserve structured logs, redaction, and correlation.

### 4.11 Hosted migration

- Use forward Alembic migrations.
- Do not roll back or delete existing production tables.
- Quarantine synthetic records from active projections.
- Deploy the evaluator through the accepted Render mechanism.
- Preserve a source and deployment rollback path.

### 4.12 Reference-agent verification

- Provide curl, plain Python, and TypeScript client examples.
- Implement three independent reference agents or clients that import no Atlas
  server packages.
- Verify enrollment, first connection, health loss, recovery, execution
  success/failure, rotation, disconnect, reconnect, and archive.

## 5. Explicitly out of scope

- Removing historical migrations or completed evidence
- Destructive deletion of legacy production tables
- Atlas-directed runtime commands
- Agent deployment or schedule management
- Connector and provider credential management
- Gmail or Drive operations
- Approvals, policies, knowledge, and artifacts
- Webhook reactivation
- Multi-user or multi-tenant behavior
- Streaming ingestion
- OpenTelemetry trace ingestion
- Published agent SDK package
- New orchestration framework

## 6. Data requirements

### 6.1 Current-to-target mapping

The current database head is `0017_gmail_send_outcomes`. ES-009 starts at
forward migration `0018_agent_visibility_lifecycle_mvp`. Existing migrations
and tables remain intact.

| Current object | Current meaning | ES-009 disposition |
| --- | --- | --- |
| `agent_registrations` | Generic descriptor and runtime-capability registry | Extend in place as the stable agent identity table. Preserve existing columns for historical descriptors. Add active MVP lifecycle, owner, monitoring, and projection fields. |
| `agent_runs` / `agent_run_steps` | Atlas-created run lifecycle and steps | Keep as historical/dormant runtime-control evidence. Do not use for agent-reported executions. |
| `audit_events` | Durable security and operational audit | Keep as durable audit. Add ES-009 event types; do not store plaintext credentials or rejected sensitive values. |
| `connectors`, `approvals`, `knowledge`, webhook tables | Deferred product capabilities | Keep dormant. They must not feed active MVP navigation or normal active projections. |
| `hosted-runtime-smoke-agent` and `synthetic.smoke` records | Hosted cutover evidence fixtures | Mark as synthetic and exclude from active default projections. Retain for historical evidence. |

Existing `agent_registrations` rows are backfilled as
`registration_source='legacy_descriptor'`, except rows with
`slug='hosted-runtime-smoke-agent'` or capability `synthetic.smoke`, which are
backfilled as `registration_source='synthetic_smoke'`. Legacy and synthetic rows
default to `active_surface_visible=false` and do not appear in active fleet
views unless an explicit historical/debug filter is added in a later accepted
scope.

### 6.2 Target schema

`agent_registrations` remains the agent root table.

Add these columns:

| Column | Type | Rules |
| --- | --- | --- |
| `owner_user_id` | FK to `users.user_id`, nullable for legacy rows | Required for new owner-enrolled agents. |
| `registration_source` | string(40) | `owner_enrolled`, `legacy_descriptor`, or `synthetic_smoke`. |
| `active_surface_visible` | boolean | Default `true` for new owner-enrolled agents, `false` for legacy/synthetic backfill. |
| `lifecycle_status` | string(40) | `pending`, `connected`, `disconnected`, or `archived`. |
| `environment` | string(80) | Required for new agents; bounded identifier. |
| `monitoring_mode` | string(40) | `heartbeat` or `activity_only`. |
| `heartbeat_interval_seconds` | integer nullable | Required for `heartbeat`; min `30`, max `3600`, default `60`. Null for `activity_only`. |
| `tags` | JSON list | At most 12 bounded identifiers, max 40 chars each. |
| `repository_url` | string(500), nullable | Owner metadata only. |
| `deployment_url` | string(500), nullable | Owner metadata only. |
| `expected_version` | string(80), nullable | Compared to telemetry `agent_version` when set. |
| `first_connected_at` | timestamptz, nullable | Set by first accepted heartbeat. |
| `disconnected_at` | timestamptz, nullable | Set by disconnect. |
| `archived_at` | timestamptz, nullable | Set by archive. |
| `last_heartbeat_received_at` | timestamptz, nullable | Server receive time only. |
| `last_activity_at` | timestamptz, nullable | Last material activity or telemetry acceptance. |
| `observed_health` | string(40) | `never_seen`, `online`, `late`, `offline`, `not_monitored`, `disconnected`, or `archived`. |
| `reported_health` | string(40) | `unknown`, `healthy`, `degraded`, or `unhealthy`. |
| `last_agent_version` | string(80), nullable | From accepted telemetry only. |
| `last_build_sha` | string(80), nullable | From accepted telemetry only. |

Create normalized ES-009 tables:

| Table | Purpose | Required keys and constraints |
| --- | --- | --- |
| `agent_credentials` | One credential record per issued agent token | PK `credential_id`; FK `agent_id`; unique `credential_lookup_id`; status `active`, `overlap`, `revoked`, or `expired`; scope fixed to `telemetry_write`; plaintext never stored. |
| `agent_heartbeats` | Accepted heartbeat events | PK `heartbeat_id`; FK `agent_id`; FK `credential_id`; unique `(agent_id, event_id)`; stores `event_fingerprint`, `contract_version`, `sent_at`, `received_at`, telemetry version/build/environment/status, and bounded `checks_json`. |
| `agent_executions` | Agent-reported execution summaries | PK `agent_execution_id`; FK `agent_id`; unique `(agent_id, external_execution_id)`; stores `representation_hash`, status, trigger, timestamps, duration, bounded summary, normalized error code, correlation, version, build, first/last reported times, and terminal time. |
| `agent_health_evaluator_leases` | Database-backed evaluator lease | PK `lease_name`; stores `holder_id`, `lease_expires_at`, last start/completion/error, and processed counts. |
| `agent_alerts` | Owner-facing operational alerts | PK `alert_id`; FK `agent_id`; stable `condition_key`; status `open`, `acknowledged`, or `resolved`; severity; first/last seen; acknowledgement/resolution metadata; bounded evidence JSON. Enforce one active alert per `(agent_id, condition_key)` while status is open or acknowledged. |
| `agent_activity_events` | Material owner-facing activity projection | PK `activity_event_id`; nullable FK `agent_id`; source type/id; event type; severity; summary; correlation id; actor type/id; bounded metadata JSON; occurred time. |
| `agent_ingestion_rate_limits` | No-new-infrastructure ingestion limits | PK `(credential_id, route_key, window_start)`; stores request count for fixed one-minute windows. |

JSON is allowed only for bounded heartbeat checks, alert evidence, and activity
metadata. It must not store arbitrary logs, prompts, provider payloads,
documents, attachments, or secrets.

### 6.3 Retention

- Accepted heartbeat rows are retained for 90 days.
- Agent execution summaries are retained for 365 days and must support at least
  100,000 retained summaries at MVP scale.
- Alerts, material activity, credential records, and audit events are retained
  indefinitely for the MVP.
- Rejected telemetry that appears secret-bearing records only a redacted audit
  event and is not retained as a heartbeat or execution payload.

## 7. Security and ingestion requirements

### 7.1 Credential design

Agent tokens use this format:

```text
atl_agent_<credential_lookup_id>.<secret>
```

Rules:

- `credential_lookup_id` is a non-secret `cred_` prefixed identifier used only
  to find the credential row.
- `secret` is 32 bytes from Python `secrets.token_urlsafe` or an equivalent
  CSPRNG source with at least 256 bits of entropy before encoding.
- Store `verifier_hmac_sha256 = HMAC-SHA256(secret, ATLAS_API_AGENT_CREDENTIAL_PEPPER)`.
- Store `verifier_key_id = ATLAS_API_AGENT_CREDENTIAL_PEPPER_KEY_ID`.
- Verification parses the lookup id, finds one candidate credential, recomputes
  the HMAC, and compares with `hmac.compare_digest`.
- The existing `ATLAS_API_EXTERNAL_CLIENT_SECRET` must not be reused for agents.
- Plaintext is returned only on create, rotate, or reconnect responses and must
  never be logged, audited, or retrievable.

Required new settings:

| Setting | Required when | Purpose |
| --- | --- | --- |
| `ATLAS_API_AGENT_CREDENTIAL_PEPPER` | Production-like environments | HMAC verifier secret for agent credentials. |
| `ATLAS_API_AGENT_CREDENTIAL_PEPPER_KEY_ID` | Production-like environments | Rotation label for the verifier secret. |
| `ATLAS_API_AGENT_HEALTH_EVALUATOR_ENABLED` | Deployed API evaluator instance | Enables the background evaluator loop. |
| `ATLAS_API_ENABLE_SYNTHETIC_SMOKE_SEED` | Temporary owner-authorized smoke only | Gates `/api/v1/dashboard/smoke-seed`; default false. |

Rotation creates a new active credential immediately and moves the former active
credential to `overlap` for exactly 24 hours. After the overlap expires, the
former credential is treated as expired and rejected. Disconnect and archive
revoke every credential immediately.

### 7.2 Identity and authorization

- Browser lifecycle reads and mutations require the existing owner session.
- Browser mutations require CSRF and `Idempotency-Key` where the API contract
  names one.
- Agent telemetry uses only `Authorization: Bearer <agent-token>`.
- A credential is valid only for its bound `agent_id`; a valid credential used
  on another agent path returns `403` without revealing the other agent.
- Telemetry from `disconnected` or `archived` agents returns `401`.
- Telemetry from pending agents is accepted only for the agent that owns the
  credential; the first accepted heartbeat transitions the agent to connected.

### 7.3 Bounds, rate limits, and replay

- Maximum request body for heartbeat and execution ingestion is 64 KiB.
- Heartbeat `checks` accepts at most 20 items.
- Check names, error codes, slugs, environment, trigger, and tag values are
  bounded identifiers.
- Execution `summary` stores at most 500 characters after redaction.
- Per credential, Atlas accepts at most 60 telemetry write requests per
  one-minute window, including at most 30 heartbeat requests.
- Per source IP, Atlas accepts at most 600 telemetry write requests per
  one-minute window.
- Identical heartbeat replay for `(agent_id, event_id, event_fingerprint)`
  returns the original accepted response. Conflicting replay returns `409`.
- Execution updates are idempotent for
  `(agent_id, external_execution_id, representation_hash)`. Terminal-to-running
  regression and conflicting immutable timestamps return `409`.

### 7.4 Secret rejection and logging

Reject telemetry fields that match existing secret-name patterns or common
secret-value patterns. Do not log full request bodies. Rejected values are not
stored in activity, alert evidence, or audit metadata.

## 8. Health, alert, and activity rules

### 8.1 Health evaluator

Render deployment uses the existing API service; ES-009 does not add a new
Render service, queue, scheduler framework, or worker platform. The API process
may start an internal evaluator loop when
`ATLAS_API_AGENT_HEALTH_EVALUATOR_ENABLED=true`. The loop must acquire the
`agent-health-evaluator` row in `agent_health_evaluator_leases` before writing
derived health.

Exact evaluator defaults:

- tick interval: 30 seconds;
- lease TTL: 90 seconds;
- batch size: 100 agents per tick;
- stale evaluator warning: no successful completion for 180 seconds.

For `monitoring_mode='heartbeat'`:

- `never_seen`: no accepted heartbeat and lifecycle is pending or connected;
- `online`: `now <= last_heartbeat_received_at + max(2 * interval, 120 seconds)`;
- `late`: after online threshold and before offline threshold;
- `offline`: `now > last_heartbeat_received_at + max(5 * interval, 300 seconds)`.

For `monitoring_mode='activity_only'`, observed health is `not_monitored` while
active, with last activity shown separately. Disconnect sets observed health to
`disconnected`; archive sets it to `archived`.

Reported health is taken from the latest accepted heartbeat status and remains
separate from observed health.

### 8.2 Alert conditions

Stable condition keys:

| Condition | Key format | Opens when | Auto-resolves when |
| --- | --- | --- | --- |
| Missed heartbeat | `agent:{agent_id}:missed-heartbeat` | Observed health becomes late or offline | Observed health returns online, disconnect, or archive |
| Failed check | `agent:{agent_id}:check:{check_name}` | Latest heartbeat check status is degraded or unhealthy | The same check returns healthy or disappears for 3 consecutive accepted heartbeats |
| Repeated failed execution | `agent:{agent_id}:execution:repeated-failure` | 3 failed executions occur within 30 minutes | No failed execution for 60 minutes after last seen |
| Version mismatch | `agent:{agent_id}:version-mismatch` | `expected_version` is set and latest `agent_version` differs | Latest telemetry matches expected version or expected version is cleared |
| Environment mismatch | `agent:{agent_id}:environment-mismatch` | Telemetry environment differs from owner-configured environment | Latest telemetry matches configured environment |
| Security ingestion | `agent:{agent_id}:security-ingestion` | Secret-pattern or contract abuse rejection occurs | Manual acknowledgement plus no repeat for 24 hours |

Acknowledgement changes alert status to `acknowledged`; it does not resolve the
source condition. Auto-resolution keeps first/last seen evidence.

### 8.3 Activity and audit

Material activity includes enrollment, first connection, credential issuance,
rotation, overlap expiry, revocation, disconnect, reconnect, archive, observed
health transition, reported unhealthy/degraded transition, execution terminal
outcome, alert open/acknowledge/resolve, and telemetry rejection category.

Routine successful dashboard reads do not create activity events. Security and
lifecycle actions continue to write durable `audit_events`.

## 9. Route and frontend disposition

### 9.1 Backend routes

| Route family | ES-009 disposition |
| --- | --- |
| `/health/live`, `/health/ready`, `/api/v1/health` | Keep. Expand readiness for database, credential pepper config, synthetic seed disabled by default, and evaluator freshness. |
| `/api/v1/external-client/authentication/probe` | Keep only as dormant external-product-client evidence. Do not reuse for agent telemetry. |
| Current `/api/v1/agents` descriptor GET routes | Replace active meaning with owner lifecycle reads plus agent heartbeat/execution routes. Existing HMAC descriptor access becomes dormant or removed from router inclusion during the active-surface work order. |
| `POST /api/v1/agents` | Owner create enrollment, one-time credential issuance. |
| `GET /api/v1/agents`, `GET /api/v1/agents/{agent_id}`, `PATCH /api/v1/agents/{agent_id}` | Owner active fleet reads and metadata update. |
| `POST /api/v1/agents/{agent_id}/heartbeats` | Agent credential heartbeat ingestion. |
| `PUT /api/v1/agents/{agent_id}/executions/{execution_id}` | Agent credential execution ingestion. |
| `POST /api/v1/agents/{agent_id}/credentials/rotate` | Owner credential rotation with 24-hour overlap. |
| `POST /api/v1/agents/{agent_id}/disconnect` | Owner disconnect and immediate credential revocation. |
| `POST /api/v1/agents/{agent_id}/reconnect` | Owner reconnect from disconnected to pending with one-time credential issuance. |
| `POST /api/v1/agents/{agent_id}/archive` | Owner archive and immediate credential revocation. |
| `/api/v1/executions`, `/api/v1/executions/{execution_id}` | Owner reads of agent-reported executions only. |
| `/api/v1/alerts`, `/api/v1/alerts/{alert_id}`, `/api/v1/alerts/{alert_id}/acknowledge` | Owner alert reads and acknowledgement. |
| `/api/v1/activity` | Owner material activity read. |
| `/api/v1/dashboard/connectors`, `/api/v1/connectors`, `/api/v1/approvals`, `/api/v1/manual-handling`, `/api/v1/knowledge/*`, `/api/v1/runs/*` | Dormant for MVP active product. Do not call from active navigation or active dashboard pages. |
| `/api/v1/dashboard/runs` and `POST /api/v1/dashboard/runs` | Dormant. Manual run creation must not be reachable from active UI. |
| `/api/v1/dashboard/smoke-seed` | Quarantined. Available only when `ATLAS_API_ENABLE_SYNTHETIC_SMOKE_SEED=true` and never used by normal production pages. |

### 9.2 Frontend file and route inventory

| Frontend surface | ES-009 disposition |
| --- | --- |
| `apps/web/src/app/page.tsx` | Public Atlas landing page. Must not contain dashboard-only controls or imply Atlas hosts/runs external agents. |
| `apps/web/src/app/(shell)/control-center/page.tsx` and `apps/web/src/features/overview/*` | Canonical active app root at `/control-center`. Rewrite to live agent visibility overview. Remove approvals/runs fixture dependency. |
| `apps/web/src/components/layout/nav-items.ts` | Primary nav becomes Overview, Agents, Executions, Alerts, Activity under `/control-center`. Settings, Runs, Approvals, Connectors, Policies, Artifacts, and Audit are removed from normal navigation. |
| `apps/web/src/app/(shell)/control-center/agents/**`, `agents-inventory.tsx`, `agent-data.ts` | Canonical active owner-enrolled agent inventory and detail routes under `/control-center/agents`. Legacy `/agents` routes may redirect here. |
| `apps/web/src/app/(shell)/agents/[agentId]/agent-operational-controls.tsx` | Remove from active route. Replace with credential/lifecycle controls only. |
| `apps/web/src/app/(shell)/control-center/alerts/**` | Canonical active alert reads and acknowledgement route under `/control-center/alerts`. Legacy `/alerts` may redirect here. |
| `apps/web/src/app/(shell)/control-center/runs/**` | Canonical active execution inventory/detail for agent-reported executions under `/control-center/runs`. Legacy `/runs` may redirect here until `/executions` is introduced. |
| `apps/web/src/app/(shell)/control-center/audit/**` | Canonical active material activity surface under `/control-center/audit`. Legacy `/audit` may redirect here until `/activity` is introduced. |
| `apps/web/src/lib/dashboard-runtime.ts` | Replace fixture-friendly runtime functions with live agent, execution, alert, activity, enrollment, credential, and lifecycle client functions. |
| `apps/web/src/components/layout/status-bar.tsx` and `top-bar.tsx` | Remove active approvals/runs monitoring assumptions; show API/session/evaluator readiness only. |
| `apps/web/src/app/(shell)/runs/*`, `approvals/*`, `connectors/*`, `policies/*`, `artifacts/*`, `audit/*`, `settings/*` | Dormant routes. They may remain in source but must be inaccessible from normal nav and must not be used as active MVP evidence. |

Production fallback to local fixtures is removed from active pages. Local
fixture data may remain only in tests, dormant routes, or explicitly named
development fixtures that cannot be mistaken for production behavior.

## 10. Migration, rollback, and deployment

### 10.1 Migration sequence

1. Add ES-009 columns to `agent_registrations` with safe defaults and nullable
   owner fields for legacy rows.
2. Backfill `registration_source`, `active_surface_visible`,
   `lifecycle_status`, `observed_health`, and `reported_health`.
3. Create `agent_credentials`, `agent_heartbeats`, `agent_executions`,
   `agent_health_evaluator_leases`, `agent_alerts`,
   `agent_activity_events`, and `agent_ingestion_rate_limits`.
4. Add uniqueness constraints and indexes for slug/source, active fleet,
   lifecycle, observed health, last contact, credential lookup, heartbeat
   replay, execution identity, open alerts, and activity chronology.
5. Validate local upgrade and downgrade against PostgreSQL before any PR is
   considered ready.

### 10.2 Deployment and rollback

- Source rollback must not require dropping new tables.
- Production rollback defaults to forward repair unless a reviewed runbook
  authorizes a database downgrade.
- New routes must be feature-disableable through source rollback or settings
  without reactivating synthetic production behavior.
- Credential issuance cannot be rolled back by recovering plaintext.
- Evaluator disablement sets readiness/evaluator freshness to stale rather
  than falsely reporting healthy.
- Render deployment uses the existing API service with
  `ATLAS_API_AGENT_HEALTH_EVALUATOR_ENABLED=true`; no new provider resource is
  authorized by ES-009.

## 11. Verification

### 11.1 Required local command set

Run the complete local validation suite before the first implementation PR push
for any source-bearing ES-009 Work Order:

```bash
npm ci
npm run typecheck
npm run lint
npm test
npm run build
python -m pip install -c apps/api/constraints.txt -e "apps/api[dev]"
python -m mypy apps/api/src
python -m ruff check apps/api
python -m pytest apps/api
cd apps/api
ATLAS_API_DATABASE_URL="$ATLAS_API_DATABASE_URL" python -m alembic upgrade head
ATLAS_API_DATABASE_URL="$ATLAS_API_DATABASE_URL" python -m alembic downgrade base
```

Focused Work Orders may run narrower checks while iterating, but pull-request
evidence must include the relevant focused checks plus the full suite required
by `.github/workflows/ci.yml`.

### 11.2 Backend acceptance evidence

- Unit tests for lifecycle, credentials, transitions, health, alerts, redaction,
  retention selectors, and rate limits.
- Contract tests for every accepted owner and agent route.
- Integration tests against PostgreSQL for migrations, replay, idempotency,
  cross-agent authorization, evaluator leases, and alert deduplication.
- Negative tests proving disconnect/archive rejection, token/path mismatch
  rejection, secret-pattern rejection, and no plaintext credential persistence.

### 11.3 Frontend acceptance evidence

- Navigation tests proving only Overview, Agents, Executions, Alerts, and
  Activity are active destinations.
- Component and integration tests for enrollment, one-time credential copy,
  rotation, disconnect, reconnect, archive, alert acknowledgement, and live
  agent/execution/activity reads.
- Loading, empty, first-use, error, stale, partial, disconnected, archived,
  keyboard, focus, mobile, and color-independent status tests.
- Tests proving active pages do not fall back to production fixtures.

### 11.4 End-to-end acceptance evidence

- Three independent clients: curl, plain Python, and TypeScript. They must
  import no Atlas server packages.
- Evidence for enrollment, first heartbeat, online/late/offline/recovery,
  failed check, successful execution, failed execution, repeated-failure alert,
  credential rotation overlap and expiry, disconnect rejection, reconnect, and
  archive.
- Hosted verification against the accepted deployed API and frontend after
  migration.

## 12. Work Order dependency graph

The ES-009 Work Order package is created for maintainer review using the next
available repository identifiers:

| Order | Planned Work Order | Depends on | Acceptance gate |
| ---: | --- | --- | --- |
| 1 | `WO-064: Active Navigation and Synthetic Fixture Quarantine` | ES-009 accepted | Active nav and active pages no longer expose dormant capabilities or normal production fixture fallback. |
| 2 | `WO-065: Agent Visibility Schema and Migration Foundation` | WO-064 | `0018` migration, models, indexes, backfill, and migration validation are complete. |
| 3 | `WO-066: Owner Enrollment and Agent Credentials` | WO-065 | Owner enrollment, one-time credential issuance, verifier storage, rotation overlap base, and audit evidence are complete. |
| 4 | `WO-067: Heartbeat and Execution Ingestion` | WO-066 | Authenticated heartbeat and execution contracts, replay, idempotency, bounds, redaction, and rate limits are complete. |
| 5 | `WO-068: Health Evaluator and Alert Lifecycle` | WO-067 | Evaluator lease, health materialization, alert open/ack/resolve, and freshness readiness are complete. |
| 6 | `WO-069: Live Dashboard Integration` | WO-068 | Overview, Agents, Agent Detail, Executions, Alerts, and Activity use live active projections. |
| 7 | `WO-070: Disconnect, Reconnect, Archive, and Credential Closeout` | WO-069 | Lifecycle terminal/reconnect behavior, immediate rejection, retained history, and UI confirmations are complete. |
| 8 | `WO-071: Hosted Reference-Agent Verification and ADP Closeout` | WO-070 | Hosted migration, three independent clients, end-to-end acceptance evidence, rollback notes, and closeout are complete. |

ADP-006 groups `WO-064` through `WO-071` after those Work Orders are written.
Autonomous delivery may begin only after the Work Orders and ADP are accepted
and the Repository Maintainer explicitly authorizes an execution window.

## 13. Stop-and-ask triggers

Stop if work requires:

- destructive legacy data removal;
- live credential exposure;
- reuse of the external-product-client secret for agents;
- Atlas-to-agent network calls;
- new infrastructure or framework outside this specification;
- identity-provider changes;
- live third-party business data;
- deferred capability reactivation;
- weakening authentication, audit, redaction, CI, or rollback controls.

## 14. Acceptance checklist

ES-009 was accepted by the Repository Maintainer on 2026-07-24 after confirming:

- the current-to-target schema mapping in section 6 is accepted;
- the credential, verifier, rate, payload, retention, and health threshold
  values in sections 6 through 8 are accepted;
- the route and frontend disposition in section 9 is accepted;
- the migration, Render evaluator, rollback, and validation requirements in
  sections 10 and 11 are accepted;
- the Work Order sequence in section 12 is accepted as the basis for Work Order
  creation and ADP-006 planning.

Implementation remains unauthorized until the corresponding Work Orders and
ADP-006 are accepted and an autonomous execution window is explicitly
authorized by the Repository Maintainer.
