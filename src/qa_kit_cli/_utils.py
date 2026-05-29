"""Utility helpers shared across the CLI."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_command(
    cmd: list[str],
    cwd: Path | None = None,
    capture: bool = True,
) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
    )
    return result.returncode, result.stdout or "", result.stderr or ""


def is_git_repo(path: Path) -> bool:
    """Return True if path is inside a git repository."""
    code, _, _ = run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=path)
    return code == 0


def find_project_root(start: Path | None = None) -> Path | None:
    """Walk up from start (default: cwd) looking for a .qakit/ directory."""
    current = (start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        if (directory / ".qakit").is_dir():
            return directory
    return None


def merge_json(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge two dicts; override wins on scalar conflicts."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json(result[key], value)
        else:
            result[key] = value
    return result


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    """Return the SHA-256 hex digest of a string."""
    return hashlib.sha256(text.encode()).hexdigest()


def atomic_write(path: Path, content: str) -> None:
    """Write content to path atomically via a uniquely-named temp file.

    Uses a unique suffix per call so concurrent writers (e.g. parallel workflow steps)
    each have their own temp file and don't race each other on Windows.
    """
    import uuid
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def load_json(path: Path) -> Any:
    """Load JSON from path, returning {} if missing or invalid."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_json(path: Path, data: Any, indent: int = 2) -> None:
    """Serialize data to JSON and write atomically."""
    atomic_write(path, json.dumps(data, indent=indent) + "\n")


def is_windows() -> bool:
    return sys.platform == "win32"


def get_qakit_dir(project_root: Path) -> Path:
    """Return the .qakit/ state directory for a project."""
    return project_root / ".qakit"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def platform_script_ext() -> str:
    return ".ps1" if is_windows() else ".sh"


def env_or(key: str, default: str) -> str:
    return os.environ.get(key, default)
