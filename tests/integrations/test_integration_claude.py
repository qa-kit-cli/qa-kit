"""Tests for Claude integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.claude import ClaudeIntegration


def test_registration() -> None:
    assert get_integration("claude") is ClaudeIntegration


def test_key() -> None:
    assert ClaudeIntegration.key == "claude"


def test_config_has_folder() -> None:
    assert "folder" in ClaudeIntegration.config
    assert ClaudeIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in ClaudeIntegration.registrar_config
    assert ClaudeIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in ClaudeIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(ClaudeIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = ClaudeIntegration.render_command("claude.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = ClaudeIntegration.render_command("claude.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = ClaudeIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(ClaudeIntegration, MarkdownIntegration)

def test_supports_skills() -> None:
    assert ClaudeIntegration.supports_skills is True


