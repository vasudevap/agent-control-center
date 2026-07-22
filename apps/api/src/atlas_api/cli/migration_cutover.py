from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from alembic import command
from atlas_api.core.config import Settings
from atlas_api.db.config import require_database_url

API_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class MigrationEvidence:
    checked_at: str
    environment: str
    database_url_configured: bool
    mode: str
    repository_head: str
    revision_before: str | None
    revision_after: str | None
    migration_required_before: bool
    upgrade_performed: bool
    authority_ticket: str | None
    backup_evidence_id: str | None


def build_alembic_config() -> Config:
    config = Config(str(API_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(API_ROOT / "alembic"))
    return config


def repository_head(config: Config) -> str:
    heads = ScriptDirectory.from_config(config).get_heads()
    if len(heads) != 1:
        joined_heads = ", ".join(heads) if heads else "none"
        raise RuntimeError(f"Expected exactly one Alembic head; found {joined_heads}.")
    return heads[0]


def current_revision(engine: Engine) -> str | None:
    from alembic.runtime.migration import MigrationContext

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        return context.get_current_revision()


def validate_evidence_id(name: str, value: str) -> None:
    if not value.strip():
        raise RuntimeError(f"{name} must not be empty.")
    if len(value) > 120:
        raise RuntimeError(f"{name} must be a short evidence label, not raw output.")
    if "://" in value or "@" in value:
        raise RuntimeError(f"{name} must not contain URLs, credentials, or emails.")


def require_upgrade_authority(args: argparse.Namespace) -> None:
    if not args.confirm_hosted_migration:
        raise RuntimeError(
            "Hosted migration upgrade requires --confirm-hosted-migration."
        )
    if args.authority_ticket is None:
        raise RuntimeError("Hosted migration upgrade requires --authority-ticket.")
    if args.backup_evidence_id is None:
        raise RuntimeError("Hosted migration upgrade requires --backup-evidence-id.")


def validate_optional_evidence_labels(args: argparse.Namespace) -> None:
    if args.authority_ticket is not None:
        validate_evidence_id("authority-ticket", args.authority_ticket)
    if args.backup_evidence_id is not None:
        validate_evidence_id("backup-evidence-id", args.backup_evidence_id)


def validate_requested_operation(args: argparse.Namespace) -> None:
    if args.mode == "upgrade":
        require_upgrade_authority(args)
    validate_optional_evidence_labels(args)


def evidence_payload(
    *,
    settings: Settings,
    mode: str,
    head: str,
    revision_before: str | None,
    revision_after: str | None,
    upgrade_performed: bool,
    authority_ticket: str | None,
    backup_evidence_id: str | None,
) -> MigrationEvidence:
    return MigrationEvidence(
        checked_at=datetime.now(UTC).replace(microsecond=0).isoformat(),
        environment=settings.environment,
        database_url_configured=settings.database_url is not None,
        mode=mode,
        repository_head=head,
        revision_before=revision_before,
        revision_after=revision_after,
        migration_required_before=revision_before != head,
        upgrade_performed=upgrade_performed,
        authority_ticket=authority_ticket,
        backup_evidence_id=backup_evidence_id,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Collect sanitized Atlas Alembic migration evidence and, when "
            "explicitly authorized, upgrade the configured database to head."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("check", "upgrade"),
        default="check",
        help="Use check for read-only evidence; upgrade applies Alembic head.",
    )
    parser.add_argument(
        "--confirm-hosted-migration",
        action="store_true",
        help="Required with --mode upgrade to acknowledge hosted migration authority.",
    )
    parser.add_argument(
        "--authority-ticket",
        help="Short non-secret Work Order or approval evidence label.",
    )
    parser.add_argument(
        "--backup-evidence-id",
        help="Short non-secret Render recovery/export evidence label.",
    )
    parser.add_argument(
        "--require-current-head",
        action="store_true",
        help="Exit non-zero unless the final database revision equals repository head.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    engine: Engine | None = None

    try:
        args = parse_args(argv)
        validate_requested_operation(args)
        settings = Settings()
        config = build_alembic_config()
        head = repository_head(config)
        engine = create_engine(require_database_url(settings))

        before = current_revision(engine)
        upgrade_performed = False

        if args.mode == "upgrade":
            command.upgrade(config, "head")
            upgrade_performed = True

        after = current_revision(engine)
        evidence = evidence_payload(
            settings=settings,
            mode=args.mode,
            head=head,
            revision_before=before,
            revision_after=after,
            upgrade_performed=upgrade_performed,
            authority_ticket=args.authority_ticket,
            backup_evidence_id=args.backup_evidence_id,
        )
        print(json.dumps(asdict(evidence), sort_keys=True))

        if args.require_current_head and after != head:
            print(
                "Configured database is not at the repository Alembic head.",
                file=sys.stderr,
            )
            return 2
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    finally:
        if engine is not None:
            engine.dispose()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
