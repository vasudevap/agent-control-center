"use client";

import * as React from "react";
import { Pause, Play, RotateCcw, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { AgentStatus } from "../agent-data";

type ControlAction = "run" | "pause" | "resume";

interface AgentOperationalControlsProps {
  agentId: string;
  agentName: string;
  initialStatus: AgentStatus;
}

const ACTION_CONTENT: Record<
  ControlAction,
  { title: string; description: string; confirmLabel: string }
> = {
  run: {
    title: "Simulate a manual run?",
    description:
      "The prototype demonstrates configuration, connector, permission, policy, and duplicate-run validation without queueing this agent.",
    confirmLabel: "Simulate manual run",
  },
  pause: {
    title: "Simulate pausing scheduled runs?",
    description:
      "The local fixture will display a paused state. No schedule changes, and a fictional run already in progress remains unchanged.",
    confirmLabel: "Simulate pause",
  },
  resume: {
    title: "Simulate resuming scheduled runs?",
    description:
      "The local fixture will display an active state. No schedule changes and no immediate run starts.",
    confirmLabel: "Simulate resume",
  },
};

export function AgentOperationalControls({
  agentId,
  agentName,
  initialStatus,
}: AgentOperationalControlsProps) {
  const [status, setStatus] = React.useState(initialStatus);
  const [action, setAction] = React.useState<ControlAction | null>(null);
  const [notice, setNotice] = React.useState<string | null>(null);
  const isPaused = status === "paused";
  const runBlocked = status === "running" || status === "queued";

  React.useEffect(() => {
    if (!action) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setAction(null);
    };

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [action]);

  const confirmAction = () => {
    if (!action) return;

    if (action === "run") {
      setNotice(`Simulated manual run prepared for ${agentName}.`);
    } else if (action === "pause") {
      setStatus("paused");
      setNotice("Simulated paused state applied to this local fixture.");
    } else {
      setStatus("active");
      setNotice("Simulated active state applied to this local fixture.");
    }

    setAction(null);
  };

  const content = action ? ACTION_CONTENT[action] : null;

  return (
    <>
      <div className="grid w-full grid-cols-2 gap-2 sm:flex sm:w-auto">
        <Button
          className="w-full sm:w-auto"
          variant="secondary"
          size="sm"
          onClick={() => setAction(isPaused ? "resume" : "pause")}
        >
          {isPaused ? <RotateCcw aria-hidden="true" /> : <Pause aria-hidden="true" />}
          {isPaused ? "Simulate resume" : "Simulate pause"}
        </Button>
        <Button
          className="w-full sm:w-auto"
          size="sm"
          onClick={() => setAction("run")}
          disabled={runBlocked}
          title={runBlocked ? "A run is already active or queued" : undefined}
        >
          <Play aria-hidden="true" />
          Simulate run
        </Button>
      </div>

      {action && content && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 p-4 backdrop-blur-[2px]"
          role="presentation"
          onMouseDown={(event) => {
            if (event.currentTarget === event.target) setAction(null);
          }}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="agent-control-title"
            className="w-full max-w-lg rounded-atlas-lg border border-border-default bg-surface p-6 shadow-2xl"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-2">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand">
                  Operational control
                </p>
                <h2 id="agent-control-title" className="text-xl font-semibold text-foreground">
                  {content.title}
                </h2>
              </div>
              <Button
                variant="ghost"
                size="icon"
                aria-label="Close dialog"
                onClick={() => setAction(null)}
              >
                <X aria-hidden="true" />
              </Button>
            </div>

            <p className="mt-4 text-sm leading-relaxed text-foreground-secondary">
              {content.description}
            </p>

            <dl className="mt-5 grid gap-3 rounded-atlas-md border border-border-default bg-surface-secondary p-4 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-foreground-tertiary">Agent</dt>
                <dd className="mt-1 font-medium text-foreground">{agentName}</dd>
              </div>
              <div>
                <dt className="text-foreground-tertiary">Agent ID</dt>
                <dd className="mt-1 break-all font-mono text-xs text-foreground">{agentId}</dd>
              </div>
            </dl>

            <p className="mt-4 rounded-atlas-md border border-warning/30 bg-warning/10 px-3 py-2 text-xs leading-relaxed text-foreground-secondary">
              Frontend prototype: confirming demonstrates the interaction only. No runtime request is sent.
            </p>

            <div className="mt-6 flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setAction(null)}>
                Cancel
              </Button>
              <Button
                variant={action === "pause" ? "secondary" : "primary"}
                onClick={confirmAction}
              >
                {content.confirmLabel}
              </Button>
            </div>
          </section>
        </div>
      )}

      {notice && (
        <div
          role="status"
          className="fixed bottom-5 right-5 z-40 max-w-sm rounded-atlas-md border border-border-default bg-surface p-4 shadow-xl"
        >
          <div className="flex items-start gap-3">
            <div className="min-w-0">
              <p className="text-sm font-medium text-foreground">{notice}</p>
              <p className="mt-1 text-xs leading-relaxed text-foreground-tertiary">
                Prototype only. No runtime or schedule state was changed.
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="-mr-2 -mt-2"
              aria-label="Dismiss message"
              onClick={() => setNotice(null)}
            >
              <X aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}
    </>
  );
}
