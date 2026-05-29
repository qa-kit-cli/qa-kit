"""Tests for integration classes, registry, and command rendering."""

from __future__ import annotations

from pathlib import Path

from qa_kit_cli.integrations import get_integration, list_integrations, register_integration
from qa_kit_cli.integrations.base import IntegrationBase, MarkdownIntegration, TomlIntegration
from qa_kit_cli.integrations.agy import AgyIntegration
from qa_kit_cli.integrations.claude import ClaudeIntegration
from qa_kit_cli.integrations.copilot import CopilotIntegration
from qa_kit_cli.integrations.gemini import GeminiIntegration


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_get_integration_claude_is_not_none() -> None:
    assert get_integration("claude") is not None


def test_get_integration_returns_correct_class() -> None:
    assert get_integration("claude") is ClaudeIntegration
    assert get_integration("gemini") is GeminiIntegration
    assert get_integration("copilot") is CopilotIntegration


def test_get_integration_unknown_returns_none() -> None:
    assert get_integration("not-a-real-integration-xyz") is None


def test_list_integrations_returns_at_least_31() -> None:
    integrations = list_integrations()
    assert len(integrations) >= 31


def test_all_integrations_have_non_empty_key() -> None:
    for cls in list_integrations():
        assert cls.key, f"Integration class {cls.__name__} has empty key"


def test_all_integration_keys_are_unique() -> None:
    keys = [cls.key for cls in list_integrations()]
    assert len(keys) == len(set(keys)), "Duplicate integration keys found"


def test_register_integration_adds_to_registry() -> None:
    class DummyIntegration(MarkdownIntegration):
        key = "_test_dummy_xyz"
        config = {"folder": ".dummy/commands/"}
        registrar_config = {"extension": ".md"}

    try:
        register_integration(DummyIntegration)
        assert get_integration("_test_dummy_xyz") is DummyIntegration
    finally:
        from qa_kit_cli.integrations import _REGISTRY
        _REGISTRY.pop("_test_dummy_xyz", None)


# ---------------------------------------------------------------------------
# MarkdownIntegration rendering
# ---------------------------------------------------------------------------


def test_markdown_integration_render_returns_content_unchanged() -> None:
    content = "# /qakit.strategy\n\nDo the QA thing."
    rendered = ClaudeIntegration.render_command("qakit.strategy", content, "Generate strategy")
    assert rendered == content


def test_markdown_integration_command_extension_is_md() -> None:
    assert ClaudeIntegration.command_extension() == ".md"


def test_markdown_integration_args_placeholder() -> None:
    assert ClaudeIntegration.args_placeholder() == "$ARGUMENTS"


# ---------------------------------------------------------------------------
# TomlIntegration rendering
# ---------------------------------------------------------------------------


def test_toml_integration_render_includes_commands_table() -> None:
    rendered = GeminiIntegration.render_command("qakit.strategy", "Do the thing.", "Generate strategy")
    assert "[[commands]]" in rendered


def test_toml_integration_render_includes_command_name() -> None:
    rendered = GeminiIntegration.render_command("qakit.strategy", "Content.", "Generate strategy")
    assert 'name = "qakit.strategy"' in rendered


def test_toml_integration_render_includes_prompt_content() -> None:
    rendered = GeminiIntegration.render_command("qakit.x", "My prompt here.", "desc")
    assert "My prompt here." in rendered


def test_toml_integration_escapes_double_quotes_in_description() -> None:
    rendered = GeminiIntegration.render_command("qakit.x", "content", 'Say "hello"')
    assert r'\"hello\"' in rendered


def test_toml_integration_command_extension_is_toml() -> None:
    assert GeminiIntegration.command_extension() == ".toml"


# ---------------------------------------------------------------------------
# Commands directory paths
# ---------------------------------------------------------------------------


def test_claude_integration_commands_dir_contains_dot_claude(tmp_path: Path) -> None:
    commands_dir = ClaudeIntegration.get_commands_dir(tmp_path)
    assert ".claude" in str(commands_dir)


def test_copilot_integration_commands_dir_contains_copilot_instructions(tmp_path: Path) -> None:
    commands_dir = CopilotIntegration.get_commands_dir(tmp_path)
    assert "copilot-instructions" in str(commands_dir)


def test_gemini_integration_commands_dir_contains_dot_gemini(tmp_path: Path) -> None:
    commands_dir = GeminiIntegration.get_commands_dir(tmp_path)
    assert ".gemini" in str(commands_dir)


def test_context_file_paths_are_set() -> None:
    assert ClaudeIntegration.context_file == ".claude/CLAUDE.md"
    assert CopilotIntegration.context_file == ".github/copilot-instructions.md"
    assert GeminiIntegration.context_file == ".gemini/GEMINI.md"


def test_agy_integration_registered() -> None:
    assert get_integration("agy") is AgyIntegration


def test_agy_is_skills_based() -> None:
    assert AgyIntegration.supports_skills is True
    assert AgyIntegration.get_skills_dir(Path.cwd()).as_posix().endswith("/.agy/skills")
