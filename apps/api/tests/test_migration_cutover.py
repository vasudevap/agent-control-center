from __future__ import annotations

import json

from atlas_api.cli import migration_cutover


def test_upgrade_requires_explicit_authority_and_backup_evidence(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    database_path = tmp_path / "atlas_guarded_migration.db"
    monkeypatch.setenv("ATLAS_API_DATABASE_URL", f"sqlite:///{database_path}")

    exit_code = migration_cutover.main(["--mode", "upgrade"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "--confirm-hosted-migration" in captured.err
    assert "sqlite:///" not in captured.out
    assert "sqlite:///" not in captured.err


def test_upgrade_outputs_sanitized_evidence_and_reaches_head(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    database_path = tmp_path / "atlas_upgrade_migration.db"
    database_url = f"sqlite:///{database_path}"
    monkeypatch.setenv("ATLAS_API_DATABASE_URL", database_url)
    monkeypatch.setenv("ATLAS_API_ENVIRONMENT", "test")

    exit_code = migration_cutover.main(
        [
            "--mode",
            "upgrade",
            "--confirm-hosted-migration",
            "--authority-ticket",
            "WO-057-maintainer-approval",
            "--backup-evidence-id",
            "render-recovery-export-confirmed",
            "--require-current-head",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out.strip().splitlines()[-1])

    assert exit_code == 0
    assert payload["database_url_configured"] is True
    assert payload["environment"] == "test"
    assert payload["migration_required_before"] is True
    assert payload["repository_head"] == "0018_agent_visibility_lifecycle_mvp"
    assert payload["revision_after"] == payload["repository_head"]
    assert payload["upgrade_performed"] is True
    assert payload["authority_ticket"] == "WO-057-maintainer-approval"
    assert payload["backup_evidence_id"] == "render-recovery-export-confirmed"
    assert database_url not in captured.out
    assert database_url not in captured.err


def test_evidence_labels_reject_url_like_values(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    database_path = tmp_path / "atlas_bad_label_migration.db"
    monkeypatch.setenv("ATLAS_API_DATABASE_URL", f"sqlite:///{database_path}")

    exit_code = migration_cutover.main(
        [
            "--mode",
            "upgrade",
            "--confirm-hosted-migration",
            "--authority-ticket",
            "WO-057-maintainer-approval",
            "--backup-evidence-id",
            "https://example.com/raw-backup",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "must not contain URLs" in captured.err


def test_check_mode_rejects_unsafe_optional_evidence_labels(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    database_path = tmp_path / "atlas_bad_check_label_migration.db"
    monkeypatch.setenv("ATLAS_API_DATABASE_URL", f"sqlite:///{database_path}")

    exit_code = migration_cutover.main(
        [
            "--mode",
            "check",
            "--authority-ticket",
            "operator@example.com",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "must not contain URLs" in captured.err
    assert "operator@example.com" not in captured.out
