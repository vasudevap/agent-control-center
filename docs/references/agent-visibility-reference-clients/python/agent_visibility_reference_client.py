#!/usr/bin/env python3
"""WO-071 Atlas Agent Visibility reference client.

This client intentionally uses only the Python standard library. It imports no
Atlas server packages and never prints owner cookies or generated agent tokens.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

CONTRACT_VERSION = "2026-07-24"


@dataclass(frozen=True)
class Config:
    base_url: str
    owner_cookie_header: str
    slug_prefix: str
    alert_timeout_seconds: int
    verify_health_loss: bool


class AtlasHttpError(RuntimeError):
    def __init__(self, status: int, body: dict[str, Any]) -> None:
        super().__init__(f"Atlas request failed with HTTP {status}")
        self.status = status
        self.body = body


def load_config() -> Config:
    cookie = require_env("ATLAS_OWNER_SESSION_COOKIE")
    return Config(
        base_url=os.environ.get("ATLAS_API_BASE_URL", "https://api.atlas.grafley.com").rstrip(
            "/"
        ),
        owner_cookie_header=normalize_cookie(cookie),
        slug_prefix=os.environ.get("ATLAS_REFERENCE_SLUG_PREFIX", "wo071-reference"),
        alert_timeout_seconds=int(
            os.environ.get("ATLAS_REFERENCE_ALERT_TIMEOUT_SECONDS", "180")
        ),
        verify_health_loss=os.environ.get(
            "ATLAS_REFERENCE_VERIFY_HEALTH_LOSS", "false"
        ).lower()
        in {"1", "true", "yes"},
    )


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} must be supplied outside the repository.")
    return value


def normalize_cookie(value: str) -> str:
    return value if "=" in value else f"atlas_owner_session={value}"


def request_json(
    config: Config,
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    owner: bool = False,
    csrf_token: str | None = None,
    agent_token: str | None = None,
    idempotency_key: str | None = None,
    expect_status: set[int] | None = None,
) -> dict[str, Any]:
    payload = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if owner:
        headers["Cookie"] = config.owner_cookie_header
    if csrf_token is not None:
        headers["X-Atlas-CSRF-Token"] = csrf_token
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    if agent_token is not None:
        headers["Authorization"] = f"Bearer {agent_token}"
    request = urllib.request.Request(
        f"{config.base_url}{path}",
        data=payload,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        status = error.code
        data = json.loads(error.read().decode("utf-8") or "{}")
    allowed = expect_status or {200, 201, 202}
    if status not in allowed:
        raise AtlasHttpError(status, data)
    return {"status": status, "body": data}


def iso_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def evidence(step: str, **details: Any) -> None:
    print(json.dumps({"step": step, **details}, sort_keys=True))


def heartbeat(
    config: Config,
    *,
    agent_id: str,
    token: str,
    event_id: str,
    status: str = "healthy",
    checks: list[dict[str, str]] | None = None,
    expect_status: set[int] | None = None,
) -> dict[str, Any]:
    return request_json(
        config,
        "POST",
        f"/api/v1/agents/{agent_id}/heartbeats",
        body={
            "event_id": event_id,
            "contract_version": CONTRACT_VERSION,
            "sent_at": iso_now(),
            "environment": "wo071-hosted",
            "status": status,
            "checks": checks or [{"name": "reference", "status": "healthy"}],
            "agent_version": "wo071-reference-python",
            "build_sha": "wo071-reference",
        },
        agent_token=token,
        expect_status=expect_status,
    )


def execution(
    config: Config,
    *,
    agent_id: str,
    token: str,
    execution_id: str,
    status: str,
    error_code: str | None = None,
) -> dict[str, Any]:
    now = iso_now()
    return request_json(
        config,
        "PUT",
        f"/api/v1/agents/{agent_id}/executions/{execution_id}",
        body={
            "contract_version": CONTRACT_VERSION,
            "representation_hash": f"sha256:{execution_id}",
            "status": status,
            "trigger": "wo071_reference",
            "started_at": now,
            "finished_at": now,
            "duration_ms": 1000,
            "summary": f"WO-071 reference execution {status}.",
            "error_code": error_code,
            "correlation_id": f"wo071-{execution_id}",
            "agent_version": "wo071-reference-python",
            "build_sha": "wo071-reference",
        },
        agent_token=token,
    )


def lifecycle(
    config: Config,
    *,
    csrf_token: str,
    agent_id: str,
    suffix: str,
) -> dict[str, Any]:
    return request_json(
        config,
        "POST",
        f"/api/v1/dashboard/agents/{agent_id}{suffix}",
        owner=True,
        csrf_token=csrf_token,
        idempotency_key=f"wo071-{suffix.strip('/').replace('/', '-')}-{uuid4().hex}",
    )["body"]["data"]


def poll_agent(
    config: Config,
    *,
    agent_id: str,
    expected_observed: set[str],
    timeout_seconds: int,
) -> str:
    deadline = time.monotonic() + timeout_seconds
    observed = "unknown"
    while time.monotonic() < deadline:
        data = request_json(
            config,
            "GET",
            f"/api/v1/dashboard/agents/{agent_id}",
            owner=True,
        )["body"]["data"]
        observed = str(data.get("observed_health"))
        if observed in expected_observed:
            return observed
        time.sleep(10)
    raise RuntimeError(
        f"Timed out waiting for observed health {sorted(expected_observed)}; "
        f"last value was {observed}."
    )


def poll_alert(
    config: Config,
    *,
    condition_suffix: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        alerts = request_json(config, "GET", "/api/v1/alerts", owner=True)["body"][
            "data"
        ]
        for alert in alerts:
            if str(alert.get("condition_key", "")).endswith(condition_suffix):
                return alert
        time.sleep(10)
    raise RuntimeError(f"Timed out waiting for alert suffix {condition_suffix!r}.")


def main() -> int:
    config = load_config()
    session = request_json(config, "GET", "/api/v1/dashboard/session", owner=True)[
        "body"
    ]["data"]
    csrf_token = session["csrf_token"]
    slug = f"{config.slug_prefix}-{int(time.time())}-{uuid4().hex[:8]}"
    enrolled = request_json(
        config,
        "POST",
        "/api/v1/dashboard/agents",
        owner=True,
        csrf_token=csrf_token,
        idempotency_key=f"wo071-enroll-{uuid4().hex}",
        body={
            "slug": slug,
            "display_name": f"WO-071 Reference Agent {slug[-8:]}",
            "description": "Hosted WO-071 reference verification agent.",
            "environment": "wo071-hosted",
            "monitoring_mode": "heartbeat",
            "heartbeat_interval_seconds": 30,
            "tags": ["wo071", "reference"],
            "expected_version": "wo071-reference-python",
        },
    )["body"]["data"]
    agent_id = enrolled["agent"]["agent_id"]
    token = enrolled["credential"]["plaintext_token"]
    evidence("enrolled", agent_id=agent_id, slug=slug, credential="redacted")

    heartbeat(config, agent_id=agent_id, token=token, event_id=f"{slug}-first")
    evidence("first_heartbeat_accepted", agent_id=agent_id)

    heartbeat(
        config,
        agent_id=agent_id,
        token=token,
        event_id=f"{slug}-failed-check",
        status="unhealthy",
        checks=[
            {
                "name": "reference-dependency",
                "status": "unhealthy",
                "error_code": "WO071_REFERENCE_CHECK_FAILED",
            }
        ],
    )
    alert = poll_alert(
        config,
        condition_suffix=":check:reference-dependency",
        timeout_seconds=config.alert_timeout_seconds,
    )
    evidence("failed_check_alert_opened", alert_id=alert["alert_id"])

    execution(
        config,
        agent_id=agent_id,
        token=token,
        execution_id=f"{slug}-success",
        status="succeeded",
    )
    for index in range(3):
        execution(
            config,
            agent_id=agent_id,
            token=token,
            execution_id=f"{slug}-failed-{index}",
            status="failed",
            error_code="WO071_REFERENCE_EXECUTION_FAILED",
        )
    repeated = poll_alert(
        config,
        condition_suffix=":execution:repeated-failure",
        timeout_seconds=config.alert_timeout_seconds,
    )
    evidence("repeated_failure_alert_opened", alert_id=repeated["alert_id"])

    if config.verify_health_loss:
        late = poll_agent(
            config,
            agent_id=agent_id,
            expected_observed={"late", "offline"},
            timeout_seconds=180,
        )
        evidence("heartbeat_loss_observed", observed_health=late)
        heartbeat(
            config,
            agent_id=agent_id,
            token=token,
            event_id=f"{slug}-recovery",
        )
        recovered = poll_agent(
            config,
            agent_id=agent_id,
            expected_observed={"online"},
            timeout_seconds=90,
        )
        evidence("heartbeat_recovery_observed", observed_health=recovered)

    rotated = lifecycle(
        config,
        csrf_token=csrf_token,
        agent_id=agent_id,
        suffix="/credentials/rotate",
    )
    rotated_token = rotated["credential"]["plaintext_token"]
    evidence("credential_rotated", agent_id=agent_id, new_credential="redacted")

    heartbeat(
        config,
        agent_id=agent_id,
        token=token,
        event_id=f"{slug}-overlap-old",
    )
    heartbeat(
        config,
        agent_id=agent_id,
        token=rotated_token,
        event_id=f"{slug}-overlap-new",
    )
    evidence("rotation_overlap_accepts_old_and_new", agent_id=agent_id)

    lifecycle(config, csrf_token=csrf_token, agent_id=agent_id, suffix="/disconnect")
    rejected = heartbeat(
        config,
        agent_id=agent_id,
        token=rotated_token,
        event_id=f"{slug}-after-disconnect",
        expect_status={401},
    )
    evidence("disconnect_rejects_telemetry", status=rejected["status"])

    reconnected = lifecycle(
        config,
        csrf_token=csrf_token,
        agent_id=agent_id,
        suffix="/reconnect",
    )
    reconnect_token = reconnected["credential"]["plaintext_token"]
    heartbeat(
        config,
        agent_id=agent_id,
        token=reconnect_token,
        event_id=f"{slug}-after-reconnect",
    )
    evidence("reconnect_credential_accepted", agent_id=agent_id)

    lifecycle(config, csrf_token=csrf_token, agent_id=agent_id, suffix="/archive")
    archived_rejected = heartbeat(
        config,
        agent_id=agent_id,
        token=reconnect_token,
        event_id=f"{slug}-after-archive",
        expect_status={401},
    )
    evidence("archive_rejects_telemetry", status=archived_rejected["status"])
    evidence("complete", agent_id=agent_id, tokens="redacted")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"step": "failed", "error": str(error)}), file=sys.stderr)
        raise
