"""SHA-256 hash manifest for tracking installed command files (safe uninstall)."""

from __future__ import annotations

from pathlib import Path

from qa_kit_cli._utils import load_json, save_json, sha256_file

_MANIFEST_DIR = "integrations"


def _manifest_path(qakit_dir: Path, integration_key: str) -> Path:
    return qakit_dir / _MANIFEST_DIR / f"{integration_key}.manifest.json"


def record_files(qakit_dir: Path, integration_key: str, files: list[Path]) -> None:
    """Record SHA-256 hashes of installed files for a given integration."""
    data = {str(f): sha256_file(f) for f in files if f.exists()}
    save_json(_manifest_path(qakit_dir, integration_key), data)


def get_recorded_files(qakit_dir: Path, integration_key: str) -> dict[str, str]:
    """Return {path_str: sha256} for files recorded under integration_key."""
    return load_json(_manifest_path(qakit_dir, integration_key))


def get_modified_files(qakit_dir: Path, integration_key: str) -> list[Path]:
    """Return paths of installed files that have been locally modified."""
    manifest = get_recorded_files(qakit_dir, integration_key)
    return [
        Path(path_str)
        for path_str, recorded_hash in manifest.items()
        if Path(path_str).exists() and sha256_file(Path(path_str)) != recorded_hash
    ]


def uninstall_files(
    qakit_dir: Path,
    integration_key: str,
    force: bool = False,
) -> tuple[list[Path], list[Path]]:
    """Remove installed files, preserving locally-modified ones unless force=True.

    Returns (removed, skipped).
    """
    manifest = get_recorded_files(qakit_dir, integration_key)
    removed: list[Path] = []
    skipped: list[Path] = []
    for path_str, recorded_hash in manifest.items():
        p = Path(path_str)
        if not p.exists():
            continue
        if sha256_file(p) == recorded_hash or force:
            p.unlink()
            removed.append(p)
        else:
            skipped.append(p)
    _manifest_path(qakit_dir, integration_key).unlink(missing_ok=True)
    return removed, skipped
