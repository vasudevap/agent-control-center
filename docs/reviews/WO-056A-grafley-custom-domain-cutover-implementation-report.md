# WO-056A Grafley Custom Domain Cutover Implementation Report

**Work Order:** [WO-056A](../work-orders/056a-grafley-custom-domain-cutover.md)
**Status:** In Progress - DNS Propagation and Certificates Pending
**Date:** 2026-07-20
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Summary

WO-056A provider-domain setup has started. The Netlify dashboard custom domain
and Render API custom domain are configured in their provider-native settings.
The exact DNS CNAME records needed from Grafley DNS were captured and the
Repository Maintainer has provisioned both Grafley CNAME records. API DNS has
been verified by Render, but Render certificate issuance is still in an error
state. Frontend authoritative DNS now returns the Netlify CNAME, but at least
one public resolver still served a stale wildcard/default A-record response
during propagation.

WO-056A is not complete yet. The remaining gates are DNS propagation
convergence, provider TLS/certificate verification, runtime environment
cutover, hosted browser/API checks from the final domains, and the final OAuth
redirect decision under WO-056.

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

- `api.atlas.grafley.com` resolves to the accepted Render CNAME target and is
  verified in the Render dashboard.
- `atlas.grafley.com` resolves to the accepted Netlify CNAME target from
  Netfirms authoritative DNS and from multiple public resolvers.
- One public resolver still returned a stale/default `66.96.160.156` A-record
  response for `atlas.grafley.com` during the DNS propagation window. The
  matching Netfirms DNS record is the wildcard `*` A record, not an explicit
  `atlas` A record.
- No Netfirms DNS change beyond the accepted `atlas` and `api.atlas` CNAME
  records is recommended unless stale wildcard/default responses persist after
  the propagation window.

## Provider Evidence

### Netlify dashboard

- Site name: `atlas-agent-control-center`
- Site ID: `cc07a93e-8ffe-47e7-b328-e5ae4247b14d`
- Provider-generated URL: `https://atlas-agent-control-center.netlify.app`
- Custom domain configured: `atlas.grafley.com`
- DNS state: external Grafley DNS provisioned; propagation and certificate
  issuance pending
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
- HTTPS probing `https://atlas.grafley.com` still failed certificate
  validation while DNS propagation and Netlify certificate issuance were
  pending.

### Render API

- Service name: `atlas-agent-control-center-api`
- Service ID: `srv-d9e2rprbc2fs73f4l23g`
- Provider-generated URL:
  `https://atlas-agent-control-center-api.onrender.com`
- Custom domain configured: `api.atlas.grafley.com`
- Render custom-domain status: verified after Grafley DNS provisioning
- Render certificate status: certificate error
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
- No Netlify or Render runtime environment variables were cut over to the
  final custom domains.
- No public launch, release tag, production mailbox scan, or production data
  workflow was performed.

## Pending Final Cutover Checklist

Do not perform these steps until both custom domains resolve consistently and
provider TLS/certificate status is healthy:

1. Verify `https://atlas.grafley.com` serves the Netlify-hosted dashboard over
   valid HTTPS.
2. Verify `https://api.atlas.grafley.com/health/live` returns the Atlas API
   health response over valid HTTPS.
3. Update Netlify production environment variable
   `NEXT_PUBLIC_API_BASE_URL` from the provider-generated Render API URL to
   `https://api.atlas.grafley.com`.
4. Redeploy the Netlify production site so the browser-visible API base URL is
   rebuilt into the dashboard.
5. Update Render API environment variable `ATLAS_API_FRONTEND_ORIGIN` from the
   provider-generated Netlify origin to `https://atlas.grafley.com`.
6. Redeploy or restart the Render API service so the CORS origin change is
   active.
7. Verify browser/API integration from `https://atlas.grafley.com`, including
   runtime-health behavior and an API readiness request with the final
   frontend origin.
8. Do not carry the earlier placeholder
   `https://api.atlas.grafley.com/api/auth/google/callback` into Google
   provider setup. Source inspection found no matching route; WO-056 must
   choose and implement or confirm the browser-facing OAuth callback surface
   before provider values are entered.

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
- Render deploy hook regenerated after exposure.

Pending:

- DNS propagation converges for the frontend custom domain across public
  resolvers.
- Netlify TLS/certificate status verified for `atlas.grafley.com`.
- Render certificate verification recovered for `api.atlas.grafley.com`.
- Netlify `NEXT_PUBLIC_API_BASE_URL` cut over to
  `https://api.atlas.grafley.com`.
- Render `ATLAS_API_FRONTEND_ORIGIN` cut over to
  `https://atlas.grafley.com`.
- Hosted dashboard/API readiness checked from the final custom domains.
- WO-056 Google OAuth redirect uses the final API domain unless a documented
  deferment is accepted.

## Rollback Notes

Rollback remains provider-native:

- Netlify can remove or replace the `atlas.grafley.com` custom-domain binding
  while retaining `https://atlas-agent-control-center.netlify.app`.
- Render can remove or replace the `api.atlas.grafley.com` custom-domain
  binding while retaining
  `https://atlas-agent-control-center-api.onrender.com`.
- Runtime variables remain on provider-generated URLs until DNS/TLS
  verification succeeds, so no runtime URL rollback is currently required.
