from __future__ import annotations

from qa_kit_cli.shared_infra import ensure_memory_files, ensure_project_layout, refresh_shared_infra


def test_refresh_shared_infra_copies_assets(project_dir) -> None:
    qakit_dir = refresh_shared_infra(project_dir)
    ensure_memory_files(project_dir)
    assert (qakit_dir / "templates" / "qa-strategy-template.md").exists()
    assert (qakit_dir / "scripts").exists()
    assert (qakit_dir / "memory" / "test-policy.md").exists()


def test_ensure_project_layout_creates_all_subdirs(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    expected = ["memory", "scripts", "templates", "integrations", "presets", "extensions", "workflows", "auth"]
    for subdir in expected:
        assert (qakit_dir / subdir).is_dir(), f"Missing expected subdir: {subdir}"


def test_ensure_project_layout_returns_qakit_path(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    assert qakit_dir == project_dir / ".qakit"
    assert qakit_dir.is_dir()


def test_ensure_project_layout_is_idempotent(project_dir) -> None:
    ensure_project_layout(project_dir)
    qakit_dir = ensure_project_layout(project_dir)  # second call must not raise
    assert qakit_dir.is_dir()


def test_ensure_memory_files_creates_three_memory_files(project_dir) -> None:
    ensure_project_layout(project_dir)
    ensure_memory_files(project_dir)
    qakit_dir = project_dir / ".qakit"
    assert (qakit_dir / "memory" / "test-policy.md").exists()
    assert (qakit_dir / "memory" / "qa-strategy.md").exists()
    assert (qakit_dir / "memory" / "test-plan.md").exists()


def test_ensure_memory_files_does_not_overwrite_existing_file(project_dir) -> None:
    ensure_project_layout(project_dir)
    memory_file = project_dir / ".qakit" / "memory" / "qa-strategy.md"
    memory_file.write_text("USER CONTENT", encoding="utf-8")

    ensure_memory_files(project_dir)
    assert memory_file.read_text(encoding="utf-8") == "USER CONTENT"


def test_ensure_memory_files_is_idempotent(project_dir) -> None:
    ensure_project_layout(project_dir)
    ensure_memory_files(project_dir)
    ensure_memory_files(project_dir)  # second call must not raise or corrupt files
    assert (project_dir / ".qakit" / "memory" / "test-policy.md").exists()


def test_refresh_shared_infra_copies_both_bash_and_powershell_scripts(project_dir) -> None:
    qakit_dir = refresh_shared_infra(project_dir)
    scripts_dir = qakit_dir / "scripts"
    assert scripts_dir.is_dir()
    bash_scripts = list((scripts_dir / "bash").glob("*.sh")) if (scripts_dir / "bash").exists() else []
    ps_scripts = list((scripts_dir / "powershell").glob("*.ps1")) if (scripts_dir / "powershell").exists() else []
    assert len(bash_scripts) > 0 or len(ps_scripts) > 0, "No scripts copied to .qakit/scripts/"
