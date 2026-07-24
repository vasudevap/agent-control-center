# Atlas Agent Control Center

## 1. Project purpose

Atlas is a single-owner agent visibility and lifecycle control center for AI
agents built, deployed, scheduled, and operated outside Atlas.

The project has three equal objectives:

1. Build a useful production-quality control center for agent identity,
   connection health, execution visibility, alerts, and trust lifecycle.
2. Develop practical skill in enterprise AI architecture, API security,
   observability, governance, and product delivery.
3. Produce professional portfolio evidence demonstrating Enterprise and AI
   Solution Architecture through honest system boundaries and working
   implementation.

## 2. Product vision

Give an agent owner one calm, trustworthy place to answer:

- Which agents are enrolled?
- Which agents are currently connected, late, offline, or disconnected?
- Which version and build is reporting?
- What executions have agents reported?
- What failed and what requires attention?
- Which credentials remain trusted?
- What changed, and when?

Atlas controls its relationship with an agent. It does not claim to control the
agent's external runtime.

## 3. Active MVP

The active MVP provides:

- Google OIDC owner authentication
- Agent enrollment
- Stable Atlas agent identities
- Per-agent credentials
- Credential rotation and revocation
- Authenticated heartbeat ingestion
- Authenticated execution reporting
- Observed and reported health
- Alert creation, acknowledgment, and resolution
- Agent lifecycle activity
- Disconnect, reconnect, and archive
- Overview, Agents, Executions, Alerts, and Activity surfaces
- PostgreSQL persistence
- Metadata-only audit evidence
- Netlify and Render deployment

## 4. Explicit MVP exclusions

The active MVP does not provide:

- Agent source-code management
- Agent deployment or process hosting
- Atlas-initiated run, pause, resume, cancel, restart, or stop commands
- Agent scheduling or orchestration
- Queue workers for agent execution
- Provider connector or credential management
- Gmail or Google Drive agent behavior
- Human approval workflows
- Policy evaluation
- Governed knowledge
- Artifact content management
- Prompt, model, or trace ingestion
- Multi-user or multi-tenant operation
- External product-client behavior

Existing implementations of excluded capabilities are retained as dormant or
historical evidence until separately reactivated or removed.

## 5. Primary user

The initial user is the repository owner, who builds or commissions agents and
operates them in external environments.

Future teams, roles, organizations, and tenants require separate product and
architecture decisions.

## 6. Operating model

The owner enrolls an agent in Atlas and receives:

- an Atlas API URL;
- a stable `agent_id`;
- a one-time agent credential;
- the supported contract version;
- the expected heartbeat settings.

The owner configures those values in the external runtime. The agent calls
Atlas over HTTPS.

Atlas does not require an agent URL and does not initiate a connection to the
agent in the MVP.

## 7. Ownership boundaries

| Concern | Owner |
| --- | --- |
| Agent code, deployment, process, schedule, tools, model, provider credentials, and business configuration | External agent environment |
| Registration, agent credential lifecycle, accepted telemetry, derived health, alerts, lifecycle, activity, and audit | Atlas |
| Version, build, checks, health report, and execution outcome | Agent report stored as untrusted reported state |
| Last authenticated contact and missed-heartbeat calculation | Atlas observation |

## 8. Active domain

- Agent
- Agent credential
- Heartbeat
- Execution
- Health
- Alert
- Activity event
- Audit event
- Owner session

`Execution` is work reported by an external agent. It is not a job dispatched
by Atlas.

## 9. Design principles

- Architecture before implementation
- Honest product boundaries
- Least privilege
- Explicit trust lifecycle
- Observed state separated from reported state
- Secure by design
- Metadata minimization
- Observable by default
- History retained across disconnection
- One generic contract for independent agents
- Progressive complexity
- Documentation as a product artifact

## 10. Success criteria

The MVP succeeds when:

- the owner can enroll an agent and receive a one-time credential;
- a valid first heartbeat visibly connects the agent;
- missed heartbeats create and resolve alerts;
- reported health and observed health remain distinct;
- execution updates are idempotent and visible;
- credential rotation works without recoverable plaintext storage;
- disconnect immediately rejects further telemetry without deleting history;
- three independently built agents use the same published contract;
- active product surfaces are service-backed and do not require synthetic
  production data;
- product language does not imply Atlas executed or stopped external work;
- architecture, security, API, design, implementation, and evidence remain
  synchronized.

## 11. Technology baseline

| Area | Technology |
| --- | --- |
| Frontend | Next.js and strict TypeScript |
| Backend | FastAPI and Python |
| Database | PostgreSQL with SQLAlchemy and Alembic |
| Owner identity | Google OIDC |
| Agent authentication | Per-agent bearer credential over TLS |
| Hosting | Netlify, Render API, Render PostgreSQL |
| Health evaluation | Bounded scheduled evaluator |
| Testing | Vitest, React Testing Library, Pytest, Ruff, MyPy |
| Documentation | Markdown in Git |

Queues, Redis, LangChain, LangGraph, Temporal, MCP, and runtime frameworks are
not part of the active MVP technology baseline.

## 12. Source of truth

Authority follows:

1. `AGENTS.md`
2. Accepted ADRs and active architecture
3. Accepted product and design specifications
4. Accepted Engineering Specification and Work Order
5. Governance procedures
6. Recommendations and historical references

Active direction:

- ADR-008
- ADR-009
- DDR-003
- `docs/specifications/atlas-agent-visibility-mvp-requirements.md`
- `docs/specifications/agent-integration-api.md`
- `docs/architecture/14-agent-visibility-mvp-target-architecture.md`
- `docs/design/12-agent-visibility-mvp-experience.md`
- `docs/implementation-plans/atlas-agent-visibility-mvp-reset.md`

## 13. Historical direction

The repository previously pursued an Atlas-owned execution platform with
Gmail, connectors, approvals, knowledge, scheduling, queueing, and an external
product-client contract.

That work is retained as architecture, implementation, security, deployment,
and learning evidence. ADR-003, ADR-004, and ADR-005 are superseded for active
work by ADR-008. Completed specifications, Work Orders, reviews, migrations,
and release records remain historical facts.

## 14. Current status

The direction reset is documented and accepted. ES-009, ADP-006, and WO-064
through WO-070 are implemented and merged.

The source now includes active owner enrollment, per-agent credentials,
heartbeat ingestion, execution ingestion, derived health, alerts, material
activity, and live product surfaces under `/control-center`.

WO-071 hosted reference-agent verification remains blocked until the production
Render API environment is provisioned with the required agent credential pepper
configuration.
