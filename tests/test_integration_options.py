"""Tests for --integration-options parsing."""

from __future__ import annotations

from qa_kit_cli._integration_options import parse_integration_options


def test_parse_empty_returns_empty() -> None:
    assert parse_integration_options(None) == {}
    assert parse_integration_options("") == {}


def test_parse_skills_flag() -> None:
    result = parse_integration_options("--skills")
    assert result == {"skills": True}


def test_parse_commands_dir_value() -> None:
    result = parse_integration_options("--commands-dir .myagent/cmds")
    assert result["commands_dir"] == ".myagent/cmds"


def test_parse_multiple_options() -> None:
    result = parse_integration_options("--skills --commands-dir .agents/cmds")
    assert result["skills"] is True
    assert result["commands_dir"] == ".agents/cmds"


def test_parse_quoted_value() -> None:
    result = parse_integration_options('--commands-dir ".my agent/cmds"')
    assert result["commands_dir"] == ".my agent/cmds"


def test_parse_hyphen_converts_to_underscore() -> None:
    result = parse_integration_options("--some-long-option")
    assert "some_long_option" in result
