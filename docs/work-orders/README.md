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
foundation and is accepted for dependency-gated implementation.

Work Orders 020 through 026 are accepted as the remaining Phase 3 implementation
sequence: authorization/external identity, API contracts, webhook hardening,
PostgreSQL queue, interval scheduler, observability/audit, and integration
closeout. They must still execute in dependency order under their individual
scope and stop-and-ask controls.

The remaining Phase 3 work-order sequence is drafted in
[`docs/implementation-plans/phase-3-work-order-backlog.md`](../implementation-plans/phase-3-work-order-backlog.md).
The backlog is planning guidance only. WO-019 through WO-026 may be reviewed
and accepted as one planning package, but each retains separate scope,
dependency gates, implementation authority, branch, validation evidence, and
merge requirements.
