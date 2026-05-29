from __future__ import annotations

from pathlib import Path

from qa_kit_cli.presets import (
    ActivePreset,
    PresetManifest,
    PresetManager,
    PresetRegistry,
    load_active_presets,
)
from qa_kit_cli.shared_infra import ensure_project_layout


# ---------------------------------------------------------------------------
# PresetManifest
# ---------------------------------------------------------------------------


def test_preset_manifest_loads_from_yml(tmp_path: Path) -> None:
    preset_dir = tmp_path / "my-preset"
    preset_dir.mkdir()
    (preset_dir / "preset.yml").write_text(
        "id: my-preset\nname: My Preset\nversion: 1.0.0\ndescription: Desc\ncompositions: []\n",
        encoding="utf-8",
    )
    manifest = PresetManifest.load_from_dir(preset_dir)
    assert manifest.id == "my-preset"
    assert manifest.name == "My Preset"
    assert manifest.version == "1.0.0"
    assert manifest.compositions == []


def test_preset_manifest_loads_compositions(tmp_path: Path) -> None:
    preset_dir = tmp_path / "comp-preset"
    preset_dir.mkdir()
    (preset_dir / "preset.yml").write_text(
        "id: comp-preset\nname: Comp\nversion: 0.1.0\ndescription: ''\n"
        "compositions:\n  - command: qakit.strategy\n    mode: replace\n    template: strategy.md\n",
        encoding="utf-8",
    )
    manifest = PresetManifest.load_from_dir(preset_dir)
    assert len(manifest.compositions) == 1
    assert manifest.compositions[0]["command"] == "qakit.strategy"
    assert manifest.compositions[0]["mode"] == "replace"


# ---------------------------------------------------------------------------
# PresetRegistry
# ---------------------------------------------------------------------------


def test_preset_registry_resolves_bundled_playwright(tmp_path: Path) -> None:
    registry = PresetRegistry(tmp_path)
    path = registry.resolve("playwright")
    assert path.exists()
    assert (path / "preset.yml").exists()


def test_preset_registry_resolves_bundled_cypress(tmp_path: Path) -> None:
    registry = PresetRegistry(tmp_path)
    path = registry.resolve("cypress")
    assert path.exists()


def test_preset_registry_resolves_bundled_lean_qa(tmp_path: Path) -> None:
    registry = PresetRegistry(tmp_path)
    path = registry.resolve("lean-qa")
    assert path.exists()


def test_preset_registry_raises_for_unknown_preset(tmp_path: Path) -> None:
    import pytest
    registry = PresetRegistry(tmp_path)
    with pytest.raises(FileNotFoundError, match="not-a-real-preset"):
        registry.resolve("not-a-real-preset")


def test_preset_registry_lists_bundled_presets(tmp_path: Path) -> None:
    registry = PresetRegistry(tmp_path)
    bundled = registry.list_bundled()
    assert "playwright" in bundled
    assert "cypress" in bundled
    assert "lean-qa" in bundled


# ---------------------------------------------------------------------------
# PresetManager
# ---------------------------------------------------------------------------


def test_preset_manager_add_priority_enable_disable_remove(project_dir) -> None:
    ensure_project_layout(project_dir)
    manager = PresetManager(project_dir)

    manager.add("playwright")
    entries = manager.list()
    assert any(e["id"] == "playwright" for e in entries)

    assert manager.set_priority("playwright", 5)
    assert manager.set_enabled("playwright", False)
    assert manager.set_enabled("playwright", True)
    assert manager.remove("playwright")


def test_preset_manager_persists_after_reload(project_dir) -> None:
    ensure_project_layout(project_dir)
    PresetManager(project_dir).add("playwright")

    reloaded = PresetManager(project_dir)
    assert any(e["id"] == "playwright" for e in reloaded.list())


def test_preset_manager_deduplication_on_readd(project_dir) -> None:
    ensure_project_layout(project_dir)
    manager = PresetManager(project_dir)
    manager.add("playwright")
    manager.add("playwright")
    playwright_entries = [e for e in manager.list() if e["id"] == "playwright"]
    assert len(playwright_entries) == 1


def test_preset_manager_default_priority_increments(project_dir) -> None:
    ensure_project_layout(project_dir)
    manager = PresetManager(project_dir)
    manager.add("playwright")
    manager.add("cypress")

    entries = {e["id"]: e for e in manager.list()}
    assert entries["playwright"]["priority"] == 1
    assert entries["cypress"]["priority"] == 2


def test_preset_manager_remove_returns_false_for_nonexistent(project_dir) -> None:
    ensure_project_layout(project_dir)
    assert not PresetManager(project_dir).remove("nonexistent-preset")


def test_preset_manager_set_priority_returns_false_for_nonexistent(project_dir) -> None:
    ensure_project_layout(project_dir)
    assert not PresetManager(project_dir).set_priority("nonexistent", 99)


def test_preset_manager_set_enabled_returns_false_for_nonexistent(project_dir) -> None:
    ensure_project_layout(project_dir)
    assert not PresetManager(project_dir).set_enabled("nonexistent", False)


# ---------------------------------------------------------------------------
# load_active_presets
# ---------------------------------------------------------------------------


def test_load_active_presets_returns_installed_and_enabled(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    PresetManager(project_dir).add("playwright")

    active = load_active_presets(qakit_dir)
    assert len(active) == 1
    assert active[0].manifest.id == "playwright"


def test_load_active_presets_excludes_disabled(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    manager = PresetManager(project_dir)
    manager.add("playwright")
    manager.set_enabled("playwright", False)

    active = load_active_presets(qakit_dir)
    assert len(active) == 0


def test_load_active_presets_sorted_by_priority(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    manager = PresetManager(project_dir)
    manager.add("playwright")
    manager.add("lean-qa")
    manager.set_priority("playwright", 2)
    manager.set_priority("lean-qa", 1)

    active = load_active_presets(qakit_dir)
    assert [p.manifest.id for p in active] == ["lean-qa", "playwright"]


def test_load_active_presets_empty_when_none_installed(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    assert load_active_presets(qakit_dir) == []


# ---------------------------------------------------------------------------
# ActivePreset
# ---------------------------------------------------------------------------


def test_active_preset_get_composition(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    PresetManager(project_dir).add("playwright")

    active = load_active_presets(qakit_dir)
    comp = active[0].get_composition("qakit.write.playwright")
    assert comp is not None
    assert comp["mode"] == "replace"
    assert comp["template"] == "write.playwright.md"


def test_active_preset_get_composition_returns_none_for_unknown(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    PresetManager(project_dir).add("playwright")

    active = load_active_presets(qakit_dir)
    assert active[0].get_composition("qakit.some.unknown.command") is None


def test_active_preset_read_template(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    PresetManager(project_dir).add("playwright")

    active = load_active_presets(qakit_dir)
    content = active[0].read_template("write.playwright.md")
    assert content is not None
    assert "Playwright" in content


def test_active_preset_read_template_returns_none_when_missing(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    PresetManager(project_dir).add("playwright")

    active = load_active_presets(qakit_dir)
    assert active[0].read_template("nonexistent.md") is None
