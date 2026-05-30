"""Tests for Bob integration."""
from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration
from qa_kit_cli.integrations.bob import BobIntegration


def test_registration() -> None:
    assert get_integration("bob") is BobIntegration


def test_key() -> None:
    assert BobIntegration.key == "bob"


def test_config_has_folder() -> None:
    assert "folder" in BobIntegration.config
    assert BobIntegration.config["folder"]


def test_registrar_config_has_dir() -> None:
    assert "dir" in BobIntegration.registrar_config
    assert BobIntegration.registrar_config["dir"]


def test_registrar_config_has_extension() -> None:
    assert "extension" in BobIntegration.registrar_config


def test_is_integration_base_subclass() -> None:
    assert issubclass(BobIntegration, IntegrationBase)


def test_render_command_returns_string() -> None:
    rendered = BobIntegration.render_command("bob.test", "test content", "test description")
    assert isinstance(rendered, str)
    assert len(rendered) > 0


def test_render_command_includes_content() -> None:
    rendered = BobIntegration.render_command("bob.test", "unique_content_xyz", "desc")
    assert "unique_content_xyz" in rendered


def test_get_commands_dir(tmp_path: Path) -> None:
    d = BobIntegration.get_commands_dir(tmp_path)
    assert isinstance(d, Path)
    assert str(d).startswith(str(tmp_path))

def test_is_markdown_integration() -> None:
    assert issubclass(BobIntegration, MarkdownIntegration)


