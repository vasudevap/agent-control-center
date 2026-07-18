# Phase 7 ADR Assessment

**Status:** Proposed - Review Required
**Owner:** Repository Maintainer
**Date:** 2026-07-18
**Related Engineering Specification:** `docs/engineering-specifications/ES-007-operational-mvp-release-readiness.md`
**Related Phase:** Phase 7 - Operational MVP Release

---

## 1. Purpose

Assess whether Phase 7 Operational MVP Release Readiness requires a new
Architecture Decision Record before implementation Work Orders proceed.

This assessment does not grant implementation or release authority. It records
the proposed decision posture for maintainer review.

## 2. Decision Coverage

| Concern | Existing authority | Proposed assessment |
| --- | --- | --- |
| Hosting path | `docs/architecture/06-deployment-architecture.md`, `docs/implementation-plans/infrastructure-provisioning-strategy.md` | Covered if Phase 7 stays on the accepted Netlify plus Render path. |
| Database and migrations | `docs/architecture/08-data-architecture.md`, WO-018 evidence, infrastructure strategy | Covered if PostgreSQL remains the system of record and migration controls are documented per Work Order. |
| Secrets and OAuth credentials | `docs/architecture/07-security-architecture.md`, `docs/architecture/10-connector-framework.md`, ES-006 | Covered if token values remain behind the connector credential boundary and provider-native secret stores remain sufficient. |
| Gmail and Drive scope posture | ES-006, WO-036, Phase 6 ADR assessment | Covered if Phase 7 keeps `gmail.modify` and `drive.file` and does not request broader scopes. |
| Human approval and send continuation | ADR-002, ADR-003, ADR-004, ADR-005 | Covered if approvals remain exact, revalidated, and Atlas-authoritative. |
| Clinical and PHI suppression | ADR-005, security architecture, ES-006, WO-038 | Covered if suppression remains a hard fail-closed gate with no approval override. |
| Observability | `docs/architecture/11-observability.md`, WO-025 evidence | Covered for MVP if Phase 7 uses existing structured logs, audit, health checks, and lightweight owner alerts. |
| Single-owner operation | PRD, architecture baseline, ES-006 | Covered if Phase 7 remains one owner, one reviewer, and one governed external product client. |
| Framework adoption | AGENTS framework policy, technology strategy | Covered if Phase 7 does not introduce LangChain, LangGraph, Temporal, or a new workflow runtime. |

## 3. Proposed Conclusion

No new ADR appears required for Phase 7 planning if implementation remains
inside the accepted Netlify/Render, PostgreSQL, connector, approval, audit,
single-owner, and no-new-framework boundaries.

Phase 7 does require explicit maintainer acceptance of:

- production deployment authority;
- environment count and promotion path;
- rollback owner and rollback evidence;
- controlled-account execution boundary;
- residual risk for any unexecuted live provider evidence;
- MVP acceptance or release deferral.

These are release governance decisions unless they change architecture.

## 4. ADR Stop Triggers

Create a proposed ADR before implementation if any Phase 7 Work Order would:

- change the hosting provider, database provider, deployment topology, or
  environment model;
- introduce a new secrets manager, monitoring vendor, queue service, scheduler
  service, or orchestration framework;
- expand beyond single-owner operation;
- require public Google app verification posture or a broader user population;
- require OAuth scopes broader than `gmail.modify` or `drive.file`;
- allow personal mailbox data to become test fixtures or committed evidence;
- store full Gmail message bodies, OAuth token values, clinical content, PHI,
  or unrestricted attachment copies in Atlas;
- make Gmail, Drive, Netlify, Render, or an external webhook receiver
  authoritative for Atlas approvals, knowledge, audit, or run state;
- weaken clinical/PHI suppression or allow approval override;
- make deployment automation mutate production resources without explicit
  release authority and rollback evidence.

## 5. Review Question

The maintainer should confirm whether Phase 7 can proceed without a new ADR
under the constraints above, or identify the specific deployment, secrets,
monitoring, OAuth, or release decision that must be recorded as ADR-006 before
implementation Work Orders are accepted.
