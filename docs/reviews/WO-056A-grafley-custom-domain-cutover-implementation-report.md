# WO-056A Grafley Custom Domain Cutover Implementation Report

**Work Order:** [WO-056A](../work-orders/056a-grafley-custom-domain-cutover.md)
**Status:** Completed - Custom Domains and Runtime Cutover Verified
**Date:** 2026-07-20
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Summary

WO-056A is complete. The Netlify dashboard custom domain and Render API custom
domain are configured in their provider-native settings, the Repository
Maintainer provisioned both accepted Grafley CNAME records, provider TLS is
active for both custom domains, and runtime configuration has been cut over to
the final Grafley domains.

WO-056 remains blocked on the separate Google OAuth production callback-route
decision recorded in the WO-056 preflight report. No Google OAuth provider
values were entered under WO-056A.

No OAuth secret, database URL, signing secret, access token, refresh token, or
provider API token was recorded in Git.

## DNS Handoff

Create these CNAME records in the Grafley DNS provider:

| Host/name | Type | Target/value | Provider |
| --- | --- | --- | --- |
| `atlas` | `CNAME` | `atlas-agent-control-center.netlify.app` | Netlify dashboard |
| `api.atlas` | `CNAME` | `atlas-agent-control-center-api.onrender.com` | Render API |

DNS propagation can take 24 hours or longer. After the records resolve,
provider verification and TLS issuance must be checked before runtime
environment variables are cut over to the final domains.

Current DNS follow-up evidence after Repository Maintainer provisioning:

- `api.atlas.grafley.com` resolves to the accepted Render CNAME target,
  returned `200` from `https://api.atlas.grafley.com/health/live`, and allowed
  final-origin CORS from `https://atlas.grafley.com`.
- `atlas.grafley.com` resolves to the accepted Netlify CNAME target from
  Netfirms authoritative DNS and from multiple public resolvers.
- One public resolver still returned a stale/default `66.96.160.156` A-record
  response for `atlas.grafley.com` during the DNS propagation window. The
  matching Netfirms DNS record is the wildcard `*` A record, not an explicit
  `atlas` A record.
- Netlify TLS issuance later completed. `netlify api showSiteTLSCertificate`
  returned certificate state `issued` for `atlas.grafley.com`, and
  `netlify api getSite` reported `ssl: true`, `force_ssl: true`, and
  `url: https://atlas.grafley.com`.
- A local router resolver continued to serve the old wildcard/default A-record
  response briefly after public resolvers had converged. That cache was treated
  as local propagation lag, not a provider blocker.

## Provider Evidence

### Netlify dashboard

- Site name: `atlas-agent-control-center`
- Site ID: `cc07a93e-8ffe-47e7-b328-e5ae4247b14d`
- Provider-generated URL: `https://atlas-agent-control-center.netlify.app`
- Custom domain configured: `atlas.grafley.com`
- DNS state: external Grafley DNS provisioned; provider TLS active
- Expected DNS record: `atlas` CNAME to
  `atlas-agent-control-center.netlify.app`

Evidence:

- `netlify api listSites --data '{"name":"atlas-agent-control-center"}'`
  initially showed `custom_domain: null`.
- `netlify api updateSite` with request body
  `custom_domain: atlas.grafley.com` returned
  `custom_domain: atlas.grafley.com`.
- `netlify api getDNSForSite` returned an empty list because Netlify DNS is
  not managing the Grafley zone; the custom domain uses external DNS.
- `dig @ns1.netfirms.com +short atlas.grafley.com CNAME` returned
  `atlas-agent-control-center.netlify.app.`
- Public resolver checks showed mixed propagation: Cloudflare and Quad9
  resolved through the Netlify target, while Google Public DNS still returned a
  stale/default `66.96.160.156` A-record response with a remaining TTL during
  the propagation window.
- Later public resolver checks resolved through the Netlify target on Google
  Public DNS and Cloudflare.
- `netlify api provisionSiteTLSCertificate` was used after DNS resolved.
- `netlify api showSiteTLSCertificate` returned certificate state `issued` for
  `atlas.grafley.com`, expiring on 2026-10-18.
- `curl --resolve atlas.grafley.com:443:18.208.88.157 -I
  https://atlas.grafley.com` and the same check against `98.84.224.111`
  returned `HTTP/2 200` from Netlify with strict transport security.

### Render API

- Service name: `atlas-agent-control-center-api`
- Service ID: `srv-d9e2rprbc2fs73f4l23g`
- Provider-generated URL:
  `https://atlas-agent-control-center-api.onrender.com`
- Custom domain configured: `api.atlas.grafley.com`
- Render custom-domain status: verified after Grafley DNS provisioning
- Render certificate status: recovered; custom-domain HTTPS is active
- Expected DNS record: `api.atlas` CNAME to
  `atlas-agent-control-center-api.onrender.com`

Evidence:

- `render services --output json` confirmed the Atlas API service ID and
  provider-generated URL.
- Render CLI v2.21.0 does not expose a first-class custom-domain command, so
  the custom-domain binding was performed through the authenticated Render
  dashboard in Chrome.
- The Render dashboard showed the service had already used `2 / 2` included
  custom domains. The Repository Maintainer explicitly approved adding
  `api.atlas.grafley.com` at the displayed `$0.25 per month` charge.
- The Render dashboard accepted `api.atlas.grafley.com` and displayed the DNS
  instruction to add a CNAME record with target
  `atlas-agent-control-center-api.onrender.com`.

Follow-up verification after Repository Maintainer DNS provisioning:

- `dig +short api.atlas.grafley.com CNAME` returned
  `atlas-agent-control-center-api.onrender.com.`
- `dig +short api.atlas.grafley.com` resolved through Render/Cloudflare
  infrastructure to IPv4 addresses.
- `dig +short api.atlas.grafley.com AAAA` returned only the CNAME chain and no
  IPv6 address.
- `dig +short api.atlas.grafley.com CAA` returned only the CNAME chain and no
  restrictive CAA record.
- Render dashboard verification changed `api.atlas.grafley.com` to
  `Verified`.
- Render dashboard certificate status changed to `Certificate Error`.
- HTTPS probing `https://api.atlas.grafley.com/health/live` still failed while
  the certificate error was present.
- Later HTTPS probing `https://api.atlas.grafley.com/health/live` returned
  `HTTP/2 200` with `{"status":"ok","service":"atlas-api","environment":"production"}`.

Render guidance reviewed:

- Render custom-domain documentation says DNS verification can lag after DNS
  changes, Render issues TLS certificates after successful verification, and
  DNS changes can take 24 hours or longer to propagate.
- Render DNS guidance says to remove `AAAA` records for custom domains while
  configuring Render because Render uses IPv4.
- Render CAA guidance says that domains with CAA records must allow Render's
  certificate authorities: Let's Encrypt and Google Trust Services.

No conflicting `AAAA` address or restrictive CAA record was observed from the
local DNS checks at the time of this report update.

## Secret Exposure and Rotation Record

While inspecting the Render Settings page, the browser DOM exposed the private
Render deploy-hook URL value. The value was not committed to Git and is not
reproduced in this report.

Emergency response:

- The custom-domain workflow was paused.
- The Render deploy hook was regenerated through the provider dashboard.
- A follow-up DOM check confirmed the page no longer exposed a raw Render
  deploy-hook URL.

Residual impact:

- Any external automation that used the old Render deploy hook must be updated
  with the new provider-native value if such automation exists.
- The current repository cutover flow relies on Git auto-deploy and does not
  depend on a committed deploy-hook value.

## Explicitly Not Performed

- No Grafley DNS records were created by Codex.
- No Google OAuth client, client secret, or redirect URI was configured.
- No hosted migration was run.
- No public launch, release tag, production mailbox scan, or production data
  workflow was performed.

## Runtime Cutover Evidence

Runtime cutover was performed only after provider TLS was active for the final
Grafley domains:

- Netlify production `NEXT_PUBLIC_API_BASE_URL` was updated from
  `https://atlas-agent-control-center-api.onrender.com` to
  `https://api.atlas.grafley.com`.
- `netlify api createSiteBuild` triggered production build
  `6a5e810bc589f817962f4682` and deploy
  `6a5e810bc589f817962f4684`; `netlify api getSiteBuild` returned
  `deploy_state: ready`, `done: true`, and `error: null`.
- Render service environment variable `ATLAS_API_FRONTEND_ORIGIN` was updated
  to `https://atlas.grafley.com` through the authenticated provider dashboard
  without exposing adjacent secret values.
- Render deploy `dep-d9f82qhkh4rs73dnaa0g` was triggered by
  `service_updated` and reached `live`.
- `curl -H 'Origin: https://atlas.grafley.com'
  https://api.atlas.grafley.com/health/ready` returned `HTTP/2 200` with
  `access-control-allow-origin: https://atlas.grafley.com`.
- The matching final-origin CORS preflight returned `HTTP/2 200` and `OK`.
- Readiness remains fail-closed for the expected WO-056/owner configuration
  problems: Google OAuth client ID, Google OAuth client secret, Google OAuth
  redirect URI, and owner identity subject are still missing.

## WO-056 OAuth Handoff

Do not carry the earlier placeholder
`https://api.atlas.grafley.com/api/auth/google/callback` into Google provider
setup. Source inspection found no matching route; WO-056 must choose and
implement or confirm the browser-facing OAuth callback surface before provider
values are entered.

## Validation State

Completed:

- Netlify custom domain binding created.
- Render custom domain binding created after maintainer approval of the
  provider charge.
- DNS CNAME record values captured.
- Repository Maintainer provisioned the accepted `atlas` and `api.atlas`
  Grafley DNS CNAME records.
- API DNS verified by Render.
- Frontend authoritative DNS verified through the Netfirms nameserver.
- Public DNS verified through Netlify and Render targets.
- Netlify TLS issued for `atlas.grafley.com`.
- Render custom-domain TLS recovered for `api.atlas.grafley.com`.
- Netlify `NEXT_PUBLIC_API_BASE_URL` cut over to
  `https://api.atlas.grafley.com` and rebuilt.
- Render `ATLAS_API_FRONTEND_ORIGIN` cut over to
  `https://atlas.grafley.com` and redeployed.
- API liveness and final-origin readiness CORS verified from
  `https://api.atlas.grafley.com`.
- Render deploy hook regenerated after exposure.

Pending:

- WO-056 must choose and implement or confirm the production Google OAuth
  browser callback surface before Google provider values are entered.
- WO-053/WO-055 readiness remains fail-closed until owner identity and Google
  OAuth values are configured under the appropriate Work Orders.

## Rollback Notes

Rollback remains provider-native:

- Netlify can remove or replace the `atlas.grafley.com` custom-domain binding
  while retaining `https://atlas-agent-control-center.netlify.app`.
- Render can remove or replace the `api.atlas.grafley.com` custom-domain
  binding while retaining
  `https://atlas-agent-control-center-api.onrender.com`.
- If the final-domain runtime cutover must be rolled back, restore Netlify
  `NEXT_PUBLIC_API_BASE_URL` to
  `https://atlas-agent-control-center-api.onrender.com`, restore Render
  `ATLAS_API_FRONTEND_ORIGIN` to
  `https://atlas-agent-control-center.netlify.app`, and redeploy both targets.
