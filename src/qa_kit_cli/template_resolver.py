"""Runtime template resolver with layered override stack.

Resolution order (first match wins):
  1. Project-local overrides  (.qakit/templates/overrides/)
  2. Installed enabled presets (.qakit/presets/<id>/templates/commands/)  by priority
  3. Installed enabled extensions (.qakit/extensions/<id>/templates/commands/)  by priority
  4. Core defaults             (bundled templates/commands/)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qa_kit_cli._assets import get_commands_dir
from qa_kit_cli._utils import load_json
from qa_kit_cli.presets import load_active_presets

_EXTENSIONS_STATE_FILE = "extensions.json"


def _load_active_extensions(qakit_dir: Path) -> list[tuple[str, Path]]:
    """Return (id, local_dir) for enabled extensions sorted by priority asc."""
    data = load_json(qakit_dir / _EXTENSIONS_STATE_FILE)
    entries: list[dict[str, Any]] = data.get("extensions", []) if data else []
    enabled = [e for e in entries if e.get("enabled", True)]
    sorted_entries = sorted(enabled, key=lambda x: int(x.get("priority", 10)))
    result: list[tuple[str, Path]] = []
    local_dir = qakit_dir / "extensions"
    for entry in sorted_entries:
        ext_id = str(entry.get("id", ""))
        ext_path = local_dir / ext_id
        if ext_path.exists():
            result.append((ext_id, ext_path))
    return result


class TemplateResolver:
    def __init__(self, qakit_dir: Path, core_commands_dir: Path | None = None) -> None:
        self.qakit_dir = qakit_dir
        self.core_dir = core_commands_dir or get_commands_dir()
        self.overrides_dir = qakit_dir / "templates" / "overrides"
        self._presets = load_active_presets(qakit_dir)
        self._extensions = _load_active_extensions(qakit_dir)

    def resolve(self, template_name: str) -> Path | None:
        """Return the winning Path for template_name, or None if not found."""
        override = self.overrides_dir / template_name
        if override.exists():
            return override

        for preset in self._presets:
            candidate = preset.local_dir / "templates" / "commands" / template_name
            if candidate.exists():
                return candidate

        for _ext_id, ext_path in self._extensions:
            candidate = ext_path / "templates" / "commands" / template_name
            if candidate.exists():
                return candidate

        core = self.core_dir / template_name
        if core.exists():
            return core

        return None

    def resolve_stack(self, template_name: str) -> list[tuple[str, Path, bool]]:
        """Return the full stack as [(layer, path, wins)] ordered by priority."""
        stack: list[tuple[str, Path, bool]] = []

        override = self.overrides_dir / template_name
        if override.exists():
            stack.append(("override", override, False))

        for preset in self._presets:
            candidate = preset.local_dir / "templates" / "commands" / template_name
            if candidate.exists():
                stack.append((f"preset:{preset.manifest.id}", candidate, False))

        for ext_id, ext_path in self._extensions:
            candidate = ext_path / "templates" / "commands" / template_name
            if candidate.exists():
                stack.append((f"extension:{ext_id}", candidate, False))

        core = self.core_dir / template_name
        if core.exists():
            stack.append(("core", core, False))

        if stack:
            layer, path, _ = stack[0]
            stack[0] = (layer, path, True)

        return stack
