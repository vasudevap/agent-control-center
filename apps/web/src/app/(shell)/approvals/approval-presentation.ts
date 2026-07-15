export type ExpiryUrgency = "scheduled" | "nearing" | "imminent" | "expired" | "none";

export interface ExpiryPresentation {
  urgency: ExpiryUrgency;
  label: string;
}

const MINUTE = 60_000;
const HOUR = 60 * MINUTE;

function threshold(window: number, proportion: number, minimum: number, maximum: number) {
  return Math.min(Math.max(window * proportion, minimum), maximum);
}

export function getExpiryPresentation(expiresAt?: string, requestedAt?: string, now = Date.now()): ExpiryPresentation {
  if (!expiresAt) return { urgency: "none", label: "No expiry is set" };

  const expiry = new Date(expiresAt).getTime();
  const requested = requestedAt ? new Date(requestedAt).getTime() : Number.NaN;
  if (Number.isNaN(expiry)) return { urgency: "none", label: "Expiry time unavailable" };

  const remaining = expiry - now;
  const originalWindow = Number.isNaN(requested) || requested >= expiry ? 24 * HOUR : expiry - requested;
  const exact = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(expiry);

  if (remaining <= 0) return { urgency: "expired", label: `Expired ${exact}` };
  if (remaining <= threshold(originalWindow, 0.05, 5 * MINUTE, HOUR)) return { urgency: "imminent", label: `Expiry imminent. Expires ${exact}` };
  if (remaining <= threshold(originalWindow, 0.2, 15 * MINUTE, 24 * HOUR)) return { urgency: "nearing", label: `Nearing expiry. Expires ${exact}` };
  return { urgency: "scheduled", label: `Expires ${exact}` };
}
