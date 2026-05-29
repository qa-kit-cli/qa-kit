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


def uninstall_files(qakit_dir: Path, integration_key: str) -> list[Path]:
    """
    Remove files that were installed by this integration and whose content
    hasn't changed since installation. Returns list of removed paths.
    """
    manifest = get_recorded_files(qakit_dir, integration_key)
    removed: list[Path] = []
    for path_str, recorded_hash in manifest.items():
        p = Path(path_str)
        if p.exists() and sha256_file(p) == recorded_hash:
            p.unlink()
            removed.append(p)
    manifest_file = _manifest_path(qakit_dir, integration_key)
    manifest_file.unlink(missing_ok=True)
    return removed
