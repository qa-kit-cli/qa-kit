"""Tests for Vibe integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.vibe import VibeIntegration


def test_registration() -> None:
    assert get_integration("vibe") is VibeIntegration


def test_key() -> None:
    assert VibeIntegration.key == "vibe"


def test_config_has_folder() -> None:
    assert "folder" in VibeIntegration.config
    assert VibeIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in VibeIntegration.registrar_config
    assert VibeIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in VibeIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(VibeIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = VibeIntegration.render_command("vibe.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = VibeIntegration.render_command("vibe.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = VibeIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(VibeIntegration, MarkdownIntegration)


