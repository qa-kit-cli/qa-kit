"""Preset manifests, registry, manager, resolver, and composition engine."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

from qa_kit_cli._assets import get_bundled_presets_dir
from qa_kit_cli._github_http import download_file
from qa_kit_cli._utils import load_json, save_json

_STATE_FILE = "presets.json"


@dataclass
class PresetManifest:
    id: str
    name: str
    version: str
    description: str
    compositions: list[dict[str, Any]]

    @classmethod
    def load_from_dir(cls, preset_dir: Path) -> PresetManifest:
        data = yaml.safe_load((preset_dir / "preset.yml").read_text(encoding="utf-8"))
        return cls(
            id=str(data.get("id", preset_dir.name)),
            name=str(data.get("name", preset_dir.name)),
            version=str(data.get("version", "0.0.0")),
            description=str(data.get("description", "")),
            compositions=list(data.get("compositions", [])),
        )


@dataclass
class ActivePreset:
    """A resolved, enabled preset with its local directory for template access."""

    manifest: PresetManifest
    local_dir: Path

    def get_composition(self, command_id: str) -> dict[str, Any] | None:
        """Return the composition entry for command_id, or None if this preset doesn't override it."""
        for comp in self.manifest.compositions:
            if comp.get("command") == command_id:
                return comp
        return None

    def read_template(self, template_name: str) -> str | None:
        """Return override template content, or None if the file doesn't exist."""
        path = self.local_dir / "templates" / "commands" / template_name
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None


def load_active_presets(qakit_dir: Path) -> list[ActivePreset]:
    """Return enabled presets sorted by priority (lowest number = highest priority)."""
    data = load_json(qakit_dir / _STATE_FILE)
    entries: list[dict[str, Any]] = data.get("presets", []) if data else []
    enabled = [e for e in entries if e.get("enabled", True)]
    sorted_entries = sorted(enabled, key=lambda x: int(x.get("priority", 100)))

    active: list[ActivePreset] = []
    local_dir = qakit_dir / "presets"
    for entry in sorted_entries:
        preset_id = str(entry.get("id", ""))
        preset_path = local_dir / preset_id
        manifest_file = preset_path / "preset.yml"
        if manifest_file.exists():
            manifest = PresetManifest.load_from_dir(preset_path)
            active.append(ActivePreset(manifest=manifest, local_dir=preset_path))
    return active


class PresetRegistry:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.bundled_dir = get_bundled_presets_dir()
        self.local_dir = project_root / ".qakit" / "presets"

    def resolve(self, preset_ref: str) -> Path:
        if preset_ref.startswith("https://"):
            return self._resolve_remote(preset_ref)
        maybe = Path(preset_ref)
        if maybe.exists() and maybe.is_dir():
            return maybe
        bundled = self.bundled_dir / preset_ref
        if bundled.exists() and bundled.is_dir():
            return bundled
        local = self.local_dir / preset_ref
        if local.exists() and local.is_dir():
            return local
        raise FileNotFoundError(f"Preset not found: {preset_ref}")

    def _resolve_remote(self, url: str) -> Path:
        tmp_dir = Path(tempfile.mkdtemp(prefix="qakit-preset-"))
        archive = tmp_dir / "preset.zip"
        download_file(url, archive)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(tmp_dir)
        candidates = [p for p in tmp_dir.rglob("preset.yml")]
        if not candidates:
            raise FileNotFoundError("Remote preset archive does not contain preset.yml")
        return candidates[0].parent

    def list_bundled(self) -> list[str]:
        if not self.bundled_dir.exists():
            return []
        return sorted(p.name for p in self.bundled_dir.iterdir() if p.is_dir())


class PresetResolver:
    """Priority resolver for active presets."""

    @staticmethod
    def sort_active(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        enabled = [e for e in entries if e.get("enabled", True)]
        return sorted(enabled, key=lambda x: int(x.get("priority", 100)))


class PresetManager:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.qakit_dir = project_root / ".qakit"
        self.registry = PresetRegistry(project_root)
        self.state_path = self.qakit_dir / _STATE_FILE
        self.local_dir = self.qakit_dir / "presets"
        self.local_dir.mkdir(parents=True, exist_ok=True)

    def _state(self) -> dict[str, Any]:
        data = cast(dict[str, Any], load_json(self.state_path))
        if not data:
            return {"presets": []}
        data.setdefault("presets", [])
        return data

    def _save(self, data: dict[str, Any]) -> None:
        save_json(self.state_path, data)

    def list(self) -> list[dict[str, Any]]:
        return list(self._state().get("presets", []))

    def add(self, preset_ref: str, priority: int = 10) -> dict[str, Any]:
        src = self.registry.resolve(preset_ref)
        manifest = PresetManifest.load_from_dir(src)
        dst = self.local_dir / manifest.id
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        data = self._state()
        presets: list[dict[str, Any]] = [
            p for p in cast(list[dict[str, Any]], data["presets"]) if p.get("id") != manifest.id
        ]
        presets.append(
            {
                "id": manifest.id,
                "name": manifest.name,
                "version": manifest.version,
                "source": str(src),
                "enabled": True,
                "priority": priority,
            }
        )
        data["presets"] = presets
        self._save(data)
        return presets[-1]

    def remove(self, preset_id: str) -> bool:
        data = self._state()
        before = len(data["presets"])
        data["presets"] = [p for p in data["presets"] if p.get("id") != preset_id]
        self._save(data)
        target = self.local_dir / preset_id
        if target.exists():
            shutil.rmtree(target)
        return len(data["presets"]) != before

    def set_priority(self, preset_id: str, priority: int) -> bool:
        data = self._state()
        changed = False
        for preset in data["presets"]:
            if preset.get("id") == preset_id:
                preset["priority"] = priority
                changed = True
        self._save(data)
        return changed

    def set_enabled(self, preset_id: str, enabled: bool) -> bool:
        data = self._state()
        changed = False
        for preset in data["presets"]:
            if preset.get("id") == preset_id:
                preset["enabled"] = enabled
                changed = True
        self._save(data)
        return changed
