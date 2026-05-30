"""Tests for Devin integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.devin import DevinIntegration


def test_registration() -> None:
    assert get_integration("devin") is DevinIntegration


def test_key() -> None:
    assert DevinIntegration.key == "devin"


def test_config_has_folder() -> None:
    assert "folder" in DevinIntegration.config
    assert DevinIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in DevinIntegration.registrar_config
    assert DevinIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in DevinIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(DevinIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = DevinIntegration.render_command("devin.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = DevinIntegration.render_command("devin.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = DevinIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(DevinIntegration, MarkdownIntegration)


