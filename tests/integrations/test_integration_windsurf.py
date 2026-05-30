"""Tests for Windsurf integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.windsurf import WindsurfIntegration


def test_registration() -> None:
    assert get_integration("windsurf") is WindsurfIntegration


def test_key() -> None:
    assert WindsurfIntegration.key == "windsurf"


def test_config_has_folder() -> None:
    assert "folder" in WindsurfIntegration.config
    assert WindsurfIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in WindsurfIntegration.registrar_config
    assert WindsurfIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in WindsurfIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(WindsurfIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = WindsurfIntegration.render_command("windsurf.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = WindsurfIntegration.render_command("windsurf.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = WindsurfIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(WindsurfIntegration, MarkdownIntegration)


