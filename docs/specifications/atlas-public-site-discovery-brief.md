# Atlas Public Site Discovery Brief

**Status:** Approved for implementation
**Version:** 1.0
**Date:** 2026-07-15
**Owner:** Product Strategy
**Related Design:** [Atlas Public Site Experience](../design/12-public-site-experience.md)
**Related Decision:** [ADR-003 Public Site Application and Hosting Boundary](../decisions/ADR-003-public-site-application-boundary.md)

---

## 1. Purpose

This brief defines the audience, product story, claim boundaries, conversion
goals, and content priorities for the public Atlas website.

It exists to prevent the site from becoming either a generic AI landing page or
an unqualified list of future enterprise features. The public site must explain
why Atlas matters, demonstrate the quality of the product and architecture, and
represent the current implementation honestly.

## 2. Website Objective

The first public site must help a qualified visitor understand, within one
minute:

1. Atlas is an Agent Control Center, not an agent builder or chatbot.
2. Atlas keeps human operators in control of autonomous work.
3. Atlas unifies operational evidence across agents, runs, approvals,
   connectors, policies, and outputs.
4. Atlas is an actively developed product and enterprise architecture reference,
   with production runtime capabilities still planned.
5. The visitor can explore the product story, architecture, and current delivery
   status without being asked to create an account.

## 3. Audience Decision

### 3.1 Primary message audience

Hands-on professionals who build or operate AI agents and need stronger control
over fragmented operational systems.

Representative roles:

- AI architects;
- solution and enterprise architects;
- AI and platform engineers;
- engineering leaders;
- technical consultants;
- technically sophisticated independent professionals.

These visitors recognize the operational consequences of managing disconnected
agents, schedules, credentials, connectors, approvals, logs, and outputs.

### 3.2 Primary conversion audience at the current product stage

The current implementation is a frontend prototype and architecture portfolio,
not a generally available SaaS product. The people most able to act on the site
today are:

- architecture and engineering leaders assessing technical judgment;
- hiring managers evaluating enterprise and AI architecture capability;
- consulting prospects evaluating an approach to governed agent operations;
- practitioners and peers interested in the reference architecture;
- potential collaborators following the build.

The site should speak in product language to the operator while providing clear
evidence paths for these evaluators.

### 3.3 Credible future commercial audience

Small technical teams and consultancies operating multiple specialized agents
but not prepared to adopt a heavyweight hyperscaler or enterprise workflow
suite.

### 3.4 Long-term audience

- AI platform teams;
- enterprise architecture functions;
- business operations teams;
- regulated organizations;
- larger multi-environment agent fleets.

### 3.5 Explicit non-audiences

The first public site does not target:

- consumer productivity users;
- people seeking a general-purpose chatbot;
- citizen developers seeking a no-code workflow canvas;
- buyers expecting a production-ready multi-tenant SaaS offering;
- model-training or conventional MLOps teams.

## 4. Audience Problems

Qualified visitors are likely to experience some combination of the following:

- no reliable inventory of agents and their owners;
- schedules and triggers spread across unrelated tools;
- weak visibility into agent health, failures, and cost;
- inconsistent connector and credential controls;
- sensitive actions occurring without a consistent approval model;
- logs, outputs, and audit evidence stored in different systems;
- difficulty understanding what an agent did and why;
- framework-specific management that increases lock-in;
- no calm operational interface for deciding what requires attention.

## 5. Strategic Positioning

### 5.1 Category

**Primary category:** Enterprise Agent Control Center
**Technical category:** Agent Control Plane
**Broader frame:** Governed Agent Operations

### 5.2 Positioning statement

> Atlas is an enterprise-inspired control plane that helps operators understand,
> govern, and control autonomous work.

### 5.3 Homepage message hypothesis

**Eyebrow:** Enterprise Agent Control Center

**Headline:** Keep autonomous work under control.

**Supporting statement:** Atlas brings agents, runs, approvals, connectors, and
operational evidence into one governed workspace.

**Primary action:** Explore Atlas
**Secondary action:** View the architecture

This homepage message does not replace the approved brand tagline. It translates
the existing positioning into a visitor-oriented outcome.

## 6. Selling-Feature Hierarchy

The website must present benefits before feature inventory.

### 6.1 Human control over autonomous work

Operators can inspect, start, pause, stop, and authorize agent behavior within
explicit governance boundaries.

Relevant capabilities include lifecycle controls, manual and scheduled runs,
human approvals, policies, and risk-aware actions.

### 6.2 Trust through operational evidence

Atlas is designed so every material action leaves inspectable evidence through
run timelines, logs, events, outputs, artifacts, approval context, audit history,
and health information.

### 6.3 One operational workspace

Operators should not need to reconstruct agent state across disconnected tools.
Atlas brings agent inventory, fleet health, runs, schedules, approvals, alerts,
connector health, cost, and usage into one operating model.

### 6.4 Governed external access

Agent access to data and external systems must be constrained and observable
through connector contracts, least-privilege permissions, credential separation,
tool allowlists, policy enforcement, and audit events.

### 6.5 Framework-independent architecture

Atlas is designed around platform contracts rather than one agent framework.
The site must describe this as an architectural intent until multiple production
runtime integrations prove it.

## 7. Differentiation

The phrase "unified control plane" is now common across enterprise competitors.
Atlas should not attempt to differentiate through category language alone.

The strongest combined differentiation is:

- control before automation;
- exact human authority for sensitive actions;
- trust through inspectable evidence;
- calm, operator-focused product design;
- explicit separation of control and execution planes;
- architecture and decisions published as part of the product story;
- an initial operating model that remains usable by one professional while
  preserving a path to team and enterprise scale.

## 8. Competitive Message Observations

The market validates the category but concentrates on large-enterprise buyers:

- Microsoft Agent 365 emphasizes IT and security administration, inventory,
  lifecycle policy, data protection, and threat defense.
- ServiceNow AI Control Tower addresses Chief AI Officers, CIOs, CTOs, and risk
  and security leaders through enterprise asset governance.
- IBM watsonx Orchestrate presents a broad enterprise control plane spanning
  agent evaluation, optimization, policy, identity, and orchestration.
- UiPath Maestro leads with end-to-end process orchestration across agents,
  robots, and people.

Atlas should occupy a narrower and more credible initial territory: governed
agent operations for hands-on technical operators, demonstrated through an
openly explained architecture and high-quality product prototype.

## 9. Claim and Evidence Model

Every substantial product claim on the website must be classified as Built,
Designed, or Planned.

### 9.1 Built

The public site may present these as current, while retaining prototype context:

- responsive Atlas application shell;
- Overview operational dashboard prototype;
- Agents Inventory and Agent Details prototypes;
- simulated agent operational controls;
- Human Approvals queue, detail, and history prototype;
- approved brand, product design, and frontend test foundations.

### 9.2 Designed

The public site may present these as documented architecture, not implemented
runtime behavior:

- control-plane and execution-plane separation;
- agent registry and runtime contracts;
- connector framework;
- security and data architecture;
- observability architecture;
- human-approval integrity model;
- PostgreSQL system-of-record strategy;
- deployment topology.

### 9.3 Planned

The public site must label these as roadmap capabilities:

- production backend API;
- authentication and authorization;
- database and migrations;
- scheduler, queue, and workers;
- real policy and approval services;
- production connectors and credential handling;
- Gmail Triage Agent;
- cost and usage monitoring;
- additional agents and team capabilities.

### 9.4 Prohibited claims

The site must not imply that Atlas currently executes production agents,
authorizes real external actions, persists immutable audit records, protects
enterprise credentials, provides multi-tenant SaaS, supports enterprise
customers in production, or has measured customer outcomes.

## 10. Conversion Strategy

The first site is an evidence and exploration surface, not a sales funnel.

Primary visitor actions:

1. Explore the product experience.
2. Inspect the architecture and governance model.
3. Understand what is built and what is planned.
4. Follow the project as it develops.

The first release should not include pricing, account creation, trial language,
customer logos, fictional testimonials, newsletter capture, or a sales-contact
form.

## 11. Content Proof Inventory

The site should draw proof from canonical repository artifacts: brand and design
principles, product requirements, architecture documentation, accepted ADRs,
implemented product screens, work orders, review evidence, roadmap, and current
implementation status.

## 12. Success Measures

The first release is successful when:

- a visitor can identify Atlas's category and purpose from the first viewport;
- the primary audience recognizes the operational problem without needing AI
  market education;
- Built, Designed, and Planned states are visually and verbally distinct;
- every major statement has a repository-backed source;
- the page provides clear paths to product, architecture, and roadmap content;
- the experience meets WCAG 2.2 AA expectations;
- the page remains usable from 320 CSS pixels through large desktop widths;
- performance and metadata are suitable for a public portfolio surface.

## 13. Decisions Resolved by This Brief

- The site is product-led, not a personal portfolio homepage.
- Professional credibility is demonstrated through product and architecture
  evidence rather than a hero-level hiring message.
- Technical operators are the primary message audience.
- The current conversion goal is exploration and evaluation, not signup.
- The Gmail agent is a reference implementation, not the product category.
- Current implementation status must remain visible.
