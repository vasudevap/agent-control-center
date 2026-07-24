"use client";

import Link from "next/link";
import {
  Activity,
  ArrowRight,
  Bell,
  Bot,
  CheckCircle2,
  Fingerprint,
  LogIn,
  RadioTower,
  Workflow,
} from "lucide-react";

import { GoogleLogo } from "@/components/brand/google-logo";
import { Button } from "@/components/ui/button";
import { dashboardSignInUrl } from "@/lib/dashboard-runtime";

const CONTROL_CENTER_HREF = "/control-center";

const trustSignals = [
  { label: "Known", value: "12", state: "Enrolled agents" },
  { label: "Late", value: "02", state: "Needs review" },
  { label: "Open", value: "04", state: "Active alerts" },
];

const problemStatements = [
  {
    title: "Agent activity is scattered",
    detail:
      "Each external runtime has its own logs, credentials, configuration, and status signals.",
  },
  {
    title: "Trust is hard to prove",
    detail:
      "Owners need evidence of identity, last contact, credential state, and reported work before they can rely on an agent.",
  },
  {
    title: "Attention arrives too late",
    detail:
      "Failures, missed heartbeats, and stale connections should be visible before they become operational surprises.",
  },
];

const valuePillars = [
  {
    icon: Fingerprint,
    title: "Agent identity",
    detail:
      "Enroll external agents with stable identities, lifecycle status, environment, version, and credential posture.",
  },
  {
    icon: RadioTower,
    title: "Observed connection health",
    detail:
      "Separate what Atlas last accepted from what an agent reports, so operational status stays precise.",
  },
  {
    icon: Bell,
    title: "Attention and alerts",
    detail:
      "Surface late, offline, disconnected, failing, and recovered states in the owner workflow.",
  },
  {
    icon: Workflow,
    title: "Reported execution history",
    detail:
      "Review bounded execution summaries and outcomes without implying Atlas dispatched the work.",
  },
];

const boundaries = [
  "Atlas observes external agents through authenticated contact.",
  "Atlas manages trust lifecycle, credential rotation, and owner visibility.",
  "Atlas does not host, schedule, execute, pause, resume, or stop external runtimes.",
];

function AtlasSignalScene() {
  return (
    <div className="absolute inset-0 overflow-hidden bg-background" aria-hidden="true">
      {Array.from({ length: 9 }).map((_, index) => (
        <span
          key={`vertical-${index}`}
          className="absolute top-0 h-full w-px bg-border-subtle"
          style={{ left: `${(index + 1) * 10}%`, opacity: 0.5 }}
        />
      ))}
      {Array.from({ length: 7 }).map((_, index) => (
        <span
          key={`horizontal-${index}`}
          className="absolute left-0 h-px w-full bg-border-subtle"
          style={{ top: `${(index + 1) * 12}%`, opacity: 0.45 }}
        />
      ))}

      <div className="absolute right-4 top-20 hidden w-[46vw] max-w-3xl md:block">
        <div className="border border-border-default bg-surface/80 p-4 shadow-atlas-md backdrop-blur">
          <div className="mb-4 flex items-center justify-between border-b border-border-default pb-3">
            <div>
              <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-brand">
                Live posture
              </p>
              <p className="mt-1 text-sm font-medium text-foreground">
                External agent visibility
              </p>
            </div>
            <span className="flex size-9 items-center justify-center rounded-atlas-sm border border-success-border bg-success-bg text-success">
              <Activity className="size-4" />
            </span>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {trustSignals.map((signal) => (
              <div
                key={signal.label}
                className="border border-border-subtle bg-surface-secondary p-3"
              >
                <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-foreground-tertiary">
                  {signal.label}
                </p>
                <p className="mt-2 font-mono text-3xl font-semibold text-foreground">
                  {signal.value}
                </p>
                <p className="mt-1 text-xs text-foreground-secondary">
                  {signal.state}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-4 grid gap-2">
            {[
              ["gmail-ops-agent", "online", "last accepted heartbeat 41s ago"],
              ["asset-index-agent", "late", "expected contact window missed"],
              [
                "finance-reconcile-agent",
                "reported failed",
                "execution summary received",
              ],
            ].map(([name, state, detail]) => (
              <div
                key={name}
                className="flex items-center justify-between gap-4 border border-border-subtle bg-background px-3 py-2"
              >
                <div className="min-w-0">
                  <p className="truncate font-mono text-xs text-foreground">{name}</p>
                  <p className="truncate text-xs text-foreground-tertiary">{detail}</p>
                </div>
                <span className="shrink-0 rounded-atlas-sm border border-border-default px-2 py-1 font-mono text-[10px] uppercase tracking-[0.08em] text-foreground-secondary">
                  {state}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="absolute bottom-10 right-8 hidden w-64 border border-border-default bg-surface-secondary/90 p-3 md:block">
        <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-foreground-tertiary">
          Boundary
        </p>
        <p className="mt-2 text-xs leading-5 text-foreground-secondary">
          Atlas verifies contact. External runtimes remain outside the control center.
        </p>
      </div>
    </div>
  );
}

function LandingCta() {
  const signInUrl = dashboardSignInUrl();
  const primaryHref = signInUrl || CONTROL_CENTER_HREF;
  const primaryLabel = signInUrl ? "Sign in with Google" : "Open control center";

  return (
    <div className="flex flex-col gap-3 sm:flex-row">
      <Button asChild size="lg" className="w-full sm:w-auto">
        <a href={primaryHref}>
          {signInUrl ? <GoogleLogo /> : <LogIn className="size-4" />}
          {primaryLabel}
        </a>
      </Button>
      <Button asChild variant="secondary" size="lg" className="w-full sm:w-auto">
        <Link href={CONTROL_CENTER_HREF}>
          Preview control center
          <ArrowRight className="size-4" />
        </Link>
      </Button>
    </div>
  );
}

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="relative min-h-[92vh] overflow-hidden border-b border-border-default">
        <AtlasSignalScene />
        <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
          <Link href="/" className="flex items-center gap-2" aria-label="Atlas home">
            <span className="flex size-8 items-center justify-center rounded-atlas-sm bg-brand-solid text-foreground-on-brand">
              <Bot className="size-4" aria-hidden="true" />
            </span>
            <span className="font-mono text-sm font-semibold uppercase tracking-[0.14em]">
              Atlas
            </span>
          </Link>
          <Button asChild variant="ghost" size="sm">
            <Link href={CONTROL_CENTER_HREF}>
              Control center
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </header>

        <div className="relative z-10 mx-auto flex max-w-7xl flex-col justify-center px-5 pb-16 pt-16 sm:px-8 lg:min-h-[calc(92vh-4.5rem)] lg:pb-24 lg:pt-10">
          <div className="max-w-2xl">
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-brand">
              Agent Visibility Control Center
            </p>
            <h1 className="mt-5 text-6xl font-semibold leading-none text-foreground sm:text-7xl lg:text-8xl">
              Atlas
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-foreground-secondary sm:text-xl">
              A secure control center for understanding which external AI agents
              are known, trusted, connected, healthy, failing, or waiting for
              owner attention.
            </p>
            <div className="mt-8">
              <LandingCta />
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-border-default bg-surface">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 py-14 sm:px-8 lg:grid-cols-[0.8fr_1.2fr] lg:py-18">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-brand">
              The problem
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-normal text-foreground">
              AI agents become operational systems before teams get an operating model.
            </h2>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            {problemStatements.map((item) => (
              <article
                key={item.title}
                className="border border-border-default bg-background p-4"
              >
                <h3 className="text-base font-semibold text-foreground">{item.title}</h3>
                <p className="mt-3 text-sm leading-6 text-foreground-secondary">
                  {item.detail}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-b border-border-default">
        <div className="mx-auto max-w-7xl px-5 py-14 sm:px-8 lg:py-18">
          <div className="max-w-3xl">
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-brand">
              What Atlas is
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-normal text-foreground">
              A single owner-facing place for agent trust, health, alerts, and reported work.
            </h2>
            <p className="mt-4 text-base leading-7 text-foreground-secondary">
              Atlas gives the owner an honest operational view of external agents.
              It records authenticated contact and bounded summaries so attention
              can move from scattered runtime clues into one disciplined console.
            </p>
          </div>

          <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {valuePillars.map((pillar) => {
              const Icon = pillar.icon;
              return (
                <article
                  key={pillar.title}
                  className="border border-border-default bg-surface p-4"
                >
                  <span className="flex size-9 items-center justify-center rounded-atlas-sm border border-border-default bg-surface-secondary text-brand">
                    <Icon className="size-4" aria-hidden="true" />
                  </span>
                  <h3 className="mt-4 text-base font-semibold text-foreground">
                    {pillar.title}
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-foreground-secondary">
                    {pillar.detail}
                  </p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="border-b border-border-default bg-surface">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 py-14 sm:px-8 lg:grid-cols-[1fr_1fr] lg:py-18">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-brand">
              The value
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-normal text-foreground">
              Operational confidence without false control-plane claims.
            </h2>
            <p className="mt-4 text-base leading-7 text-foreground-secondary">
              Atlas helps owners see evidence, act on attention signals, and
              manage the trust lifecycle while keeping each agent runtime outside
              Atlas where it belongs.
            </p>
          </div>
          <div className="grid gap-3">
            {boundaries.map((boundary) => (
              <div
                key={boundary}
                className="flex gap-3 border border-border-default bg-background p-4"
              >
                <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-success" aria-hidden="true" />
                <p className="text-sm leading-6 text-foreground-secondary">{boundary}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-background">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-12 sm:px-8 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-brand">
              Owner access
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-foreground">
              Enter the Atlas control center.
            </h2>
          </div>
          <LandingCta />
        </div>
      </section>
    </main>
  );
}
