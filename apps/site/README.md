# Atlas Public Site

`apps/site` is the public product, architecture, and delivery-status website for
Atlas. It is a read-only sibling to the control-center product in `apps/web`.

The site is governed by:

- `docs/specifications/atlas-public-site-discovery-brief.md`
- `docs/design/12-public-site-experience.md`
- `docs/decisions/ADR-003-public-site-application-boundary.md`
- `docs/work-orders/010-atlas-public-site.md`

From the repository root:

```bash
npm run dev:site
npm run typecheck:site
npm run lint:site
npm run test:site
npm run build:site
```

The first release contains no authentication, persistence, analytics, forms,
connectors, or production operational data.
