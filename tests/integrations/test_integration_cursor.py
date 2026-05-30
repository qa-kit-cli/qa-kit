"""Tests for Cursor integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.cursor_agent import CursorIntegration


def test_registration() -> None:
    assert get_integration("cursor") is CursorIntegration


def test_key() -> None:
    assert CursorIntegration.key == "cursor"


def test_config_has_folder() -> None:
    assert "folder" in CursorIntegration.config
    assert CursorIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in CursorIntegration.registrar_config
    assert CursorIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in CursorIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(CursorIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = CursorIntegration.render_command("cursor.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = CursorIntegration.render_command("cursor.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = CursorIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(CursorIntegration, MarkdownIntegration)


