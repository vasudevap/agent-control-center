from __future__ import annotations

import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REFERENCE_CLIENT_ROOT = (
    REPOSITORY_ROOT / "docs" / "references" / "agent-visibility-reference-clients"
)
REFERENCE_CLIENTS = [
    REFERENCE_CLIENT_ROOT / "curl" / "agent-visibility-reference-client.sh",
    REFERENCE_CLIENT_ROOT / "python" / "agent_visibility_reference_client.py",
    REFERENCE_CLIENT_ROOT / "typescript" / "agent-visibility-reference-client.ts",
]
SECRET_LITERAL_PATTERN = re.compile(
    r"(sk-[A-Za-z0-9]{12,}|ntn_[A-Za-z0-9]{8,}|BEGIN PRIVATE KEY)"
)


def test_wo071_reference_clients_are_present_and_standalone() -> None:
    for client_path in REFERENCE_CLIENTS:
        assert client_path.exists(), f"{client_path} is missing"
        source = client_path.read_text(encoding="utf-8")
        assert "atlas_api" not in source
        assert "@/app" not in source
        assert "@/lib" not in source
        assert not SECRET_LITERAL_PATTERN.search(source)


def test_wo071_reference_clients_document_secret_safe_inputs() -> None:
    readme = (REFERENCE_CLIENT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "ATLAS_OWNER_SESSION_COOKIE" in readme
    assert "Do not paste" in readme
    assert "redacted evidence" in readme
