from __future__ import annotations

from pathlib import Path

from qa_kit_cli._assets import get_commands_dir
from qa_kit_cli.agents import COMMAND_MANIFEST, CommandRegistrar, detect_active_integration
from qa_kit_cli.presets import PresetManager
from qa_kit_cli.shared_infra import ensure_project_layout


# ---------------------------------------------------------------------------
# COMMAND_MANIFEST integrity
# ---------------------------------------------------------------------------


def test_command_manifest_has_expected_count() -> None:
    assert len(COMMAND_MANIFEST) == 36


def test_command_manifest_command_ids_are_unique() -> None:
    ids = [spec.command_id for spec in COMMAND_MANIFEST]
    assert len(ids) == len(set(ids)), "Duplicate command IDs in COMMAND_MANIFEST"


def test_command_manifest_template_names_are_unique() -> None:
    names = [spec.template_name for spec in COMMAND_MANIFEST]
    assert len(names) == len(set(names)), "Duplicate template names in COMMAND_MANIFEST"


def test_all_command_manifest_templates_exist_on_disk() -> None:
    commands_dir = get_commands_dir()
    missing = [spec.template_name for spec in COMMAND_MANIFEST if not (commands_dir / spec.template_name).exists()]
    assert not missing, f"Missing template files: {missing}"


# ---------------------------------------------------------------------------
# CommandRegistrar — install
# ---------------------------------------------------------------------------


def test_command_registrar_installs_commands(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    registrar = CommandRegistrar()
    installed = registrar.install_for_integration(project_dir, qakit_dir, "claude")
    assert len(installed) == len(COMMAND_MANIFEST)
    assert (project_dir / ".claude" / "commands").is_dir()


def test_command_registrar_uses_core_template_when_no_presets(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    registrar = CommandRegistrar()
    registrar.install_for_integration(project_dir, qakit_dir, "claude")

    content = (project_dir / ".claude" / "commands" / "qakit.write.playwright.md").read_text()
    assert "Playwright" in content


def test_command_registrar_installs_for_copilot_creates_correct_dir(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    CommandRegistrar().install_for_integration(project_dir, qakit_dir, "copilot")
    assert (project_dir / ".github" / "copilot-instructions").is_dir()


def test_command_registrar_installs_for_gemini_creates_toml_files(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    installed = CommandRegistrar().install_for_integration(project_dir, qakit_dir, "gemini")
    assert all(p.suffix == ".toml" for p in installed)
    assert (project_dir / ".gemini" / "commands").is_dir()


def test_command_registrar_toml_output_contains_commands_table(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    CommandRegistrar().install_for_integration(project_dir, qakit_dir, "gemini")
    strategy_file = project_dir / ".gemini" / "commands" / "qakit.strategy.toml"
    assert strategy_file.exists()
    content = strategy_file.read_text(encoding="utf-8")
    assert "[[commands]]" in content
    assert "qakit.strategy" in content


def test_command_registrar_records_manifest_file(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    CommandRegistrar().install_for_integration(project_dir, qakit_dir, "claude")
    manifest_file = qakit_dir / "integrations" / "claude.manifest.json"
    assert manifest_file.exists()


# ---------------------------------------------------------------------------
# Preset compositions
# ---------------------------------------------------------------------------


def test_preset_composition_replace_overrides_core_template(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    PresetManager(project_dir).add("playwright")

    registrar = CommandRegistrar()
    registrar.install_for_integration(project_dir, qakit_dir, "claude")

    content = (project_dir / ".claude" / "commands" / "qakit.write.playwright.md").read_text()
    assert "playwright.config.ts alignment" in content


def test_preset_composition_append_adds_to_core_template(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    PresetManager(project_dir).add("playwright")

    registrar = CommandRegistrar()
    registrar.install_for_integration(project_dir, qakit_dir, "claude")

    content = (project_dir / ".claude" / "commands" / "qakit.write.a11y.md").read_text()
    assert "axe-core" in content
    assert "Playwright preset" in content


def test_higher_priority_preset_wins_replace(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    manager = PresetManager(project_dir)
    manager.add("lean-qa")
    manager.add("playwright")
    manager.set_priority("lean-qa", 1)
    manager.set_priority("playwright", 2)

    registrar = CommandRegistrar()
    registrar.install_for_integration(project_dir, qakit_dir, "claude")

    content = (project_dir / ".claude" / "commands" / "qakit.strategy.md").read_text()
    assert "minimal" in content.lower() or "lean" in content.lower() or "concise" in content.lower()


def test_apply_compositions_replace(project_dir) -> None:
    from qa_kit_cli.presets import ActivePreset, PresetManifest

    manifest = PresetManifest(
        id="test-preset",
        name="Test",
        version="0.0.1",
        description="",
        compositions=[{"command": "qakit.strategy", "mode": "replace", "template": "strategy.md"}],
    )
    preset_dir = project_dir / ".qakit" / "presets" / "test-preset"
    tpl_dir = preset_dir / "templates" / "commands"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "strategy.md").write_text("OVERRIDE CONTENT", encoding="utf-8")

    preset = ActivePreset(manifest=manifest, local_dir=preset_dir)
    result = CommandRegistrar._apply_compositions("CORE CONTENT", "qakit.strategy", [preset])
    assert result == "OVERRIDE CONTENT"


def test_apply_compositions_append(project_dir) -> None:
    from qa_kit_cli.presets import ActivePreset, PresetManifest

    manifest = PresetManifest(
        id="test-preset",
        name="Test",
        version="0.0.1",
        description="",
        compositions=[{"command": "qakit.strategy", "mode": "append", "template": "strategy.md"}],
    )
    preset_dir = project_dir / ".qakit" / "presets" / "test-preset"
    tpl_dir = preset_dir / "templates" / "commands"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "strategy.md").write_text("APPENDED", encoding="utf-8")

    preset = ActivePreset(manifest=manifest, local_dir=preset_dir)
    result = CommandRegistrar._apply_compositions("CORE", "qakit.strategy", [preset])
    assert result.startswith("CORE")
    assert "APPENDED" in result


def test_apply_compositions_no_matching_command_returns_core(project_dir) -> None:
    from qa_kit_cli.presets import ActivePreset, PresetManifest

    manifest = PresetManifest(
        id="p",
        name="P",
        version="0.0.1",
        description="",
        compositions=[{"command": "qakit.other", "mode": "replace", "template": "other.md"}],
    )
    preset_dir = project_dir / ".qakit" / "presets" / "p"
    preset_dir.mkdir(parents=True)
    preset = ActivePreset(manifest=manifest, local_dir=preset_dir)
    result = CommandRegistrar._apply_compositions("CORE", "qakit.strategy", [preset])
    assert result == "CORE"


# ---------------------------------------------------------------------------
# detect_active_integration
# ---------------------------------------------------------------------------


def test_detect_active_integration_defaults_to_claude(project_dir) -> None:
    result = detect_active_integration(project_dir)
    assert result == "claude"


def test_detect_active_integration_finds_copilot_folder(project_dir) -> None:
    (project_dir / ".github" / "copilot-instructions").mkdir(parents=True)
    result = detect_active_integration(project_dir)
    assert result == "copilot"


def test_detect_active_integration_finds_claude_folder(project_dir) -> None:
    (project_dir / ".claude" / "commands").mkdir(parents=True)
    result = detect_active_integration(project_dir)
    assert result == "claude"
