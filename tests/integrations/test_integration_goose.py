"""Tests for Goose integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, YamlIntegration
from qa_kit_cli.integrations.goose import GooseIntegration


def test_registration() -> None:
    assert get_integration("goose") is GooseIntegration


def test_key() -> None:
    assert GooseIntegration.key == "goose"


def test_config_has_folder() -> None:
    assert "folder" in GooseIntegration.config
    assert GooseIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in GooseIntegration.registrar_config
    assert GooseIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in GooseIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(GooseIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = GooseIntegration.render_command("goose.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = GooseIntegration.render_command("goose.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = GooseIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_yaml_integration() -> None:
    assert issubclass(GooseIntegration, YamlIntegration)


def test_command_extension_is_yaml() -> None:
    assert GooseIntegration.command_extension() == ".yaml"


def test_args_placeholder_is_template() -> None:
    assert GooseIntegration.args_placeholder() == "{{args}}"


