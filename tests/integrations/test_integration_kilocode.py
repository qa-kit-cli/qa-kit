"""Tests for KiloCode integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.kilocode import KiloCodeIntegration


def test_registration() -> None:
    assert get_integration("kilocode") is KiloCodeIntegration


def test_key() -> None:
    assert KiloCodeIntegration.key == "kilocode"


def test_config_has_folder() -> None:
    assert "folder" in KiloCodeIntegration.config
    assert KiloCodeIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in KiloCodeIntegration.registrar_config
    assert KiloCodeIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in KiloCodeIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(KiloCodeIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = KiloCodeIntegration.render_command("kilocode.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = KiloCodeIntegration.render_command("kilocode.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = KiloCodeIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(KiloCodeIntegration, MarkdownIntegration)


