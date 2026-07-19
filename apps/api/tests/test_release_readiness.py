from __future__ import annotations

import json
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_release_readiness_source_contracts_are_present() -> None:
    package_json = json.loads((REPO_ROOT / "package.json").read_text())
    web_package_json = json.loads((REPO_ROOT / "apps/web/package.json").read_text())
    api_pyproject = (REPO_ROOT / "apps/api/pyproject.toml").read_text()
    ci_workflow = (REPO_ROOT / ".github/workflows/ci.yml").read_text()

    assert package_json["workspaces"] == ["apps/*"]
    assert package_json["scripts"]["build"] == "npm --workspace @atlas/web run build"
    assert package_json["scripts"]["lint"] == "npm --workspace @atlas/web run lint"
    assert package_json["scripts"]["typecheck"] == (
        "npm --workspace @atlas/web run typecheck"
    )
    assert web_package_json["scripts"]["build"] == "next build"

    assert 'requires-python = ">=3.12"' in api_pyproject
    assert (
        'atlas-schedule-sweep = "atlas_api.cli.sweep_schedules:main"'
        in api_pyproject
    )
    assert (REPO_ROOT / "apps/api/alembic.ini").is_file()

    assert "image: postgres:18" in ci_workflow
    assert "python -m alembic upgrade head" in ci_workflow
    assert "python -m alembic downgrade base" in ci_workflow
    assert "npm run build" in ci_workflow


def test_release_readiness_provider_files_match_cutover_authority() -> None:
    assert not (REPO_ROOT / "render.yaml").exists()

    netlify_toml = REPO_ROOT / "netlify.toml"
    assert netlify_toml.is_file()

    netlify_config = tomllib.loads(netlify_toml.read_text())
    assert netlify_config["build"] == {
        "base": "apps/web",
        "command": "npm run build",
        "publish": "apps/web/.next",
        "environment": {"NEXT_TELEMETRY_DISABLED": "1"},
    }
    assert netlify_config["plugins"] == [{"package": "@netlify/plugin-nextjs"}]
    assert "NEXT_PUBLIC_API_BASE_URL" not in netlify_toml.read_text()
