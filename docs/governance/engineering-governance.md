# Engineering Governance

## Purpose and ownership

This document defines how Atlas converts approved intent into reviewed repository changes. The repository maintainer owns this handbook and approves amendments through the normal pull-request process. Contributors and implementation agents must follow it.

## Source-of-truth hierarchy

When instructions overlap, use this order:

1. Repository-wide policy in [`AGENTS.md`](../../AGENTS.md).
2. Accepted architecture and ADRs in `docs/architecture/` and `docs/decisions/`.
3. Approved product specifications in `docs/specifications/` and approved design/DDR records in `docs/design/`.
4. The approved Engineering Specification or Work Order authorizing the current change.
5. This governance handbook and repository procedures.
6. Tool-specific scoped guidance such as `.claude/CLAUDE.md`.
7. Recommendations and historical references, which are advisory only.

Git is the technical source of truth. Notion is an operational workspace and must not silently override repository authority.

## Work lifecycle

1. Proposed work identifies its objective, owner, scope, impacts, acceptance criteria, and governing references.
2. Significant engineering execution is refined into an Engineering Specification; bounded product implementation is authorized by a Work Order.
3. Architecture-changing decisions require a proposed ADR before implementation; design decisions require the appropriate DDR process.
4. The review owner confirms the [Definition of Ready](./definition-of-ready.md).
5. An implementation agent works only on a short-lived branch and stays within the approved artifact.
6. The pull request supplies validation and compliance evidence.
7. Required CI and review complete before the approved merge method is used.
8. The implementation/review report and release records close the lifecycle under the [Definition of Done](./definition-of-done.md).

## Authority and agent boundaries

Architecture documents and accepted ADRs govern system structure, technology, infrastructure, security boundaries, and deployment. Approved design documents and DDRs govern UX and visual behavior. Product specifications govern user and business requirements. Implementation agents may translate approved artifacts into code and documentation; they may not invent scope, approve their own architectural exceptions, bypass platform contracts, weaken controls, or start a later Work Order.

## Review responsibilities and evidence

The author or implementation agent supplies a focused diff, linked governing artifact, command results, relevant tests, architecture/design/security impact statements, documentation updates, risk and rollback notes, and visual/accessibility/responsive evidence for UI work. The reviewer verifies scope, authority alignment, acceptance criteria, risk treatment, decision records, and CI. In a solo project, the maintainer may perform the review, but the evidence remains required.

## Architecture-compliance review

Every significant pull request states whether architecture changes. If none, the reviewer confirms consistency with current architecture. If architecture changes, the pull request links the approved ADR and updated canonical architecture. An unexplained architecture change blocks merge.

## Exceptions

Exceptions must identify the rule, reason, risk, compensating control, owner, expiry or revisit trigger, and follow-up issue. Emergency fixes may use `hotfix/`, but cannot disable CI or erase evidence; any unavoidable procedural deviation receives a retrospective review. Accepted exceptions never silently redefine canonical policy.
