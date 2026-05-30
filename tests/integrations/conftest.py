"""Shared fixtures for per-integration tests."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """A temporary project root directory."""
    return tmp_path


@pytest.fixture
def qakit_dir(project_root: Path) -> Path:
    d = project_root / ".qakit"
    d.mkdir(parents=True, exist_ok=True)
    return d
