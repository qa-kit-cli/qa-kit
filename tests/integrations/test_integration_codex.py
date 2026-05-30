"""Tests for Codex integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.codex import CodexIntegration


def test_registration() -> None:
    assert get_integration("codex") is CodexIntegration


def test_key() -> None:
    assert CodexIntegration.key == "codex"


def test_config_has_folder() -> None:
    assert "folder" in CodexIntegration.config
    assert CodexIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in CodexIntegration.registrar_config
    assert CodexIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in CodexIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(CodexIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = CodexIntegration.render_command("codex.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = CodexIntegration.render_command("codex.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = CodexIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(CodexIntegration, MarkdownIntegration)

def test_supports_skills() -> None:
    assert CodexIntegration.supports_skills is True


