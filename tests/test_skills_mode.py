"""Tests for skills mode installation."""

from __future__ import annotations

from qa_kit_cli.agents import SkillRegistrar
from qa_kit_cli.integrations import get_integration
from qa_kit_cli.shared_infra import ensure_project_layout


def test_claude_integration_supports_skills() -> None:
    integration = get_integration("claude")
    assert integration is not None
    assert integration.supports_skills is True


def test_codex_integration_supports_skills() -> None:
    integration = get_integration("codex")
    assert integration is not None
    assert integration.supports_skills is True


def test_skill_registrar_installs_skill_dirs(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    registrar = SkillRegistrar()
    installed = registrar.install_for_integration(project_dir, qakit_dir, "claude")
    assert len(installed) > 0
    for path in installed:
        assert path.name == "SKILL.md"
        assert path.parent.parent == project_dir / ".claude" / "skills"


def test_skill_registrar_creates_skill_subdirs(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    SkillRegistrar().install_for_integration(project_dir, qakit_dir, "claude")
    skills_dir = project_dir / ".claude" / "skills"
    assert skills_dir.is_dir()
    subdirs = [d for d in skills_dir.iterdir() if d.is_dir()]
    assert len(subdirs) > 0


def test_skill_registrar_claude_adds_frontmatter(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    SkillRegistrar().install_for_integration(project_dir, qakit_dir, "claude")
    skill_file = project_dir / ".claude" / "skills" / "qakit-strategy" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")
    assert "description:" in content


def test_skill_registrar_raises_for_unsupported_integration(project_dir) -> None:
    import pytest
    qakit_dir = ensure_project_layout(project_dir)
    integration = get_integration("generic")
    assert integration is not None
    if not integration.supports_skills:
        with pytest.raises(ValueError, match="does not support skills mode"):
            SkillRegistrar().install_for_integration(project_dir, qakit_dir, "generic")


def test_skill_registrar_records_manifest(project_dir) -> None:
    from qa_kit_cli.integrations.manifest import get_recorded_files

    qakit_dir = ensure_project_layout(project_dir)
    SkillRegistrar().install_for_integration(project_dir, qakit_dir, "claude")
    manifest = get_recorded_files(qakit_dir, "claude.skills")
    assert len(manifest) > 0
