# Atlas Repository Handoff

## Current Handoff Snapshot

As of 2026-07-24:

- ADP-006 has merged WO-064 through WO-070 for the Agent Visibility and
  Lifecycle MVP.
- Root `/` is the public Atlas landing page. The active authenticated product
  shell is rooted at `/control-center`.
- Active MVP navigation is limited to Overview, Agents, Executions, Alerts, and
  Activity under `/control-center`.
- Owner-enrolled agents use one-time Atlas telemetry credentials. Atlas accepts
  authenticated heartbeats and execution summaries, derives observed health,
  opens/resolves alerts, records material activity, and supports owner
  lifecycle actions: rotate credential, disconnect, reconnect, and archive.
- Atlas does not host, deploy, schedule, execute, pause, resume, stop, or
  maintain external agent runtimes.
- WO-071 is blocked. Hosted API readiness reports
  `agent_credential_pepper_missing` and
  `agent_credential_pepper_key_id_missing`; production Render environment
  values must be provisioned outside the repository before hosted
  reference-agent verification can complete.
- Do not record owner subject values, cookies, generated agent tokens, provider
  credentials, database URLs, or credential pepper values in source, logs,
  screenshots, pull requests, or chat.

## Recommended orientation order

1. `AGENTS.md`
2. `PROJECT.md`
3. `ROADMAP.md`
4. `docs/architecture/README.md`
5. `docs/decisions/README.md`
6. `docs/governance/README.md`
7. This handoff guide
8. `docs/implementation-plans/ADP-006-agent-visibility-lifecycle-mvp.md`
9. `docs/reviews/WO-071-hosted-reference-agent-verification-and-adp-closeout-blocker-report.md`

## Active direction

Atlas is governed as a single-owner agent visibility and lifecycle control
center for externally operated agents.

Non-negotiable boundaries:

- External agents call Atlas; Atlas does not call them in the MVP.
- Atlas does not host or stop external runtimes.
- Agent credentials are scoped to one agent and shown once.
- Reported state is never presented as Atlas-observed truth.
- Disconnect revokes Atlas trust and preserves history.
- Existing production migrations and historical evidence are not deleted.
- Deferred capabilities are not silently reactivated.

## Current implementation

Reusable foundations exist:

- Next.js application shell and design system
- public landing page and authenticated `/control-center` shell
- FastAPI API and contract conventions
- Google OIDC owner identity
- owner sessions and CSRF
- PostgreSQL and Alembic
- structured errors and correlation
- audit and redaction foundations
- Netlify and Render deployment
- local tests and CI

The active MVP through WO-070 includes:

- active five-destination navigation
- owner-created agent enrollment
- per-agent credential persistence
- one-time credential issuance
- credential rotation and revocation
- heartbeat ingestion
- external execution ingestion
- observed versus reported health
- health evaluator
- live alert derivation
- live agent detail for database-backed agents
- live Overview, Agents, Executions, Alerts, and Activity surfaces
- production fixture and synthetic-data quarantine

The source also contains broad execution-platform capabilities from the former
direction, including approvals, manual handling, connectors, OAuth, governed
knowledge, Gmail operational services, queues, schedulers, webhooks, policies,
and artifacts. Those capabilities are dormant or historical for the active MVP
unless separately reactivated.

## Next governance step

WO-071 hosted reference-agent verification and ADP-006 closeout is the next
active gate. It remains blocked until the production Render API environment has
the required agent credential pepper settings.

After the hosted environment is provisioned, complete WO-071 by verifying:

- enrollment and first connection;
- heartbeat loss and recovery;
- successful and failed execution reporting;
- credential rotation;
- disconnect, reconnect, and archive;
- reference-agent evidence from independent curl, Python, and TypeScript
  clients.

## Existing user work

The previously uncommitted repository-direction documentation has been
reconciled into the active docs branch. Preserve any remaining uncommitted local
work unless the Repository Maintainer explicitly asks to discard it.
