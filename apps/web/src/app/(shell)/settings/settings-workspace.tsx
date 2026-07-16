"use client";

import * as React from "react";
import {
  Bell,
  CalendarClock,
  Database,
  Palette,
  RotateCcw,
  Save,
  Settings2,
} from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface SettingsFixture {
  workspaceName: string;
  timezone: string;
  density: "comfortable" | "compact";
  reducedMotion: boolean;
  alertDigest: boolean;
  approvalReminder: boolean;
  scheduleWindow: "always" | "business-hours";
  maxConcurrentRuns: number;
  evidenceRetentionDays: number;
}

const DEFAULT_SETTINGS: SettingsFixture = {
  workspaceName: "Atlas Operations",
  timezone: "America/Toronto",
  density: "comfortable",
  reducedMotion: false,
  alertDigest: true,
  approvalReminder: true,
  scheduleWindow: "business-hours",
  maxConcurrentRuns: 4,
  evidenceRetentionDays: 30,
};
const INPUT_CLASS =
  "mt-2 h-9 w-full rounded-atlas-md border border-border-default bg-surface px-3 text-sm text-foreground outline-none hover:border-border-strong focus:border-brand";

function ToggleField({
  id,
  label,
  description,
  checked,
  onChange,
}: {
  id: string;
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label
      htmlFor={id}
      className="flex cursor-pointer items-start justify-between gap-4 rounded-atlas-md border border-border-subtle p-3"
    >
      <span>
        <span
          id={`${id}-label`}
          className="block text-sm font-medium text-foreground"
        >
          {label}
        </span>
        <span
          id={`${id}-description`}
          className="mt-1 block text-xs leading-relaxed text-foreground-secondary"
        >
          {description}
        </span>
      </span>
      <input
        id={id}
        type="checkbox"
        aria-labelledby={`${id}-label`}
        aria-describedby={`${id}-description`}
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className="mt-1 size-4 accent-brand"
      />
    </label>
  );
}

export function SettingsWorkspace() {
  const [values, setValues] = React.useState(DEFAULT_SETTINGS);
  const [notice, setNotice] = React.useState("");
  const dirty = JSON.stringify(values) !== JSON.stringify(DEFAULT_SETTINGS);
  const update = <K extends keyof SettingsFixture>(
    key: K,
    value: SettingsFixture[K],
  ) => setValues((current) => ({ ...current, [key]: value }));
  const reset = () => {
    setValues(DEFAULT_SETTINGS);
    setNotice(
      "Session changes reset to the original fictional fixture values.",
    );
  };
  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    setNotice(
      "Simulated settings save for this session. No configuration was persisted or sent.",
    );
  };

  return (
    <form className="flex flex-col gap-5" onSubmit={submit}>
      <PageHeader
        eyebrow="Workspace"
        title="Settings"
        description="Explore fictional workspace preferences without saving configuration."
        icon={Settings2}
        meta={
          <span className="rounded-full border border-warning-border bg-warning-bg px-2.5 py-0.5 text-xs font-medium text-warning">
            Session-only simulation
          </span>
        }
      />
      <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
        <strong>Frontend prototype.</strong> Values exist only in component
        memory. No account, identity, authorization, service, browser storage,
        notification, schedule, or retention control is changed.
      </div>
      <p className="sr-only" aria-live="polite">
        {notice}
      </p>
      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader divided className="flex-row items-start gap-3">
            <Settings2
              className="mt-0.5 size-4 text-brand"
              aria-hidden="true"
            />
            <div>
              <CardTitle>Workspace</CardTitle>
              <CardDescription>
                Fictional display identity and time context
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="grid gap-4 pt-3 sm:grid-cols-2 sm:pt-3">
            <label className="text-xs font-medium text-foreground-secondary">
              Workspace name
              <input
                className={INPUT_CLASS}
                value={values.workspaceName}
                onChange={(event) =>
                  update("workspaceName", event.target.value)
                }
              />
            </label>
            <label className="text-xs font-medium text-foreground-secondary">
              Timezone
              <select
                className={INPUT_CLASS}
                value={values.timezone}
                onChange={(event) => update("timezone", event.target.value)}
              >
                <option value="America/Toronto">America/Toronto</option>
                <option value="America/Vancouver">America/Vancouver</option>
                <option value="Europe/London">Europe/London</option>
                <option value="UTC">UTC</option>
              </select>
            </label>
          </CardContent>
        </Card>
        <Card>
          <CardHeader divided className="flex-row items-start gap-3">
            <Palette className="mt-0.5 size-4 text-brand" aria-hidden="true" />
            <div>
              <CardTitle>Appearance</CardTitle>
              <CardDescription>
                Session preference examples; the shell theme control remains
                separate
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="grid gap-3 pt-3 sm:pt-3">
            <label className="text-xs font-medium text-foreground-secondary">
              Information density
              <select
                className={INPUT_CLASS}
                value={values.density}
                onChange={(event) =>
                  update(
                    "density",
                    event.target.value as SettingsFixture["density"],
                  )
                }
              >
                <option value="comfortable">Comfortable</option>
                <option value="compact">Compact</option>
              </select>
            </label>
            <ToggleField
              id="reduced-motion"
              label="Prefer reduced motion"
              description="A fictional preference descriptor; it does not modify OS or browser settings."
              checked={values.reducedMotion}
              onChange={(checked) => update("reducedMotion", checked)}
            />
          </CardContent>
        </Card>
        <Card>
          <CardHeader divided className="flex-row items-start gap-3">
            <Bell className="mt-0.5 size-4 text-brand" aria-hidden="true" />
            <div>
              <CardTitle>Notifications</CardTitle>
              <CardDescription>
                No notification is scheduled or delivered
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="grid gap-3 pt-3 sm:pt-3">
            <ToggleField
              id="alert-digest"
              label="Alert digest"
              description="Display a fictional daily digest preference."
              checked={values.alertDigest}
              onChange={(checked) => update("alertDigest", checked)}
            />
            <ToggleField
              id="approval-reminder"
              label="Approval reminders"
              description="Display a fictional reminder preference for pending reviews."
              checked={values.approvalReminder}
              onChange={(checked) => update("approvalReminder", checked)}
            />
          </CardContent>
        </Card>
        <Card>
          <CardHeader divided className="flex-row items-start gap-3">
            <CalendarClock
              className="mt-0.5 size-4 text-brand"
              aria-hidden="true"
            />
            <div>
              <CardTitle>Scheduling</CardTitle>
              <CardDescription>
                No scheduler or queue is contacted
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="grid gap-4 pt-3 sm:grid-cols-2 sm:pt-3">
            <label className="text-xs font-medium text-foreground-secondary">
              Schedule window
              <select
                className={INPUT_CLASS}
                value={values.scheduleWindow}
                onChange={(event) =>
                  update(
                    "scheduleWindow",
                    event.target.value as SettingsFixture["scheduleWindow"],
                  )
                }
              >
                <option value="business-hours">Business hours</option>
                <option value="always">Any time</option>
              </select>
            </label>
            <label className="text-xs font-medium text-foreground-secondary">
              Maximum concurrent runs
              <input
                className={INPUT_CLASS}
                type="number"
                min={1}
                max={20}
                value={values.maxConcurrentRuns}
                onChange={(event) =>
                  update("maxConcurrentRuns", Number(event.target.value))
                }
              />
            </label>
          </CardContent>
        </Card>
        <Card className="xl:col-span-2">
          <CardHeader divided className="flex-row items-start gap-3">
            <Database className="mt-0.5 size-4 text-brand" aria-hidden="true" />
            <div>
              <CardTitle>Retention declaration</CardTitle>
              <CardDescription>
                A display preference only; no record is retained or deleted
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="pt-3 sm:pt-3">
            <label className="block max-w-sm text-xs font-medium text-foreground-secondary">
              Evidence metadata retention days
              <input
                className={INPUT_CLASS}
                type="number"
                min={1}
                max={365}
                value={values.evidenceRetentionDays}
                onChange={(event) =>
                  update("evidenceRetentionDays", Number(event.target.value))
                }
              />
            </label>
            <p className="mt-3 text-xs leading-relaxed text-foreground-secondary">
              Retention enforcement requires a future service, access-control
              model, durable audit evidence, and authorized implementation. This
              form performs none of those actions.
            </p>
          </CardContent>
        </Card>
      </div>
      <div className="flex flex-col gap-3 rounded-atlas-lg border border-border-strong bg-surface p-3 shadow-atlas-md sm:flex-row sm:items-center">
        <p className="text-xs text-foreground-secondary">
          {dirty
            ? "Unsaved session-only changes"
            : "Original fictional fixture values"}
        </p>
        <div className="flex flex-wrap gap-2 sm:ml-auto">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            disabled={!dirty}
            onClick={reset}
          >
            <RotateCcw aria-hidden="true" />
            Reset session changes
          </Button>
          <Button type="submit" size="sm">
            <Save aria-hidden="true" />
            Simulate save settings
          </Button>
        </div>
      </div>
      {notice && (
        <div
          role="status"
          className="rounded-atlas-md border border-success-border bg-success-bg px-4 py-3 text-sm text-foreground"
        >
          {notice}
        </div>
      )}
    </form>
  );
}
