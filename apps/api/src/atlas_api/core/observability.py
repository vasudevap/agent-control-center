from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, Literal

from atlas_api.core.correlation import get_correlation_id

SafeValue = str | int | bool | None
LogSeverity = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

REDACTED = "[redacted]"
MAX_SAFE_VALUE_LENGTH = 240
DENIED_KEY_PARTS = (
    "authorization",
    "body",
    "cookie",
    "password",
    "secret",
    "signature",
    "token",
)
ALLOWED_METADATA_KEYS = frozenset(
    {
        "actor_id",
        "actor_type",
        "attempt_count",
        "channel",
        "component",
        "correlation_id",
        "error_code",
        "event_id",
        "event_type",
        "external_client_id",
        "job_id",
        "job_type",
        "key_id",
        "nonce_status",
        "operation_id",
        "outcome",
        "queue_job_id",
        "reason_code",
        "resource_id",
        "resource_reference",
        "resource_type",
        "result",
        "run_id",
        "schedule_id",
        "scheduled_for",
        "skipped_count",
        "state",
        "status",
        "webhook_delivery_attempt_id",
        "webhook_subscription_id",
        "worker_id",
    }
)


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sanitize_metadata(metadata: Mapping[str, Any] | None) -> dict[str, SafeValue]:
    if not metadata:
        return {}
    sanitized: dict[str, SafeValue] = {}
    for key, value in metadata.items():
        if key not in ALLOWED_METADATA_KEYS:
            continue
        lowered = key.lower()
        if any(part in lowered for part in DENIED_KEY_PARTS):
            sanitized[key] = REDACTED
            continue
        safe_value = _safe_value(value)
        if safe_value is not None or value is None:
            sanitized[key] = safe_value
    return sanitized


def _safe_value(value: Any) -> SafeValue:
    if value is None or isinstance(value, bool | int):
        return value
    if isinstance(value, str):
        if len(value) > MAX_SAFE_VALUE_LENGTH:
            return value[:MAX_SAFE_VALUE_LENGTH] + "..."
        return value
    return None


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        metadata = sanitize_metadata(getattr(record, "metadata", None))
        payload: dict[str, SafeValue] = {
            "timestamp": utc_timestamp(),
            "severity": record.levelname,
            "component": _record_value(record, "component", record.name),
            "event_type": _record_value(record, "event_type", "log_event"),
            "correlation_id": _record_value(
                record,
                "correlation_id",
                get_correlation_id() or "correlation_unavailable",
            ),
            "message": record.getMessage(),
        }
        payload.update(metadata)
        if record.exc_info and record.exc_info[0] is not None:
            payload["error_code"] = record.exc_info[0].__name__
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _record_value(
    record: logging.LogRecord, attribute: str, default: str
) -> SafeValue:
    value = getattr(record, attribute, default)
    safe = _safe_value(value)
    return safe if safe is not None else default


def configure_json_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(level)


def log_event(
    logger: logging.Logger,
    *,
    severity: LogSeverity = "INFO",
    component: str,
    event_type: str,
    message: str,
    correlation_id: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> None:
    logger.log(
        logging.getLevelName(severity),
        message,
        extra={
            "component": component,
            "event_type": event_type,
            "correlation_id": correlation_id or get_correlation_id(),
            "metadata": sanitize_metadata(metadata),
        },
    )
