"""Extension manifests, registry, manager, and lifecycle hook execution."""

from __future__ import annotations

import filecmp
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from qa_kit_cli._assets import get_bundled_extensions_dir
from qa_kit_cli._github_http import download_file
from qa_kit_cli._utils import load_json, save_json

_STATE_FILE = "extensions.json"
HOOK_EVENTS: tuple[str, ...] = (
    "before_strategy",
    "after_strategy",
    "before_testplan",
    "after_testplan",
    "before_coverage",
    "after_coverage",
    "before_gaps",
    "after_gaps",
    "before_policy",
    "after_policy",
    "before_write_playwright",
    "after_write_playwright",
    "before_write_cypress",
    "after_write_cypress",
    "before_write_jest",
    "after_write_jest",
    "before_write_vitest",
    "after_write_vitest",
    "before_write_pom",
    "after_write_pom",
    "before_ci_github_actions",
    "after_ci_github_actions",
    "before_ci_jenkins",
    "after_ci_jenkins",
    "before_maintain_flaky",
    "after_maintain_flaky",
    "before_review_pr",
    "after_review_pr",
    "before_review_bugreport",
    "after_review_bugreport",
    "before_tasks",
    "after_tasks",
    "before_checklist",
    "after_checklist",
    "before_traceability",
    "after_traceability",
    "before_regression",
    "after_regression",
    "before_defects",
    "after_defects",
    "before_release_gate",
    "after_release_gate",
    "before_env",
    "after_env",
)


@dataclass
class ExtensionManifest:
    id: str
    name: str
    version: str
    description: str
    hooks: list[str]
    commands: dict[str, str]

    @classmethod
    def load_from_dir(cls, extension_dir: Path) -> "ExtensionManifest":
        data = yaml.safe_load((extension_dir / "extension.yml").read_text(encoding="utf-8"))
        hooks = [str(h) for h in data.get("hooks", [])]
        invalid = [h for h in hooks if h not in HOOK_EVENTS]
        if invalid:
            raise ValueError(f"Unsupported hook events in {extension_dir}: {', '.join(invalid)}")
        return cls(
            id=str(data.get("id", extension_dir.name)),
            name=str(data.get("name", extension_dir.name)),
            version=str(data.get("version", "0.0.0")),
            description=str(data.get("description", "")),
            hooks=hooks,
            commands=dict(data.get("commands", {})),
        )


class ExtensionRegistry:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.bundled_dir = get_bundled_extensions_dir()
        self.local_dir = project_root / ".qakit" / "extensions"

    def list_bundled(self) -> list[str]:
        if not self.bundled_dir.exists():
            return []
        return sorted(p.name for p in self.bundled_dir.iterdir() if p.is_dir())

    def resolve(self, extension_ref: str) -> Path:
        if extension_ref.startswith("https://"):
            return self._resolve_remote(extension_ref)
        maybe = Path(extension_ref)
        if maybe.exists() and maybe.is_dir():
            return maybe
        bundled = self.bundled_dir / extension_ref
        if bundled.exists() and bundled.is_dir():
            return bundled
        local = self.local_dir / extension_ref
        if local.exists() and local.is_dir():
            return local
        raise FileNotFoundError(f"Extension not found: {extension_ref}")

    def _resolve_remote(self, url: str) -> Path:
        tmp_dir = Path(tempfile.mkdtemp(prefix="qakit-extension-"))
        archive = tmp_dir / "extension.zip"
        download_file(url, archive)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(tmp_dir)
        candidates = [p for p in tmp_dir.rglob("extension.yml")]
        if not candidates:
            raise FileNotFoundError("Remote extension archive does not contain extension.yml")
        return candidates[0].parent


class HookExecutor:
    """Executes extension hook commands when defined."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def execute(self, manifests: list[ExtensionManifest], event: str) -> list[tuple[str, int]]:
        results: list[tuple[str, int]] = []
        for manifest in manifests:
            command = manifest.commands.get(event)
            if not command:
                continue
            rc = subprocess.call(command, cwd=self.project_root, shell=True)
            results.append((manifest.id, rc))
        return results


class ExtensionManager:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.qakit_dir = project_root / ".qakit"
        self.registry = ExtensionRegistry(project_root)
        self.state_path = self.qakit_dir / _STATE_FILE
        self.local_dir = self.qakit_dir / "extensions"
        self.local_dir.mkdir(parents=True, exist_ok=True)

    def _state(self) -> dict[str, Any]:
        data = load_json(self.state_path)
        if not data:
            return {"extensions": []}
        data.setdefault("extensions", [])
        return data

    def _save(self, data: dict[str, Any]) -> None:
        save_json(self.state_path, data)

    def list(self) -> list[dict[str, Any]]:
        return list(self._state().get("extensions", []))

    def add(self, extension_ref: str, priority: int = 10) -> dict[str, Any]:
        import datetime

        src = self.registry.resolve(extension_ref)
        manifest = ExtensionManifest.load_from_dir(src)
        dst = self.local_dir / manifest.id
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        data = self._state()
        extensions = [e for e in data["extensions"] if e.get("id") != manifest.id]
        extensions.append({
            "id": manifest.id,
            "name": manifest.name,
            "version": manifest.version,
            "priority": priority,
            "enabled": True,
            "source": str(src),
            "installed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })
        data["extensions"] = extensions
        self._save(data)
        return extensions[-1]

    def _find_entry(self, extension_id: str) -> dict[str, Any] | None:
        for entry in self.list():
            if str(entry.get("id", "")) == extension_id:
                return entry
        return None

    def update(self, extension_id: str, force: bool = False) -> dict[str, Any]:
        """Update an installed extension from its current registry source."""
        entry = self._find_entry(extension_id)
        if entry is None:
            raise FileNotFoundError(f"Extension '{extension_id}' is not installed.")

        src = self.registry.resolve(extension_id)
        new_manifest = ExtensionManifest.load_from_dir(src)
        dst = self.local_dir / extension_id
        old_manifest = ExtensionManifest.load_from_dir(dst) if (dst / "extension.yml").exists() else new_manifest
        old_source = Path(str(entry.get("source", ""))) if entry.get("source") else None

        if new_manifest.version == old_manifest.version:
            return {
                "id": extension_id,
                "old_version": old_manifest.version,
                "new_version": new_manifest.version,
                "updated_templates": 0,
                "already_latest": True,
            }

        preserved_files: list[tuple[Path, bytes]] = []
        preserved_templates: dict[Path, bytes] = {}
        template_updates = 0

        if dst.exists():
            # Preserve non-template files (config, local metadata) always.
            for path in dst.rglob("*"):
                if not path.is_file():
                    continue
                rel = path.relative_to(dst)
                if rel.parts[:2] == ("templates", "commands") or rel == Path("extension.yml"):
                    continue
                preserved_files.append((rel, path.read_bytes()))

            current_templates_dir = dst / "templates" / "commands"
            new_templates_dir = src / "templates" / "commands"
            old_templates_dir = (old_source / "templates" / "commands") if old_source else None

            if new_templates_dir.exists():
                for new_tpl in new_templates_dir.rglob("*"):
                    if not new_tpl.is_file():
                        continue
                    rel = new_tpl.relative_to(new_templates_dir)
                    current_tpl = current_templates_dir / rel
                    if not current_tpl.exists() or not filecmp.cmp(new_tpl, current_tpl, shallow=False):
                        template_updates += 1

                    if force:
                        continue

                    if not current_tpl.exists() or old_templates_dir is None:
                        continue

                    old_tpl = old_templates_dir / rel
                    if old_tpl.exists() and not filecmp.cmp(current_tpl, old_tpl, shallow=False):
                        preserved_templates[rel] = current_tpl.read_bytes()

        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        # Restore preserved template edits when not forcing.
        if not force and preserved_templates:
            for rel, content in preserved_templates.items():
                target = dst / "templates" / "commands" / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)

        # Restore preserved config files.
        for rel, content in preserved_files:
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

        data = self._state()
        updated_entries: list[dict[str, Any]] = []
        for existing in data.get("extensions", []):
            if str(existing.get("id", "")) != extension_id:
                updated_entries.append(existing)
                continue
            updated = dict(existing)
            updated["name"] = new_manifest.name
            updated["version"] = new_manifest.version
            updated["source"] = str(src)
            updated_entries.append(updated)
        data["extensions"] = updated_entries
        self._save(data)

        return {
            "id": extension_id,
            "old_version": old_manifest.version,
            "new_version": new_manifest.version,
            "updated_templates": template_updates,
            "already_latest": False,
        }

    def remove(self, extension_id: str, keep_config: bool = False, force: bool = False) -> bool:
        """Remove an extension.

        keep_config: leave config files in place.
        force: skip confirmation and remove managed files without backup.
        """
        data = self._state()
        before = len(data["extensions"])
        data["extensions"] = [e for e in data["extensions"] if e.get("id") != extension_id]
        self._save(data)
        target = self.local_dir / extension_id
        if target.exists() and not keep_config:
            shutil.rmtree(target)
        elif target.exists() and keep_config:
            backup = self.local_dir / f"{extension_id}.bak"
            if backup.exists():
                shutil.rmtree(backup)
            shutil.copytree(target, backup)
            shutil.rmtree(target)
        return len(data["extensions"]) != before

    def set_enabled(self, extension_id: str, enabled: bool) -> bool:
        data = self._state()
        changed = False
        for extension in data["extensions"]:
            if extension.get("id") == extension_id:
                extension["enabled"] = enabled
                changed = True
        self._save(data)
        return changed

    def set_priority(self, extension_id: str, priority: int) -> bool:
        data = self._state()
        changed = False
        for extension in data["extensions"]:
            if extension.get("id") == extension_id:
                extension["priority"] = priority
                changed = True
        self._save(data)
        return changed

    def active_manifests(self) -> list[ExtensionManifest]:
        manifests: list[ExtensionManifest] = []
        for ext in self.list():
            if not ext.get("enabled", True):
                continue
            path = self.local_dir / str(ext.get("id"))
            manifest_file = path / "extension.yml"
            if manifest_file.exists():
                manifests.append(ExtensionManifest.load_from_dir(path))
        return manifests
