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
It grants bounded release-readiness implementation authority. Live credential
use, controlled-account execution, production deployment, and MVP release
remain gated by explicit Work Order or release decisions.
