from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[mK]")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from a string for clean output assertions."""
    return _ANSI_ESCAPE.sub("", text)


@pytest.fixture
def project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def qakit_dir(project_dir: Path) -> Path:
    from qa_kit_cli.shared_infra import ensure_project_layout
    return ensure_project_layout(project_dir)
