export type ExpiryUrgency = "scheduled" | "nearing" | "imminent" | "expired" | "none";

export interface ExpiryPresentation {
  urgency: ExpiryUrgency;
  label: string;
  shortLabel: string;
}

const MINUTE = 60_000;
const HOUR = 60 * MINUTE;

function threshold(window: number, proportion: number, minimum: number, maximum: number) {
  return Math.min(Math.max(window * proportion, minimum), maximum);
}

/**
 * Derives presentation-only expiry urgency from canonical request/expiry
 * timestamps, per architecture/13-human-approvals.md section 18. This is a
 * client-side presentation facet only; the browser is never authoritative
 * for real expiry, as the architecture explicitly states.
 */
export function getExpiryPresentation(expiresAt?: string, requestedAt?: string, referenceNow = Date.now()): ExpiryPresentation {
  if (!expiresAt) return { urgency: "none", label: "No expiry is set", shortLabel: "No expiry" };

  const expiry = new Date(expiresAt).getTime();
  const requested = requestedAt ? new Date(requestedAt).getTime() : Number.NaN;
  if (Number.isNaN(expiry)) return { urgency: "none", label: "Expiry time unavailable", shortLabel: "Unknown" };

  const remaining = expiry - referenceNow;
  const originalWindow = Number.isNaN(requested) || requested >= expiry ? 24 * HOUR : expiry - requested;
  const exact = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(expiry);

  if (remaining <= 0) return { urgency: "expired", label: `Expired ${exact}`, shortLabel: "Expired" };
  if (remaining <= threshold(originalWindow, 0.05, 5 * MINUTE, HOUR)) return { urgency: "imminent", label: `Expiry imminent. Expires ${exact}`, shortLabel: "Imminent" };
  if (remaining <= threshold(originalWindow, 0.2, 15 * MINUTE, 24 * HOUR)) return { urgency: "nearing", label: `Nearing expiry. Expires ${exact}`, shortLabel: "Nearing" };
  return { urgency: "scheduled", label: `Expires ${exact}`, shortLabel: "On track" };
}

export function relativeTime(iso: string, referenceNow = Date.now()) {
  const diff = new Date(iso).getTime() - referenceNow;
  const abs = Math.abs(diff);
  const HOUR_MS = 3600_000;
  const DAY_MS = 24 * HOUR_MS;
  const unit = abs >= DAY_MS ? "day" : abs >= HOUR_MS ? "hour" : "minute";
  const value = unit === "day" ? Math.round(abs / DAY_MS) : unit === "hour" ? Math.round(abs / HOUR_MS) : Math.max(1, Math.round(abs / 60000));
  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
  return formatter.format(diff < 0 ? -value : value, unit);
}
