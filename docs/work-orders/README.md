# Work Orders

This directory contains migrated Atlas implementation work orders. They record authorized scope and completion status; they do not override accepted architecture or design decisions.

Work Order 005 is the approved application-shell baseline now implemented in `apps/web`.

Work Order 006 implemented the approved Agents Inventory and is `Completed`.

Work Order 007 has the Agent Details design direction locked for this milestone.

Work Order 008 authorizes the frontend prototype for governed agent operational
controls. Runtime mutation integration remains pending a dedicated engineering
specification and implementation work order.

Work Order 009 authorizes the frontend-only Human Approvals experience. Its
selected design direction is integrated on `main`; functional conformance,
implementation evidence, and formal closure are complete.

Work Order 010 completed and merged the frontend-only Runs, Run Detail,
Artifacts, and Artifact Detail prototype surfaces.

Work Order 011 completed and merged the frontend-only Alerts and Audit prototype
surfaces.

Work Order 012 authorizes the frontend-only Connectors, Policies, and Settings
prototype surfaces and is completed.

Work Order 013 records the post-delivery indicator-consistency maintenance
review across Atlas operational inventories and is completed.

Work Order 014 authorizes the final responsive-header, simulation-language,
title-metadata, and mobile-action-flow consistency corrections and is
completed.

Work Order 015 implements the Phase 3 backend Platform Foundation scope under
accepted ES-004 and is completed.

Work Order 016 documents the Phase 3 infrastructure provisioning and
environment strategy before additional backend implementation or live resource
provisioning begins and is completed.

Work Order 017 hardens backend runtime settings, dependency installation, local
backend commands, and CI alignment and is completed.

Work Order 018 replaces SQLite-only migration smoke validation with the
accepted local and CI PostgreSQL 18 path and is completed.

Work Order 019 establishes a provider-neutral, owner-only backend session
foundation and is completed.

Work Orders 020 through 026 completed the remaining Phase 3 implementation
sequence: authorization/external identity, API contracts, webhook hardening,
PostgreSQL queue, interval scheduler, observability/audit, and integration
closeout.

The Phase 3 work-order sequence is recorded in
[`docs/implementation-plans/phase-3-work-order-backlog.md`](../implementation-plans/phase-3-work-order-backlog.md).
The backlog is retained as closeout evidence.

Work Orders 027 through 035 completed and merged the Phase 5 Agent Framework
and Governance Contracts package:

- WO-027: Agent Registry and Runtime Contracts
- WO-028: Run Lifecycle and Job Intake Contracts
- WO-029: Governed Knowledge Fact Contracts
- WO-030: Knowledge Question and Answer Lifecycle
- WO-031: Approval Decision and Manual-Handling Contracts
- WO-032: Facts-Used Evidence and Revalidation Contracts
- WO-033: Webhook and Audit Event Contract Expansion
- WO-034: Phase 5 Dashboard Contract Compatibility Pass
- WO-035: Phase 5 Contract Integration Verification and Closeout

The Phase 5 sequence is recorded in
[`docs/implementation-plans/phase-5-work-order-backlog.md`](../implementation-plans/phase-5-work-order-backlog.md).

Work Orders 036 through 044 completed and merged as the Phase 6 Gmail Agent MVP
Candidate package under ES-006 and ADP-003:

- WO-036: Gmail OAuth, Scopes, and Connector Boundary
- WO-037: Gmail Message Eligibility, Retrieval, and Classification
- WO-038: Clinical and PHI Suppression Guardrail
- WO-039: Low-Risk Mailbox Actions and Attachment Saving
- WO-040: Ask-Instead-of-Guess and Governed Fact Use
- WO-041: Draft Generation and Facts-Used Evidence
- WO-042: Approval Gates, Edit-Then-Approve, and Send Continuation
- WO-043: Gmail Agent Operational Reconciliation
- WO-044: Controlled-Account Verification and MVP Candidate Closeout

The Phase 6 sequence is recorded in
[`docs/implementation-plans/phase-6-work-order-backlog.md`](../implementation-plans/phase-6-work-order-backlog.md).

Work Orders 045 through 052 are accepted for the Phase 7 Operational MVP
Release Readiness package under ES-007 and ADP-004:

- WO-045: Controlled-Account Release Verification
- WO-046: Dashboard Productization and Runtime Operations
- WO-047: Environment Configuration and Secrets Readiness
- WO-048: Deployment Path and Migration Readiness
- WO-049: Monitoring, Health, and Recovery Readiness
- WO-050: Release Runbooks and Rollback
- WO-051: MVP Release Candidate Validation
- WO-052: MVP Acceptance and Phase 7 Closeout

The Phase 7 sequence is recorded in
[`docs/implementation-plans/phase-7-work-order-backlog.md`](../implementation-plans/phase-7-work-order-backlog.md).
It granted bounded release-readiness implementation authority. Controlled
Gmail/Drive evidence and MVP release-candidate acceptance are recorded under
WO-045 and WO-052. Production deployment, release tagging, public launch, and
post-MVP implementation remain gated by separate explicit authority.

Work Orders 053 through 060, including WO-056A, are accepted for the hosted MVP
production cutover package under ES-008 and ADP-005:

- WO-053: Production Environment and Secrets Provisioning
- WO-054: Netlify Frontend Deployment
- WO-055: Render API and PostgreSQL Deployment
- WO-056A: Grafley Custom Domain Cutover
- WO-056: Google OAuth Production Client and Redirects
- WO-057: Hosted Migration, Backup, and Restore Readiness
- WO-058: Hosted Smoke Tests and Monitoring Confirmation
- WO-059: Production Rollback and Release Withdrawal Rehearsal
- WO-060: Release Tag and Production Closeout

Work Order 062 was accepted and completed as the remediation scope for the
original WO-058 hosted dashboard integration blocker:

- WO-062: Hosted Dashboard Runtime Integration

Work Order 063 was accepted and completed as the remediation scope for the
remaining WO-058 runtime smoke seed and synthetic connector enablement blocker:

- WO-063: Hosted Runtime Smoke Seed and Synthetic Connector Enablement

The hosted cutover sequence is recorded in
[`docs/implementation-plans/hosted-production-cutover-work-order-backlog.md`](../implementation-plans/hosted-production-cutover-work-order-backlog.md).
WO-053 provider configuration is now complete for the current hosted MVP
cutover scope, including the separate owner-OIDC provider values and immutable
owner identity subject, without recording secret or subject values.
WO-054 has created and linked the Netlify target, and the corrected Netlify
publish path now deploys the hosted dashboard successfully. Browser runtime
health reached the hosted Render API and reported `Runtime not ready (4)` in
the pre-WO-061 deployment evidence, which was the expected fail-closed backend
readiness state at that time. WO-055 has created the Render API service and
PostgreSQL target, and has bound the database URL plus current signing values
through provider-native Render UI. After WO-061 owner-subject binding, API
readiness now returns `ready` with no configuration problems; hosted migrations
remain governed by WO-057. The
Repository Maintainer confirmed `grafleyinc@gmail.com` as the single-owner
Google account after `atlas-owner@grafley.com` was found not to be a Google
account, accepted
`https://atlas.grafley.com` and `https://api.atlas.grafley.com` as final
Grafley product URLs, and will provision CNAME records after Netlify and Render
provide exact target values under WO-056A. Netlify and Render custom-domain
bindings now exist; both Grafley CNAME records have been provisioned, provider
TLS is active, runtime variables are cut over to
`https://atlas.grafley.com` and `https://api.atlas.grafley.com`, and
final-origin API CORS evidence passed. WO-057 now has source guardrails, a
hosted migration/backup/restore procedure, local migration validation, hosted
migration evidence, and final current-head verification. Release tags and
public launch remain bounded by the active Work Order scope and stop-and-ask
triggers.

WO-058 was originally blocked because the hosted dashboard operational surfaces
used session-only fictional fixtures for connector, run, approval, audit,
alert, log, and monitoring views. WO-062 replaced the release-critical hosted
paths with owner-authenticated, server-signed runtime integrations. A later
2026-07-22 WO-058 rerun confirmed that Connectors, Runs, Approvals, Audit, and
Alerts rendered live runtime states, but still lacked connected Gmail/Drive
evidence, a synthetic manual run, and a synthetic approval state. WO-063 added
the owner-authenticated synthetic smoke seed and the final 2026-07-22 WO-058
rerun passed with synthetic connector, run, approval, metadata-only audit, and
monitoring evidence. WO-059 is now the next dependency-ready Work Order.
WO-060 must not begin until WO-059 completes and the Repository Maintainer
records the required go/no-go / release-tag authority decision.

WO-056 Google OAuth preflight found no implemented browser-facing callback at
the earlier placeholder `/api/auth/google/callback` path. ADR-006 is accepted
and uses `https://atlas.grafley.com/oauth/google/callback` as the
browser-facing Google OAuth redirect URI, with server-side dashboard callback
handling and API-owned provider token exchange. The source callback route and
signed API completion endpoint are implemented; Google provider values must not
be entered until the callback route is deployed and verified. Google OAuth
provider configuration was completed for `grafleyinc@gmail.com` in Google Cloud
project `atlas-agent-control-center`; Render now has the Google OAuth client
ID, client secret, and redirect URI configured without value exposure.

WO-061 is completed for Google OIDC owner identity enrollment. The governed
source slice was merged through PR #96, deployed to Render, completed one
controlled authorization with `grafleyinc@gmail.com`, manually bound the
derived opaque owner subject in Render without value exposure, and verified
`https://api.atlas.grafley.com/health/ready` returns `ready` with
`problems: []`. Migrations, release tags, and public launch remain gated by
later Work Orders.
