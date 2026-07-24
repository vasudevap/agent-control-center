# ADP-006: Agent Visibility and Lifecycle MVP

**Status:** Blocked - Hosted credential configuration missing
**Program ID:** ADP-006
**Type:** Autonomous Delivery Program
**Owner:** Repository Maintainer
**Created:** 2026-07-24
**Execution Window:** Authorized by Repository Maintainer on 2026-07-24
**Engineering Specification:** `docs/engineering-specifications/ES-009-agent-visibility-and-lifecycle-mvp.md`
**Work Order Set:** `WO-064` through `WO-071`

---

## 1. Purpose

Sequence the ES-009 Agent Visibility and Lifecycle MVP Work Orders into a
governed delivery program.

ADP-006 adopts the parallel frontend route change made on 2026-07-24: root
`/` is the public Atlas landing page, while the active authenticated dashboard
shell is rooted at `/control-center`. All active MVP navigation, links,
redirects, and future frontend work orders must use `/control-center/...` as
the canonical app route base unless a later accepted decision changes it.

ADP-006 does not replace individual Work Orders. Each Work Order remains the
technical scope authority for implementation, exclusions, validation,
rollback, and stop-and-ask triggers after acceptance.

## 2. Execution Authority

ES-009 was accepted by the Repository Maintainer on 2026-07-24.

ADP-006 is created for review and planning. Autonomous delivery is not
authorized until the Repository Maintainer explicitly accepts ADP-006, accepts
the Work Order set, and authorizes an execution window for the named Work
Orders.

When authorized, delivery remains bounded by ES-009, each Work Order, accepted
architecture decisions, and repository governance. Work must stop when any
Work Order stop-and-ask trigger applies.

## 3. Work Order Set

| Order | Work Order | Current State | ADP Execution Action | Completion Gate |
| ---: | --- | --- | --- | --- |
| 1 | `WO-064: Active Navigation and Synthetic Fixture Quarantine` | Completed - Merged | Reduce active navigation, remove misleading controls, and quarantine synthetic fixture behavior | Active product path exposes only honest Agent Visibility MVP destinations |
| 2 | `WO-065: Agent Visibility Schema and Migration Foundation` | Completed - Merged | Add ES-009 migration, models, constraints, indexes, and historical/synthetic backfill | PostgreSQL migration and model tests pass with legacy evidence preserved |
| 3 | `WO-066: Owner Enrollment and Agent Credentials` | Completed - Merged | Implement owner enrollment, one-time credential issuance, verifier storage, and readiness settings | Owner can create a pending agent and receive a non-recoverable one-time credential |
| 4 | `WO-067: Heartbeat and Execution Ingestion` | Completed - Merged | Implement authenticated heartbeat and execution ingestion with replay, bounds, redaction, and rate limits | Independent agents can submit accepted telemetry without Atlas runtime control |
| 5 | `WO-068: Health Evaluator and Alert Lifecycle` | Completed - Merged | Implement leased evaluator, derived health, alerts, activity, and freshness readiness | Atlas derives observed health and alert state from accepted telemetry |
| 6 | `WO-069: Live Dashboard Integration` | Completed - Merged | Replace active UI fixtures with live Overview, Agents, Agent Detail, Executions, Alerts, and Activity | Active dashboard surfaces render live ES-009 data and required states |
| 7 | `WO-070: Disconnect, Reconnect, Archive, and Credential Closeout` | Completed - Merged | Complete lifecycle actions, credential rotation/overlap, rejection, retained history, and UI confirmations | Trust lifecycle is owner-controlled without deleting history or stopping external runtimes |
| 8 | `WO-071: Hosted Reference-Agent Verification and ADP Closeout` | Blocked - Hosted credential configuration missing | Validate hosted behavior with curl, Python, and TypeScript clients; record closeout evidence | ES-009 success criteria are proven through hosted live verification |

## 4. Dependency Sequence

```text
ES-009 accepted
  -> WO-064 active surface reset
    -> WO-065 schema and migration foundation
      -> WO-066 owner enrollment and credentials
        -> WO-067 heartbeat and execution ingestion
          -> WO-068 health evaluator and alerts
            -> WO-069 live dashboard integration
              -> WO-070 lifecycle and credential closeout
                -> WO-071 hosted reference-agent verification and ADP closeout
```

## 5. Parallel Execution Notes

The ES-009 package is intentionally mostly serial because each lane consumes
state created by the prior lane.

| Lane | Work Orders | Parallel-safe conditions |
| --- | --- | --- |
| Active surface | WO-064 | First because it removes misleading product authority before new live features are added |
| Persistence | WO-065 | Serial migration foundation before service/API work |
| API trust and telemetry | WO-066, WO-067 | Serial because ingestion depends on credential issuance and verifier behavior |
| Health and alert derivation | WO-068 | Depends on accepted telemetry records |
| Frontend productization | WO-069 | Depends on stable live read/mutation contracts |
| Lifecycle closeout | WO-070 | Depends on credential, telemetry, health, alert, and UI surfaces |
| Hosted evidence | WO-071 | Serial closeout after all active product behavior exists |

If autonomous delivery is authorized, separate agents may perform read-only
review, test planning, or documentation preparation in parallel, but source
edits that affect migrations, API contracts, credential behavior, or active
frontend routes must be reconciled through one dependency-ready Work Order at
a time.

## 6. Required Validation

Each source-bearing Work Order must run focused local checks while iterating.
Before the first PR push for the ADP execution window, and again when the
package is close to final closeout, run the complete ES-009 command set:

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

Hosted validation belongs to WO-071 unless a prior Work Order explicitly
authorizes hosted evidence.

## 7. Stop-and-Ask Triggers

Stop and request Repository Maintainer direction before proceeding if any of
the following occurs:

- ADP-006, ES-009, or the dependency-ready Work Order is not accepted;
- autonomous delivery has not been explicitly authorized for the named Work
  Orders;
- implementation requires destructive legacy data removal;
- implementation requires provider writes, production secrets, hosted
  migration, deployment, release tagging, public launch, or production data use
  outside the active Work Order;
- any credential, token, owner subject, provider secret, or database URL would
  be exposed in chat, screenshots, source, logs, tests, or PR text;
- the work would reuse the external-product-client secret for agents;
- Atlas would call out to deploy, schedule, run, pause, resume, stop, or
  maintain an external agent runtime;
- a new infrastructure resource, orchestration framework, identity-provider
  change, or deployment topology is needed;
- deferred connector, Gmail, Drive, approval, policy, knowledge, artifact,
  webhook, queue, or runtime-control capability would be reactivated;
- required CI fails and the needed fix is outside the current Work Order.

## 8. Evidence and Reporting

Each completed Work Order must leave repository evidence:

- implementation or readiness report under `docs/reviews/`;
- Work Order and ADP status updates;
- local validation command results and CI status;
- migration evidence where relevant;
- hosted evidence where relevant;
- secret scans for touched source and docs where credentials are in scope;
- rollback notes and residual risks.

Current WO-071 hosted evidence is blocked because the production Render API
readiness endpoint reports `agent_credential_pepper_missing` and
`agent_credential_pepper_key_id_missing`. Owner enrollment and one-time agent
credential issuance fail closed without those values, so ADP-006 cannot close
until they are provisioned outside the repository and hosted verification is
rerun.

## 9. Completion Definition

ADP-006 is complete when:

- WO-064 through WO-071 are implemented, validated, reviewed, merged, and
  documented;
- active Atlas navigation and surfaces match ADR-008, ADR-009, DDR-003, and
  ES-009;
- owner enrollment, per-agent credentials, telemetry ingestion, derived health,
  alerts, activity, lifecycle actions, and live dashboard surfaces are
  complete;
- hosted verification proves the ES-009 success criteria with curl, Python,
  and TypeScript clients;
- no unresolved security, credential, migration, hosted evidence, CI, rollback,
  or architectural blocker remains;
- residual risks are accepted by the Repository Maintainer.
