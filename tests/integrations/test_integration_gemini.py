"""Tests for Gemini integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, TomlIntegration
from qa_kit_cli.integrations.gemini import GeminiIntegration


def test_registration() -> None:
    assert get_integration("gemini") is GeminiIntegration


def test_key() -> None:
    assert GeminiIntegration.key == "gemini"


def test_config_has_folder() -> None:
    assert "folder" in GeminiIntegration.config
    assert GeminiIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in GeminiIntegration.registrar_config
    assert GeminiIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in GeminiIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(GeminiIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = GeminiIntegration.render_command("gemini.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = GeminiIntegration.render_command("gemini.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = GeminiIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_toml_integration() -> None:
    assert issubclass(GeminiIntegration, TomlIntegration)


def test_command_extension_is_toml() -> None:
    assert GeminiIntegration.command_extension() == ".toml"


def test_render_contains_commands_table() -> None:
    rendered = GeminiIntegration.render_command("gemini.test", "body", "desc")
    assert "[[commands]]" in rendered


