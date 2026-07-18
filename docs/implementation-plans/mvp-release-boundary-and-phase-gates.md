# MVP Release Boundary and Phase Gates

**Status:** Proposed - Governance Review Required
**Owner:** Repository Maintainer
**Created:** 2026-07-18
**Purpose:** Define the crisp MVP boundary, phase gates, success criteria, exit
criteria, deployment path, associated Work Orders, required governing
artifacts, autonomous execution structure, and current completion percentages.

---

## 1. MVP Boundary

The project is not at MVP today. It is at a completed Phase 3 platform
foundation.

The crisp MVP boundary is:

| Boundary | Definition |
| --- | --- |
| Pre-MVP foundation | Phases 1-5 establish architecture, repository governance, platform foundation, dashboard surface, and generic agent/governance contracts. |
| MVP candidate | Phase 6 demonstrates the first end-to-end Gmail Agent workflow with controlled data, fake-or-limited production effects, and all required safety controls. |
| MVP release | Phase 7 makes the Gmail Agent usable for normal single-owner personal operation on the approved Netlify/Render deployment path. |
| Beyond MVP | Phases 8-11 expand capability, durability, orchestration, additional agents, and enterprise readiness after the MVP is operable. |

MVP means one real operator can use Atlas to run the first Gmail Agent workflow
end to end, with authentication, scheduling, approvals, auditability, logs,
safe low-risk action execution, high-risk approval gates, and deployment to the
approved hosting path.

## 2. Phase Gate Table

Completion percentages represent progress against each phase's exit criteria,
not lines of code or effort spent.

| Phase | Stage | MVP boundary | Current % | Associated Work Orders | Governing Artifacts | Deployment posture | Entry gate | Success criteria | Exit criteria |
| ---: | --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| 1 | Architecture Foundation | Pre-MVP | 100% | Architecture docs, ADR baseline, PRD; no numbered WOs required | PRD; architecture baseline; ADR-001 through ADR-005; roadmap; technology strategy; design principles | Documentation only | Project purpose and architecture scope agreed | System context, container, component, security, data, runtime, connector, observability, and technology architecture exist | Architecture baseline accepted and usable for governed execution |
| 2 | Repository Foundation | Pre-MVP | 100% | ES-000 through ES-003; frontend WOs 001-014 partially cover repository/dashboard groundwork | ES-000 through ES-003; governance controls; definition of ready/done; pull-request and review standards; WO-001 through WO-014; relevant design decision records | Local repo and CI | Canonical repo, governance, and frontend foundation path defined | Repository standards, CI, review process, frontend test infrastructure, and initial dashboard design assets exist | Governed branch/PR/CI workflow is usable and source of truth is in Git |
| 3 | Platform Foundation | Pre-MVP | 100% | WO-015 through WO-026 | ES-004; Phase 3 master plan, target architecture, backlog, and decision register; ADP-001; WO-015 through WO-026; WO-026 closeout report | Local and CI backend foundation; no live production operation | Phase 3 engineering spec and accepted WOs | FastAPI foundation, PostgreSQL migrations, auth/session scaffolding, authorization boundary, API contracts, queue, scheduler, webhook fake delivery, logging, audit, and closeout smoke test pass | WO-026 merged, CI green, Phase 3 closeout report complete |
| 4 | Dashboard Productization | Pre-MVP, MVP-enabling | 60% | Existing: WO-001, WO-005, WO-006, WO-009 through WO-014 completed; remaining dashboard/backend-integration WOs TBD | Existing dashboard WOs and implementation reports; likely dashboard productization ES; API-integration and fixture-removal WOs; UI acceptance/review reports; design decision records if the approved experience changes | Netlify preview before production | Phase 3 backend foundation complete | Dashboard routes are integrated with real API contracts, auth/session state, errors, loading states, empty states, and operator flows | Operator can manage agents, runs, approvals, audit/log views, connector settings, and health from the dashboard without fixture-only behavior |
| 5 | Agent Framework and Governance Contracts | Pre-MVP, MVP-enabling | 5% | Proposed WO-027 through WO-035 | Proposed ES-005; Phase 5 ADR assessment; Phase 5 WO backlog; proposed ADP-002; proposed WO-027 through WO-035; future implementation reports and closeout report | Render development/staging API with synthetic data only | Phase 3 complete, ES-005 accepted, ADR assessment accepted, and Phase 5 WOs accepted | Generic agent registry/runtime contracts, external approval decision API, manual-handling contract, governed knowledge CRUD, confirmations, volatility, questions/answers, webhooks, `facts_used`, audit, and revalidation contracts exist | Generic contracts are implemented, tested, documented, and merged without Gmail-specific behavior |
| 6 | Gmail Agent MVP Candidate | MVP candidate | 0% | TBD, after Phase 5 | Likely ES-006; Gmail Agent functional specification and WO backlog; Gmail OAuth/security or connector-scope ADR if required; Gmail WOs; privacy/safety review; controlled-data demo and acceptance report | Controlled Gmail test account or limited private beta | Phase 5 contracts complete; Gmail/OAuth scope accepted | Gmail OAuth, eligible-message selection, classification, ask-instead-of-guess, draft/evidence generation, approvals, safe low-risk actions, high-risk approval gates, logs, and audit work end to end | First Gmail Agent workflow can run safely with controlled data and no unresolved safety blocker |
| 7 | Operational MVP Release | MVP release | 0% | TBD | Likely release-management plan; deployment/provisioning WOs; environment configuration; operational-readiness and security/privacy reviews; monitoring and rollback runbooks; MVP acceptance and residual-risk record | Netlify + Render MVP production deployment | Phase 6 candidate passes safety and usability review | Normal single-owner use is reliable enough: deployment, health/readiness, scheduling, retries, recovery path, monitoring, documented operations, and rollback are in place | MVP is operable for personal use, with CI green, deployment verified, no credential exposure, and accepted residual risk |
| 8 | Advanced Agentic Workflows | Beyond MVP | 0% | TBD | Likely advanced-workflow ES and ADRs; framework evaluation; one or more WOs per workflow; safety and post-MVP risk reviews; implementation and acceptance reports | Incremental post-MVP environments | MVP released and stable | Additional workflow patterns, richer planning/tooling, and optional framework experiments are evaluated against architecture criteria | Advanced workflows add value without weakening MVP safety, audit, or maintainability |
| 9 | Durable Orchestration | Beyond MVP | 0% | TBD | Likely orchestration ADR; durable-workflow ES; Temporal-or-equivalent evaluation; migration and rollback plan; orchestration WOs; durability and recovery evidence | Post-MVP staging before production | Durable workflow needs exceed simple queue/scheduler | Temporal or equivalent orchestration is justified, ADR-approved, implemented, and tested | Long-running/recoverable workflows are durable without unnecessary complexity |
| 10 | Additional Agents | Beyond MVP | 0% | TBD | Likely per-agent PRD addenda or functional specifications; connector-scope ADRs where needed; WOs per agent; policy/safety reviews; rollout, acceptance, and closeout reports | Agent-by-agent rollout | Gmail MVP proves reusable platform contracts | Calendar, documents, shopping, travel, job search, or other agents reuse platform contracts | Each new agent ships behind accepted WOs, safety controls, and operational evidence |
| 11 | Enterprise Features | Beyond MVP | 0% | TBD | Likely enterprise PRD and ES; ADRs for SSO, RBAC, multi-user operation, tenancy, secrets, and networking; governance/security reviews; phased enterprise WOs; support-readiness evidence | Enterprise-ready environments only after separate authority | Multi-user/enterprise requirements are accepted | RBAC, SSO, multi-user governance, stronger secrets, private networking, tenant boundaries, and enterprise audit requirements are designed | Enterprise capabilities meet accepted security, governance, deployment, and support criteria |

## 3. Autonomous Execution Artifact Model

The phase gate table should remain the release-control view. It should not try
to carry every work-order dependency directly, because that makes the table
wide, brittle, and hard for multiple agents to execute from.

Use the following artifact model for autonomous delivery:

| Artifact type | Role in execution | Automation rule |
| --- | --- | --- |
| PRD or PRD addendum | Defines the product outcome, user value, and MVP or post-MVP boundary | Required before a new product capability phase begins |
| Architecture baseline | Defines the accepted system, container, component, data, security, runtime, connector, observability, and deployment boundaries | Required before ES drafting when architecture already exists; update only through accepted governance |
| ADR | Records a significant architecture, security, data, framework, runtime, deployment, or integration decision | ADRs decide; they do not collect or own WOs. A WO may depend on one or more accepted ADRs |
| ES | Converts accepted product and architecture authority into an engineering scope, exclusions, interfaces, validation, and rollback expectations | Required before implementation WOs for a major capability |
| ADP | Sequences accepted WOs into an autonomous execution program, including dependency gates, parallel lanes, validation, PR/CI rules, and stop-and-ask triggers | Required before uninterrupted multi-WO execution |
| WO | Authorizes one bounded implementation change with file scope, prerequisites, acceptance criteria, validation, rollback, and stop-and-ask triggers | The smallest unit an implementation agent should execute |
| Review or acceptance record | Records readiness, implementation evidence, validation, risks, and closure | Required to close ES, WO, ADP, MVP candidate, and release phases |
| Runbook or release plan | Defines deployment, health checks, rollback, operations, monitoring, credential handling, and incident/recovery steps | Required before MVP production release and any live integration |
| Risk, privacy, or security review | Records accepted residual risk and safety/privacy findings | Required when live credentials, external provider data, user data, or production effects enter scope |

The ADP is the correct place to group WOs for autonomous execution. Dependent
WOs belong in serialized ADP waves. Independent WOs belong in parallel ADP
lanes. ADRs remain decision gates that WOs cite as prerequisites.

## 4. Required Artifact Register by Phase

This table is a best-effort artifact register based on the current state of the
repository. Future phases may add, split, or retire artifacts when their
specific scope is drafted.

| Phase | Stage | Required governing artifacts | Decision gates | Execution package | Parallelization posture |
| ---: | --- | --- | --- | --- | --- |
| 1 | Architecture Foundation | PRD; architecture baseline; ADR-001 through ADR-005; architecture README; roadmap; technology strategy; design principles | Accepted architecture and ADR baseline | No ADP required; documentation foundation is complete | Complete; no active parallel implementation |
| 2 | Repository Foundation | ES-000 through ES-003; governance README; Definition of Ready; Definition of Done; PR/review process; branching and release management; WO-001 through WO-014; design decision records; implementation reports | ADR-001 for frontend testing; ADR-002 for approval decision integrity | Individual frontend/governance WOs | Complete; no active parallel implementation |
| 3 | Platform Foundation | ES-004; Phase 3 master plan; target architecture; decision register; phase backlog; ADP-001; WO-015 through WO-026; implementation reports; Phase 3 closeout | ADR-003, ADR-004, ADR-005 accepted before backend platform work | ADP-001 completed Phase 3 dependency sequence | Complete; Phase 3 was mostly serial with limited dependency-ready parallelism |
| 4 | Dashboard Productization | Dashboard productization ES or ES addendum; dashboard API-integration WOs; fixture-removal plan; UI acceptance records; accessibility/responsive evidence; implementation reports; closeout | ADR only if operator experience, auth, data, or decision semantics change | Future dashboard ADP or ADP lane after API contracts freeze | Can run partly in parallel with Phase 5 after API contracts and auth/session interface are stable |
| 5 | Agent Framework and Governance Contracts | Proposed ES-005; Phase 5 ADR assessment; proposed Phase 5 WO backlog; proposed WO-027 through WO-035; proposed ADP-002; future contract tests, implementation reports, and closeout report | Existing ADR-002 through ADR-005 appear sufficient unless Phase 5 crosses a documented ADR trigger | ADP-002 groups proposed WOs into dependency waves and becomes executable only after acceptance | High parallel potential after ES-005 and required WOs are accepted; agent runtime, knowledge, approval, events, dashboard compatibility, and tests can occupy separate lanes |
| 6 | Gmail Agent MVP Candidate | ES-006; Gmail functional specification; Gmail connector/security scope; OAuth/scope decision record or ADR if needed; Gmail WO backlog; Gmail safety/privacy review; controlled-data demo plan; acceptance report | Gmail OAuth scopes, provider data handling, production-effect limits, and clinical/PHI suppression policy accepted | Gmail MVP ADP after Phase 5 contracts are merged and Gmail WOs accepted | Moderate parallel potential: connector/auth, classifier/drafting, UI integration, and safety tests can split after Gmail contract boundaries are fixed |
| 7 | Operational MVP Release | Release-management plan; deployment WOs; environment configuration record; secrets/credential handling checklist; operational readiness review; monitoring plan; runbooks; rollback plan; MVP acceptance and residual-risk record | Production deployment authority, environment count, rollback owner, monitoring threshold, and residual risk accepted | MVP release ADP only after Phase 6 candidate passes review | Mostly serial near release; documentation, monitoring, and dashboard polish can run in parallel before final cutover |
| 8 | Advanced Agentic Workflows | PRD addendum; advanced-workflow ES; framework evaluation; ADR if LangChain, LangGraph, Temporal, or equivalent becomes justified; workflow WOs; safety review; acceptance records | Framework adoption and workflow-risk decisions accepted | Post-MVP ADP per workflow family | Parallel by workflow family if shared contracts are stable |
| 9 | Durable Orchestration | Orchestration ADR; durable-workflow ES; migration plan; rollback plan; queue/scheduler compatibility review; durability tests; orchestration WOs; recovery evidence | Durable orchestration need and chosen runtime accepted | Orchestration ADP with migration gates | Mostly serial for architecture and migration; tests and documentation can parallelize after interface freeze |
| 10 | Additional Agents | Per-agent PRD addendum or functional spec; connector-scope ADR assessment; per-agent ES; per-agent WOs; safety/privacy reviews; rollout and closeout reports | Connector permissions, data handling, and action-risk boundaries accepted per agent | Agent-family ADPs after reusable platform contracts prove stable | High parallel potential across independent agents once shared framework and policy contracts are stable |
| 11 | Enterprise Features | Enterprise PRD; enterprise ES; ADRs for SSO, RBAC, multi-user operation, tenancy, secrets, networking, and support model; security/governance reviews; enterprise WOs; support readiness evidence | Enterprise identity, tenancy, authorization, support, and deployment boundaries accepted | Enterprise readiness ADP split by capability domain | Parallel only after enterprise architecture boundaries are accepted; identity/tenancy/security remain serial gates |

## 5. Autonomous Delivery Wave Plan

ADPs should schedule WOs by dependency wave, not by document type. Each WO in a
future ADP should declare `depends_on`, `blocked_by`, `parallel_safe_with`,
file/domain boundaries, validation commands, evidence requirements, and
stop-and-ask triggers.

| Wave | Phase focus | Dependency gate | Parallel lanes | Serial follow-up | Autonomy boundary |
| --- | --- | --- | --- | --- | --- |
| Wave 0 | Phase 5 planning | ES-005 accepted; ADR assessment complete; no unresolved architecture decision | Artifact drafting can split into ES review fixes, WO backlog drafting, and test strategy drafting | Accept ES-005, WO-027 through WO-035, and ADP-002 before code | Agent may draft and revise docs; must stop before implementing unaccepted WOs |
| Wave 1 | Generic contracts | Accepted Phase 5 WOs and ADP-002 | WO-027 agent runtime/registry; WO-029 governed knowledge facts; WO-031 approval/manual-handling | WO-028 run lifecycle, WO-030 knowledge Q&A, WO-033 events, WO-034 dashboard compatibility, WO-032 facts-used, and WO-035 closeout follow by dependency | No Gmail-specific behavior; no live provider calls |
| Wave 2 | Dashboard integration | Stable backend API/auth/session contracts from Phase 5 | Real API integration; loading/error/empty states; dashboard audit/approval views; fixture-removal evidence | Operator acceptance and dashboard productization closeout | No production deployment authority unless Phase 7 release plan grants it |
| Wave 3 | Gmail MVP candidate | Phase 5 contracts merged; ES-006 and Gmail WOs accepted; Gmail credentials boundary approved | Gmail connector/OAuth scaffold; message eligibility/classification; draft/evidence generation; safety/privacy tests; UI workflow integration | Controlled-data end-to-end demo and safety acceptance | Must stop before live credentials or real account effects unless explicitly authorized |
| Wave 4 | Operational MVP release | Phase 6 candidate accepted; release plan and runbooks accepted | Monitoring, rollback docs, deployment verification, final dashboard polish, residual-risk review | Production cutover and MVP acceptance | Live production deployment requires explicit release authority |
| Wave 5 | Post-MVP expansion | MVP accepted and stable | Independent agents, workflow families, documentation, and tests | Shared platform migrations, durable orchestration, or enterprise identity gates | Do not add frameworks, multi-user behavior, or enterprise controls without ADR/ES authority |

## 6. Issues, Unknowns, and TBD Decisions

The artifact set above is a best-effort planning view. The following items may
change the phase sequence, scope, or governing artifacts when they are decided:

- whether Phase 4 must finish before Phase 5, or can complete in parallel with
  Phase 5 under a separately accepted integration scope;
- whether the proposed WO-027 through WO-035 breakdown is accepted as-is or
  split further before implementation;
- whether ES-005 and ES-006 should remain separate specifications, with an ADP
  coordinating them only after their WOs are accepted;
- whether Phase 5 introduces a significant new security, data, or contract
  decision that requires a new ADR rather than an update to an existing ADR;
- the MVP definition of acceptable Gmail risk, test coverage, data handling,
  and production-effect limits;
- Gmail OAuth scopes, test-account versus personal-account use, and the
  authorization needed to use live credentials;
- whether Google Drive is an MVP dependency or should be deferred;
- the exact clinical/protected-health-information suppression policy and its
  validation thresholds;
- the minimum MVP observability stack beyond Render logs and health checks;
- whether plain Python/direct SDK contracts remain sufficient or a workflow
  framework becomes justified under the framework-adoption policy;
- production environment count, deployment approvals, rollback ownership, and
  the exact point at which a human release decision is required;
- the maximum number of parallel implementation agents that should be active on
  the same branch family without increasing review and merge risk;
- the exact WO dependency fields and naming convention to preserve during
  ADP-002 execution;
- measurable acceptance criteria for normal single-owner use; and
- the intentionally speculative Phase 8-11 artifacts, which must be revised
  when those phases are entered.

## 7. MVP Success Criteria

MVP succeeds when:

- at least one production Gmail Agent is operable for the single owner;
- the dashboard shows agents, status, runs, logs, outputs, approvals, health,
  and connector state using real backend contracts;
- manual Run Now and scheduled execution both work;
- low-risk Gmail actions execute safely and idempotently;
- high-risk actions require approval before execution;
- ask-instead-of-guess creates governed questions instead of unsafe drafts;
- knowledge facts used by drafts are traceable through `facts_used`;
- clinical/protected-health-information suppression prevents drafts, approvals,
  questions, and learned facts for suppressed content;
- audit records distinguish human, external client, and service actors;
- credentials and secrets are never exposed in logs, APIs, webhooks, or UI;
- Netlify and Render deployment is verified with documented rollback;
- architecture, ADRs, WOs, implementation reports, and status records remain
  synchronized.

## 8. MVP Exit Criteria

The project exits MVP and enters post-MVP expansion only after:

- Phase 7 is complete;
- the Gmail Agent has been used successfully in normal single-owner operation;
- known MVP defects are triaged with no unresolved safety, security, or data
  loss blockers;
- monitoring and manual recovery are sufficient for initial personal use;
- residual risks are accepted and documented;
- Phase 8+ scope is approved through new Engineering Specifications, ADRs, or
  Work Orders as required.

## 9. Immediate Next Governance Step

Create the Phase 5 execution package before implementation. The recommended
sequence is ES first, WOs second, ADP third:

| Order | Next artifact | Purpose | Autonomy effect |
| ---: | --- | --- | --- |
| 1 | Phase 5 Engineering Specification | Proposed as ES-005; defines generic agent/governance contracts, API surfaces, validation rules, audit, security, errors, idempotency, retention, and test requirements | Allows agents to draft WOs against stable scope after acceptance |
| 2 | Phase 5 ADR assessment | Proposed; records that existing ADR-002 through ADR-005 appear sufficient unless Phase 5 crosses an ADR trigger | Prevents implementation from making architecture decisions silently |
| 3 | Phase 5 Work Order Backlog | Proposed; breaks Phase 5 into WO-027 through WO-035 with explicit dependencies and parallel-safety guidance | Creates independently executable units after acceptance |
| 4 | ADP-002: Phase 5 Autonomous Delivery Program | Proposed and blocked pending acceptance; groups WOs into dependency waves and parallel lanes with validation, PR/CI, merge, evidence, and stop-and-ask rules | Authorizes uninterrupted execution only after ES-005, WOs, and ADP-002 are accepted |

Phase 5 must not silently become Gmail-specific implementation. Gmail-specific
execution belongs to Phase 6 after the generic contracts are ready.
