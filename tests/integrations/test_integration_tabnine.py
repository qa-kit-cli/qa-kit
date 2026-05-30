"""Tests for Tabnine integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, TomlIntegration
from qa_kit_cli.integrations.tabnine import TabnineIntegration


def test_registration() -> None:
    assert get_integration("tabnine") is TabnineIntegration


def test_key() -> None:
    assert TabnineIntegration.key == "tabnine"


def test_config_has_folder() -> None:
    assert "folder" in TabnineIntegration.config
    assert TabnineIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in TabnineIntegration.registrar_config
    assert TabnineIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in TabnineIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(TabnineIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = TabnineIntegration.render_command("tabnine.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = TabnineIntegration.render_command("tabnine.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = TabnineIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_toml_integration() -> None:
    assert issubclass(TabnineIntegration, TomlIntegration)


def test_command_extension_is_toml() -> None:
    assert TabnineIntegration.command_extension() == ".toml"


def test_render_contains_commands_table() -> None:
    rendered = TabnineIntegration.render_command("tabnine.test", "body", "desc")
    assert "[[commands]]" in rendered


