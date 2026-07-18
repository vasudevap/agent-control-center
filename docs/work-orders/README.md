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

Work Orders 027 through 035 are proposed as the Phase 5 Agent Framework and
Governance Contracts package. They are not implementation-authorized until
ES-005 and the individual Work Orders are accepted:

- WO-027: Agent Registry and Runtime Contracts
- WO-028: Run Lifecycle and Job Intake Contracts
- WO-029: Governed Knowledge Fact Contracts
- WO-030: Knowledge Question and Answer Lifecycle
- WO-031: Approval Decision and Manual-Handling Contracts
- WO-032: Facts-Used Evidence and Revalidation Contracts
- WO-033: Webhook and Audit Event Contract Expansion
- WO-034: Phase 5 Dashboard Contract Compatibility Pass
- WO-035: Phase 5 Contract Integration Verification and Closeout

The proposed Phase 5 sequence is drafted in
[`docs/implementation-plans/phase-5-work-order-backlog.md`](../implementation-plans/phase-5-work-order-backlog.md).
