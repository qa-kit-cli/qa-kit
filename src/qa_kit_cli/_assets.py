"""Locate bundled core_pack assets whether running from source or an installed wheel."""

from __future__ import annotations

from pathlib import Path


def _source_root() -> Path:
    """Return the repository root when running from a source checkout."""
    return Path(__file__).parent.parent.parent


def get_core_pack() -> Path:
    """
    Return the path to core_pack/.
    In a wheel install it lives at qa_kit_cli/core_pack/.
    In a source checkout we fall back to the repo-level directories.
    """
    wheel_pack = Path(__file__).parent / "core_pack"
    if wheel_pack.is_dir():
        return wheel_pack
    return _source_root()


def get_commands_dir() -> Path:
    pack = get_core_pack()
    candidate = pack / "commands"
    if candidate.is_dir():
        return candidate
    return _source_root() / "templates" / "commands"


def get_templates_dir() -> Path:
    pack = get_core_pack()
    candidate = pack / "templates"
    if candidate.is_dir():
        return candidate
    return _source_root() / "templates"


def get_scripts_dir() -> Path:
    pack = get_core_pack()
    candidate = pack / "scripts"
    if candidate.is_dir():
        return candidate
    return _source_root() / "scripts"


def get_bundled_presets_dir() -> Path:
    pack = get_core_pack()
    candidate = pack / "presets"
    if candidate.is_dir():
        return candidate
    return _source_root() / "presets"


def get_bundled_extensions_dir() -> Path:
    pack = get_core_pack()
    candidate = pack / "extensions"
    if candidate.is_dir():
        return candidate
    return _source_root() / "extensions"


def get_bundled_workflows_dir() -> Path:
    pack = get_core_pack()
    candidate = pack / "workflows"
    if candidate.is_dir():
        return candidate
    return _source_root() / "workflows"
