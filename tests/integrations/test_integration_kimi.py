"""Tests for Kimi integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.kimi import KimiIntegration


def test_registration() -> None:
    assert get_integration("kimi") is KimiIntegration


def test_key() -> None:
    assert KimiIntegration.key == "kimi"


def test_config_has_folder() -> None:
    assert "folder" in KimiIntegration.config
    assert KimiIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in KimiIntegration.registrar_config
    assert KimiIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in KimiIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(KimiIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = KimiIntegration.render_command("kimi.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = KimiIntegration.render_command("kimi.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = KimiIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(KimiIntegration, MarkdownIntegration)


