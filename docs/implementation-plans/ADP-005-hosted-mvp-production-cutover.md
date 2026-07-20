# ADP-005: Hosted MVP Production Cutover

**Status:** Accepted - In Progress
**Program ID:** ADP-005
**Type:** Autonomous Delivery Program
**Owner:** Repository Maintainer
**Created:** 2026-07-19
**Execution Window:** Authorized by Repository Maintainer on 2026-07-19
**Engineering Specification:** `docs/engineering-specifications/ES-008-hosted-mvp-production-cutover.md`
**Work Order Backlog:** `docs/implementation-plans/hosted-production-cutover-work-order-backlog.md`

---

## 1. Purpose

Sequence the proposed hosted MVP production cutover Work Orders into a governed
execution program after Phase 7 release-candidate acceptance.

ADP-005 does not replace individual Work Orders. Each Work Order remains the
technical scope authority for implementation, exclusions, validation,
rollback, and stop-and-ask triggers after acceptance.

## 2. Execution Authority

Execution authority was granted by the Repository Maintainer on 2026-07-19 for
the accepted ES-008, hosted production cutover ADR assessment, WO-053 through
WO-060, and ADP-005 package. On 2026-07-20, the Repository Maintainer accepted
the Grafley custom-domain direction, created `atlas-owner@grafley.com`, and
added WO-056A as the governed custom-domain cutover dependency before Google
OAuth is finalized.

Authority remains bounded by each Work Order. Provider writes, deployment,
migration, OAuth configuration, rollback action, release tag, and hosted
production use must still match the active Work Order scope and stop-and-ask
triggers.

## 3. Proposed Work Order Set

| Order | Work Order | Current State | ADP Execution Action | Completion Gate |
| ---: | --- | --- | --- | --- |
| 1 | `WO-053: Production Environment and Secrets Provisioning` | In Progress - Owner/OAuth Pending | Netlify/Render provider targets and Render database/signing values configured; owner identity and Google OAuth still pending | Provider-native env/secrets configured without value exposure or documented blocker |
| 2 | `WO-054: Netlify Frontend Deployment` | Completed - Hosted Runtime Evidence Captured | Netlify target, API URL, production deploy, browser runtime-health evidence, and rollback target recorded | Frontend hosted and rollback path verified |
| 3 | `WO-055: Render API and PostgreSQL Deployment` | Blocked - Owner/OAuth Binding and Migration Pending | API/database targets created; database URL and signing values bound; owner/OAuth values and hosted migration still pending | API/database hosted with health/readiness evidence |
| 4 | `WO-056A: Grafley Custom Domain Cutover` | Completed - Custom Domains and Runtime Cutover Verified | Netlify and Render custom-domain bindings are configured; both Grafley CNAMEs are provisioned; provider TLS is active; Netlify and Render runtime variables are cut over to the final domains | `https://atlas.grafley.com` and `https://api.atlas.grafley.com` are active |
| 5 | `WO-056: Google OAuth Production Client and Redirects` | Accepted - Pending Implementation - Callback Decision Accepted | Implement the ADR-006 dashboard callback route before Google provider values are entered; source preflight found no direct browser-facing callback at the earlier placeholder path | Hosted OAuth redirects work with accepted scopes |
| 6 | `WO-057: Hosted Migration, Backup, and Restore Readiness` | Accepted - Pending Implementation | Await hosted database readiness | Hosted DB migration and recovery evidence recorded |
| 7 | `WO-058: Hosted Smoke Tests and Monitoring Confirmation` | Accepted - Pending Implementation | Await WO-054 through WO-057 evidence, including WO-056A | Hosted smoke, audit/log, connector, and monitoring checks pass |
| 8 | `WO-059: Production Rollback and Release Withdrawal Rehearsal` | Accepted - Pending Implementation | Await hosted deployment evidence | Rollback and withdrawal paths reviewed or rehearsed |
| 9 | `WO-060: Release Tag and Production Closeout` | Accepted - Pending Implementation | Await final evidence and maintainer decision | Go/no-go decision, optional tag, URLs, and closeout recorded |

## 4. Dependency Sequence

```text
ES-008 accepted + WO-053 through WO-060 accepted + WO-056A accepted + ADP-005 accepted
  -> WO-053 provider env/secrets provisioning
    -> parallel-safe setup where authorized:
       WO-054 Netlify frontend
       WO-055 Render API/PostgreSQL
      -> WO-056A Grafley custom-domain cutover
      -> WO-056 Google OAuth redirects
      -> WO-057 hosted migration/backup/restore
        -> WO-058 hosted smoke/monitoring
        -> WO-059 rollback/withdrawal rehearsal
          -> WO-060 go/no-go, optional tag, closeout
```

## 5. Parallel Execution Notes

| Lane | Work Orders | Parallel-safe conditions |
| --- | --- | --- |
| Provider configuration | WO-053 | Serial gate before provider writes |
| Hosting setup | WO-054, WO-055 | May run in parallel only after env map and provider authority are explicit |
| Domain/OAuth/migration | WO-056A, WO-056, WO-057 | Serial because final URLs should precede OAuth and database state must be stable |
| Release evidence | WO-058, WO-059, WO-060 | Serial final evidence and maintainer decision |

Parallel agents must not modify provider configuration, migrations, OAuth
settings, release tags, or rollback records without rebasing and reconciling
before PR review.

## 6. Stop-and-Ask Triggers

Stop and request Repository Maintainer direction before proceeding if any of
the following occurs:

- ES-008, a required Work Order, or ADP-005 is not accepted;
- implementation requires provider writes, production secrets, deployment,
  production migration, release tagging, public launch, or production data use
  outside the accepted Work Order boundary;
- provider dashboards would expose secret values in chat, screenshots, source,
  logs, or PRs;
- Google requires broader scopes or external verification;
- custom-domain setup requires a different provider, registrar, paid plan, or
  DNS authority decision;
- deployment topology, provider choice, environment count, secrets ownership,
  database provider, or monitoring posture changes require ADR review;
- required CI fails and the needed fix is outside the current Work Order;
- rollback, restore, release withdrawal, or tag authority is ambiguous.

## 7. Evidence and Reporting

Each Work Order completed under ADP-005 must leave repository evidence:

- implementation or readiness report under `docs/reviews/`;
- current Work Order and ADP/backlog status;
- local validation command results and GitHub CI status;
- provider evidence with secret values redacted or omitted;
- deployment URL and health evidence where relevant;
- migration head, backup, restore, and rollback evidence where relevant;
- residual risks and maintainer decisions where relevant.

## 8. Completion Definition

ADP-005 is complete only when:

- WO-053 through WO-060, including WO-056A, are implemented, validated,
  reviewed, and merged;
- hosted frontend and API evidence are recorded;
- migration, backup, restore, OAuth, smoke, monitoring, and rollback evidence
  are recorded;
- no unresolved safety, security, credential, provider, deployment, rollback,
  release-tag, or CI blocker remains;
- residual risks are accepted by the Repository Maintainer;
- the final go/no-go and production closeout decision is recorded.
