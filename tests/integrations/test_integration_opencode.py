"""Tests for OpenCode integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.opencode import OpenCodeIntegration


def test_registration() -> None:
    assert get_integration("opencode") is OpenCodeIntegration


def test_key() -> None:
    assert OpenCodeIntegration.key == "opencode"


def test_config_has_folder() -> None:
    assert "folder" in OpenCodeIntegration.config
    assert OpenCodeIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in OpenCodeIntegration.registrar_config
    assert OpenCodeIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in OpenCodeIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(OpenCodeIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = OpenCodeIntegration.render_command("opencode.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = OpenCodeIntegration.render_command("opencode.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = OpenCodeIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(OpenCodeIntegration, MarkdownIntegration)


