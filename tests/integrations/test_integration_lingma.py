"""Tests for Lingma integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.lingma import LingmaIntegration


def test_registration() -> None:
    assert get_integration("lingma") is LingmaIntegration


def test_key() -> None:
    assert LingmaIntegration.key == "lingma"


def test_config_has_folder() -> None:
    assert "folder" in LingmaIntegration.config
    assert LingmaIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in LingmaIntegration.registrar_config
    assert LingmaIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in LingmaIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(LingmaIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = LingmaIntegration.render_command("lingma.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = LingmaIntegration.render_command("lingma.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = LingmaIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(LingmaIntegration, MarkdownIntegration)


