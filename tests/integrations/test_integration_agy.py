"""Tests for Agy integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.agy import AgyIntegration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration


def test_registration() -> None:
    assert get_integration("agy") is AgyIntegration


def test_key() -> None:
    assert AgyIntegration.key == "agy"


def test_config_has_folder() -> None:
    assert "folder" in AgyIntegration.config
    assert AgyIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in AgyIntegration.registrar_config
    assert AgyIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in AgyIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(AgyIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = AgyIntegration.render_command("agy.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = AgyIntegration.render_command("agy.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = AgyIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(AgyIntegration, MarkdownIntegration)

def test_supports_skills() -> None:
    assert AgyIntegration.supports_skills is True


