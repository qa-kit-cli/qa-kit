"""Runtime template resolver with layered override stack.

Resolution order (first match wins):
  1. Project-local overrides  (.qakit/templates/overrides/)
  2. Installed presets         (.qakit/presets/<id>/templates/commands/)  by priority
  3. Core defaults             (bundled templates/commands/)
"""

from __future__ import annotations

from pathlib import Path

from qa_kit_cli._assets import get_commands_dir
from qa_kit_cli.presets import load_active_presets


class TemplateResolver:
    def __init__(self, qakit_dir: Path, core_commands_dir: Path | None = None) -> None:
        self.qakit_dir = qakit_dir
        self.core_dir = core_commands_dir or get_commands_dir()
        self.overrides_dir = qakit_dir / "templates" / "overrides"
        self._presets = load_active_presets(qakit_dir)

    def resolve(self, template_name: str) -> Path | None:
        """Return the winning Path for template_name, or None if not found."""
        override = self.overrides_dir / template_name
        if override.exists():
            return override

        for preset in self._presets:
            candidate = preset.local_dir / "templates" / "commands" / template_name
            if candidate.exists():
                return candidate

        core = self.core_dir / template_name
        if core.exists():
            return core

        return None

    def resolve_stack(self, template_name: str) -> list[tuple[str, Path, bool]]:
        """Return the full stack as [(layer, path, wins)] for the `preset resolve` command."""
        stack: list[tuple[str, Path, bool]] = []

        override = self.overrides_dir / template_name
        if override.exists():
            stack.append(("override", override, False))

        for preset in self._presets:
            candidate = preset.local_dir / "templates" / "commands" / template_name
            if candidate.exists():
                stack.append((f"preset:{preset.manifest.id}", candidate, False))

        core = self.core_dir / template_name
        if core.exists():
            stack.append(("core", core, False))

        if stack:
            layer, path, _ = stack[0]
            stack[0] = (layer, path, True)

        return stack
