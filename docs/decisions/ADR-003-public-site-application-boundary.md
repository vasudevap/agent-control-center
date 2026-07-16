# ADR-003 - Public Site Application and Hosting Boundary

**Status:** Accepted
**Date:** 2026-07-15
**Decision Owners:** Product, Architecture, and Engineering Review
**Scope:** Atlas public website

---

## Context

Atlas needs a public website that explains the product, communicates its
architecture, and accurately distinguishes implemented, designed, and planned
capabilities.

The existing `apps/web` workspace is the operational control-center product.
It contains application routes, an information-dense shell, and future
authentication and privileged API responsibilities. A public site has different
requirements: anonymous access, search and social metadata, independent release
and rollback, content-led layouts, and a smaller security boundary.

The root npm workspace already includes `apps/*`, so the repository can host a
sibling application without creating another repository.

## Decision

Atlas will implement the public website as `apps/site`, a sibling application to
`apps/web` within the existing monorepo.

| Application | Responsibility |
| --- | --- |
| `apps/site` | Public product, architecture, status, and portfolio narrative |
| `apps/web` | Atlas control-center product and future authenticated operations |

The public site will:

1. use TypeScript, React, and Next.js-compatible application conventions;
2. build through the Sites-compatible Vite/vinext toolchain;
3. deploy independently through OpenAI Sites for the initial hosted release;
4. remain static and read-only in its first release;
5. contain no authentication, persistence, external connectors, secrets, or
   privileged API access;
6. use its own public-site components while inheriting approved Atlas brand and
   design decisions;
7. be validated independently and through root workspace commands;
8. preserve a future custom-domain split between the public site and product.

The target domain model is:

```text
atlas.example.com       Public site
app.atlas.example.com   Control-center application
```

Custom-domain activation is outside this decision and requires ownership of the
selected domain and DNS configuration.

## Rationale

### Sibling application rather than routes inside `apps/web`

A separate application avoids moving existing product routes, keeps anonymous
content outside the future authenticated application boundary, and allows
independent deployment and caching.

### Monorepo rather than a separate repository

The website depends on the same brand, product status, architecture, roadmap,
and review evidence. Keeping these together reduces messaging drift and lets CI
validate product and site changes under one governance model.

### Sites hosting for the initial public release

Sites provides an independently deployable, private-first publishing path for
the new public surface without changing the existing Netlify direction for the
Atlas product application. The deployment remains isolated from the privileged
backend architecture.

## Consequences

### Positive

- Public and authenticated surfaces have explicit boundaries.
- The site can release or roll back without releasing the product application.
- Existing application routes remain stable.
- Public metadata and content layouts do not complicate the product shell.
- The website remains governed by the same repository documentation.
- The initial deployment introduces no production data or credentials.

### Trade-offs

- The repository maintains two frontend build pipelines.
- Root scripts and CI must validate both applications.
- Brand consistency is governed initially through approved documentation rather
  than a shared runtime component package.
- Dependency upgrades must consider both workspaces.
- A future custom domain requires separate DNS and hosting configuration.

### Risks and controls

- Product claims may drift from implementation status: maintain the Built,
  Designed, and Planned claim model.
- Visual tokens may diverge: inherit the approved brand and Modern
  Infrastructure direction.
- Visitors may mistake the prototype for production behavior: display
  active-development and prototype context.
- CI duration may increase: provide independent workspace scripts and aggregate
  root checks.

## Alternatives Considered

### Add marketing routes to `apps/web`

Rejected because it couples public content to the future authenticated product
boundary, would require route migration or awkward URL structure, and prevents
independent release.

### Create a separate repository

Rejected because ownership, technology, and governance are currently shared.
The additional repository would increase documentation, brand, and status drift
without a meaningful isolation benefit.

### Publish static files from the product public directory

Rejected because it provides no durable content architecture, metadata model,
independent validation, or deployment boundary.

### Extract a shared design-system package immediately

Deferred. Product components are optimized for operational interfaces, while
the site requires content-led presentation. Stable shared brand assets or tokens
may be extracted after real reuse is demonstrated.

## Implementation Constraints

- `apps/site` must not import privileged product modules or mock operational data
  directly from `apps/web`.
- The site must not expose repository-local file paths or development URLs.
- Public content must not claim production capabilities that are not implemented.
- No analytics, forms, cookies, or external scripts are authorized initially.
- The implementation must follow WO-010 and the public-site design specification.
