# Hosted Production Cutover ADR Assessment

**Status:** Accepted - Custom Domain Note Added
**Owner:** Repository Maintainer
**Date:** 2026-07-19
**Related Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)

## Purpose

Assess whether the hosted MVP production cutover requires a new Architecture
Decision Record before implementation.

## Existing Decision Coverage

| Decision area | Existing authority | Assessment |
| --- | --- | --- |
| Hosting path | Deployment architecture and infrastructure provisioning strategy | Covered while the cutover stays on Netlify frontend plus Render API/PostgreSQL. |
| Custom product domains | ES-008 and ADP-005 hosted URL authority | Covered while `atlas.grafley.com` and `api.atlas.grafley.com` point to the accepted Netlify and Render targets without changing providers or topology. |
| System of record | Data architecture and PostgreSQL hardening evidence | Covered while PostgreSQL remains the runtime system of record. |
| Secrets ownership | Security architecture, WO-047, and provider-native provisioning strategy | Covered while secrets stay in Netlify/Render/Google provider stores and not source. |
| Gmail/Drive scopes | ES-006, WO-036, and Phase 6 ADR assessment | Covered while scopes remain `gmail.modify` and `drive.file`. |
| Single-owner operation | PRD, ES-006, ES-007, and WO-052 closeout | Covered while deployment remains single-owner only. |
| Release tags | Release management governance | Covered while tags are annotated, immutable, and created only with explicit authority. |
| Monitoring posture | Observability architecture and WO-049 | Covered for lightweight MVP monitoring and manual recovery. |

## Decision

No new ADR is required before ADP-005 if the cutover remains within the
accepted Netlify, Render, PostgreSQL, Google OAuth, single-owner, and
provider-native secrets boundaries. The accepted Grafley custom domains do not
require a new ADR while they remain CNAME front doors for the already accepted
Netlify and Render services.

## ADR Triggers

Create a proposed ADR before implementation if any ADP-005 Work Order would:

- change hosting provider, database provider, DNS authority, or deployment
  topology;
- introduce a new secrets manager or monitoring vendor;
- broaden Google OAuth scopes or add Google verification for multiple users;
- add multi-user, RBAC, tenancy, delegation, or enterprise controls;
- introduce LangChain, LangGraph, Temporal, or another workflow runtime;
- change release-tag immutability or rollback policy;
- require persistent production data beyond the accepted PostgreSQL model.

## Acceptance State

This ADR assessment was accepted for ADP-005. It does not authorize deployment
or provider actions outside accepted Work Orders, including WO-056A custom
domain handoff and verification.
