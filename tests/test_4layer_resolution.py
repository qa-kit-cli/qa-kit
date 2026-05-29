"""Tests for 4-layer template resolution: overrides → presets → extensions → core."""

from __future__ import annotations

from pathlib import Path

import pytest

from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.template_resolver import TemplateResolver


TEMPLATE = "write.playwright.md"


def _write_template(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _enable_extension(qakit_dir: Path, ext_id: str, priority: int = 10) -> None:
    import json

    state_file = qakit_dir / "extensions.json"
    data: dict = {"extensions": []}
    if state_file.exists():
        data = json.loads(state_file.read_text())
    data["extensions"] = [e for e in data["extensions"] if e.get("id") != ext_id]
    data["extensions"].append({"id": ext_id, "enabled": True, "priority": priority})
    state_file.write_text(json.dumps(data, indent=2))


def _enable_preset(qakit_dir: Path, preset_id: str, priority: int = 10) -> None:
    import json

    # Write minimal preset.yml so load_active_presets() can find it
    preset_dir = qakit_dir / "presets" / preset_id
    preset_dir.mkdir(parents=True, exist_ok=True)
    preset_yml = preset_dir / "preset.yml"
    if not preset_yml.exists():
        preset_yml.write_text(
            f"id: {preset_id}\nname: {preset_id}\nversion: 0.0.1\ndescription: test\n",
            encoding="utf-8",
        )

    state_file = qakit_dir / "presets.json"
    data: dict = {"presets": []}
    if state_file.exists():
        data = json.loads(state_file.read_text())
    data["presets"] = [p for p in data["presets"] if p.get("id") != preset_id]
    data["presets"].append({"id": preset_id, "enabled": True, "priority": priority})
    state_file.write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Layer 4: core wins when nothing else provides a template
# ---------------------------------------------------------------------------

def test_core_layer_resolves_when_nothing_else_present(qakit_dir: Path) -> None:
    resolver = TemplateResolver(qakit_dir)
    result = resolver.resolve(TEMPLATE)
    assert result is not None
    assert result.exists()


# ---------------------------------------------------------------------------
# Layer 3: extension beats core
# ---------------------------------------------------------------------------

def test_extension_beats_core(qakit_dir: Path) -> None:
    ext_id = "my-ext"
    ext_tmpl = qakit_dir / "extensions" / ext_id / "templates" / "commands" / TEMPLATE
    _write_template(ext_tmpl, "EXTENSION CONTENT")
    _enable_extension(qakit_dir, ext_id)

    resolver = TemplateResolver(qakit_dir)
    result = resolver.resolve(TEMPLATE)
    assert result is not None
    assert result.read_text(encoding="utf-8") == "EXTENSION CONTENT"


# ---------------------------------------------------------------------------
# Layer 2: preset beats extension
# ---------------------------------------------------------------------------

def test_preset_beats_extension(qakit_dir: Path) -> None:
    ext_id = "ext-a"
    preset_id = "my-preset"
    ext_tmpl = qakit_dir / "extensions" / ext_id / "templates" / "commands" / TEMPLATE
    preset_tmpl = qakit_dir / "presets" / preset_id / "templates" / "commands" / TEMPLATE
    _write_template(ext_tmpl, "EXT CONTENT")
    _write_template(preset_tmpl, "PRESET CONTENT")
    _enable_extension(qakit_dir, ext_id)
    _enable_preset(qakit_dir, preset_id)

    resolver = TemplateResolver(qakit_dir)
    result = resolver.resolve(TEMPLATE)
    assert result is not None
    assert result.read_text(encoding="utf-8") == "PRESET CONTENT"


# ---------------------------------------------------------------------------
# Layer 1: override beats preset
# ---------------------------------------------------------------------------

def test_override_beats_preset(qakit_dir: Path) -> None:
    preset_id = "my-preset"
    override_tmpl = qakit_dir / "templates" / "overrides" / TEMPLATE
    preset_tmpl = qakit_dir / "presets" / preset_id / "templates" / "commands" / TEMPLATE
    _write_template(override_tmpl, "OVERRIDE CONTENT")
    _write_template(preset_tmpl, "PRESET CONTENT")
    _enable_preset(qakit_dir, preset_id)

    resolver = TemplateResolver(qakit_dir)
    result = resolver.resolve(TEMPLATE)
    assert result is not None
    assert result.read_text(encoding="utf-8") == "OVERRIDE CONTENT"


# ---------------------------------------------------------------------------
# resolve_stack shows all 4 layers
# ---------------------------------------------------------------------------

def test_resolve_stack_includes_extension_layer(qakit_dir: Path) -> None:
    ext_id = "test-ext"
    ext_tmpl = qakit_dir / "extensions" / ext_id / "templates" / "commands" / TEMPLATE
    _write_template(ext_tmpl, "EXT CONTENT")
    _enable_extension(qakit_dir, ext_id)

    resolver = TemplateResolver(qakit_dir)
    stack = resolver.resolve_stack(TEMPLATE)
    layers = [layer for layer, _, _ in stack]
    assert any("extension:" in lyr for lyr in layers)
    assert any(lyr == "core" for lyr in layers)


def test_resolve_stack_first_entry_is_winner(qakit_dir: Path) -> None:
    ext_id = "test-ext-win"
    ext_tmpl = qakit_dir / "extensions" / ext_id / "templates" / "commands" / TEMPLATE
    _write_template(ext_tmpl, "EXT WINS")
    _enable_extension(qakit_dir, ext_id)

    resolver = TemplateResolver(qakit_dir)
    stack = resolver.resolve_stack(TEMPLATE)
    winner_entries = [(l, p, w) for l, p, w in stack if w]
    assert len(winner_entries) == 1
    layer, _, _ = winner_entries[0]
    assert "extension:" in layer


# ---------------------------------------------------------------------------
# Disabled extension is excluded
# ---------------------------------------------------------------------------

def test_disabled_extension_excluded_from_resolution(qakit_dir: Path) -> None:
    import json

    ext_id = "disabled-ext"
    ext_tmpl = qakit_dir / "extensions" / ext_id / "templates" / "commands" / TEMPLATE
    _write_template(ext_tmpl, "DISABLED EXT")
    state_file = qakit_dir / "extensions.json"
    state_file.write_text(
        json.dumps({"extensions": [{"id": ext_id, "enabled": False, "priority": 1}]})
    )

    resolver = TemplateResolver(qakit_dir)
    result = resolver.resolve(TEMPLATE)
    # Should fall back to core, not the disabled extension
    assert result is not None
    assert result.read_text(encoding="utf-8") != "DISABLED EXT"


# ---------------------------------------------------------------------------
# Disabled preset excluded
# ---------------------------------------------------------------------------

def test_disabled_preset_excluded_from_resolution(qakit_dir: Path) -> None:
    import json

    preset_id = "disabled-preset"
    preset_tmpl = qakit_dir / "presets" / preset_id / "templates" / "commands" / TEMPLATE
    _write_template(preset_tmpl, "DISABLED PRESET")
    state_file = qakit_dir / "presets.json"
    state_file.write_text(
        json.dumps({"presets": [{"id": preset_id, "enabled": False, "priority": 1}]})
    )

    resolver = TemplateResolver(qakit_dir)
    result = resolver.resolve(TEMPLATE)
    assert result is not None
    assert result.read_text(encoding="utf-8") != "DISABLED PRESET"
