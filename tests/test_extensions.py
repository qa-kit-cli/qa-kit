from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from qa_kit_cli.extensions import (
    HOOK_EVENTS,
    ExtensionManifest,
    ExtensionManager,
    ExtensionRegistry,
    HookExecutor,
)
from qa_kit_cli.shared_infra import ensure_project_layout


# ---------------------------------------------------------------------------
# ExtensionManifest
# ---------------------------------------------------------------------------


def test_extension_manifest_loads_from_yml(tmp_path: Path) -> None:
    ext_dir = tmp_path / "my-ext"
    ext_dir.mkdir()
    (ext_dir / "extension.yml").write_text(
        "id: my-ext\nname: My Extension\nversion: 1.2.3\ndescription: Test ext\n"
        "hooks:\n  - after_strategy\ncommands:\n  after_strategy: 'echo done'\n",
        encoding="utf-8",
    )
    manifest = ExtensionManifest.load_from_dir(ext_dir)
    assert manifest.id == "my-ext"
    assert manifest.name == "My Extension"
    assert manifest.version == "1.2.3"
    assert manifest.hooks == ["after_strategy"]
    assert manifest.commands == {"after_strategy": "echo done"}


def test_extension_manifest_rejects_invalid_hooks(tmp_path: Path) -> None:
    ext_dir = tmp_path / "bad-ext"
    ext_dir.mkdir()
    (ext_dir / "extension.yml").write_text(
        "id: bad\nhooks:\n  - not_a_valid_hook_event\ncommands: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="not_a_valid_hook_event"):
        ExtensionManifest.load_from_dir(ext_dir)


def test_extension_manifest_empty_hooks_accepted(tmp_path: Path) -> None:
    ext_dir = tmp_path / "empty-hooks"
    ext_dir.mkdir()
    (ext_dir / "extension.yml").write_text(
        "id: empty\nhooks: []\ncommands: {}\n",
        encoding="utf-8",
    )
    manifest = ExtensionManifest.load_from_dir(ext_dir)
    assert manifest.hooks == []


def test_extension_manifest_multiple_valid_hooks(tmp_path: Path) -> None:
    ext_dir = tmp_path / "multi"
    ext_dir.mkdir()
    (ext_dir / "extension.yml").write_text(
        "id: multi\nhooks:\n  - after_strategy\n  - before_testplan\n  - after_review_pr\ncommands: {}\n",
        encoding="utf-8",
    )
    manifest = ExtensionManifest.load_from_dir(ext_dir)
    assert len(manifest.hooks) == 3


# ---------------------------------------------------------------------------
# ExtensionRegistry
# ---------------------------------------------------------------------------


def test_extension_registry_resolves_bundled_git(tmp_path: Path) -> None:
    registry = ExtensionRegistry(tmp_path)
    path = registry.resolve("git")
    assert path.exists()
    assert (path / "extension.yml").exists()


def test_extension_registry_raises_for_unknown_extension(tmp_path: Path) -> None:
    registry = ExtensionRegistry(tmp_path)
    with pytest.raises(FileNotFoundError, match="not-a-real-extension"):
        registry.resolve("not-a-real-extension")


def test_extension_registry_resolves_absolute_local_path(tmp_path: Path) -> None:
    ext_dir = tmp_path / "local-ext"
    ext_dir.mkdir()
    (ext_dir / "extension.yml").write_text(
        "id: local\nhooks: []\ncommands: {}\n", encoding="utf-8"
    )
    registry = ExtensionRegistry(tmp_path)
    path = registry.resolve(str(ext_dir))
    assert path == ext_dir


def test_extension_registry_resolves_all_bundled_extensions(tmp_path: Path) -> None:
    registry = ExtensionRegistry(tmp_path)
    bundled_ids = ["git", "coverage-gate", "test-numbering", "allure", "testrail", "jira"]
    for ext_id in bundled_ids:
        path = registry.resolve(ext_id)
        assert path.exists(), f"Bundled extension not found: {ext_id}"


# ---------------------------------------------------------------------------
# ExtensionManager
# ---------------------------------------------------------------------------


def test_extension_manager_add_list_enable_disable_remove(project_dir) -> None:
    ensure_project_layout(project_dir)
    manager = ExtensionManager(project_dir)

    manager.add("git")
    entries = manager.list()
    assert any(e["id"] == "git" for e in entries)

    assert manager.set_enabled("git", False)
    assert manager.set_enabled("git", True)
    assert manager.remove("git")


def test_extension_manager_persists_after_reload(project_dir) -> None:
    ensure_project_layout(project_dir)
    ExtensionManager(project_dir).add("git")

    reloaded = ExtensionManager(project_dir)
    assert any(e["id"] == "git" for e in reloaded.list())


def test_extension_manager_deduplication_on_readd(project_dir) -> None:
    ensure_project_layout(project_dir)
    manager = ExtensionManager(project_dir)
    manager.add("git")
    manager.add("git")
    git_entries = [e for e in manager.list() if e["id"] == "git"]
    assert len(git_entries) == 1


def test_extension_manager_active_manifests_includes_enabled(project_dir) -> None:
    ensure_project_layout(project_dir)
    manager = ExtensionManager(project_dir)
    manager.add("git")
    manifests = manager.active_manifests()
    assert any(m.id == "git" for m in manifests)


def test_extension_manager_active_manifests_excludes_disabled(project_dir) -> None:
    ensure_project_layout(project_dir)
    manager = ExtensionManager(project_dir)
    manager.add("git")
    manager.set_enabled("git", False)
    manifests = manager.active_manifests()
    assert not any(m.id == "git" for m in manifests)


def test_extension_manager_set_enabled_nonexistent_returns_false(project_dir) -> None:
    ensure_project_layout(project_dir)
    assert not ExtensionManager(project_dir).set_enabled("nonexistent", True)


def test_extension_manager_remove_nonexistent_returns_false(project_dir) -> None:
    ensure_project_layout(project_dir)
    assert not ExtensionManager(project_dir).remove("nonexistent")


def test_extension_manager_add_multiple_independent_extensions(project_dir) -> None:
    ensure_project_layout(project_dir)
    manager = ExtensionManager(project_dir)
    manager.add("git")
    manager.add("coverage-gate")
    ids = {e["id"] for e in manager.list()}
    assert "git" in ids
    assert "coverage-gate" in ids


# ---------------------------------------------------------------------------
# HookExecutor
# ---------------------------------------------------------------------------


def test_hook_executor_calls_subprocess_for_matching_event(tmp_path: Path) -> None:
    executor = HookExecutor(tmp_path)
    manifest = ExtensionManifest(
        id="test",
        name="Test",
        version="0.1.0",
        description="",
        hooks=["after_strategy"],
        commands={"after_strategy": "echo hook fired"},
    )
    with patch("qa_kit_cli.extensions.subprocess.call", return_value=0) as mock_call:
        results = executor.execute([manifest], "after_strategy")
    assert results == [("test", 0)]
    mock_call.assert_called_once()


def test_hook_executor_skips_event_not_in_commands(tmp_path: Path) -> None:
    executor = HookExecutor(tmp_path)
    manifest = ExtensionManifest(
        id="test",
        name="Test",
        version="0.1.0",
        description="",
        hooks=["after_strategy"],
        commands={},
    )
    with patch("qa_kit_cli.extensions.subprocess.call", return_value=0) as mock_call:
        results = executor.execute([manifest], "after_strategy")
    assert results == []
    mock_call.assert_not_called()


def test_hook_executor_handles_multiple_manifests(tmp_path: Path) -> None:
    executor = HookExecutor(tmp_path)
    manifests = [
        ExtensionManifest(
            id="ext-a",
            name="A",
            version="0.1.0",
            description="",
            hooks=["after_strategy"],
            commands={"after_strategy": "echo a"},
        ),
        ExtensionManifest(
            id="ext-b",
            name="B",
            version="0.1.0",
            description="",
            hooks=["after_strategy"],
            commands={"after_strategy": "echo b"},
        ),
    ]
    with patch("qa_kit_cli.extensions.subprocess.call", return_value=0):
        results = executor.execute(manifests, "after_strategy")
    assert len(results) == 2
    assert {r[0] for r in results} == {"ext-a", "ext-b"}
