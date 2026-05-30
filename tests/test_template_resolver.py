"""Tests for the runtime template resolver."""

from __future__ import annotations

from qa_kit_cli.agents import COMMAND_MANIFEST
from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.template_resolver import TemplateResolver


def test_resolver_finds_core_template(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    resolver = TemplateResolver(qakit_dir)
    path = resolver.resolve("strategy.md")
    assert path is not None
    assert path.exists()
    assert path.name == "strategy.md"


def test_resolver_returns_none_for_missing_template(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    resolver = TemplateResolver(qakit_dir)
    assert resolver.resolve("nonexistent-template.md") is None


def test_resolver_override_wins_over_core(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    overrides_dir = qakit_dir / "templates" / "overrides"
    overrides_dir.mkdir(parents=True, exist_ok=True)
    override_file = overrides_dir / "strategy.md"
    override_file.write_text("OVERRIDE CONTENT", encoding="utf-8")

    resolver = TemplateResolver(qakit_dir)
    path = resolver.resolve("strategy.md")
    assert path == override_file


def test_resolver_preset_wins_over_core(project_dir) -> None:
    from qa_kit_cli.presets import PresetManager

    qakit_dir = ensure_project_layout(project_dir)
    PresetManager(project_dir).add("playwright")

    resolver = TemplateResolver(qakit_dir)
    path = resolver.resolve("write.playwright.md")
    assert path is not None
    assert "playwright" in str(path)


def test_resolver_resolve_stack_has_correct_layers(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    resolver = TemplateResolver(qakit_dir)
    stack = resolver.resolve_stack("strategy.md")
    assert len(stack) >= 1
    layers = [layer for layer, _, _ in stack]
    assert "core" in layers


def test_resolver_marks_winner_in_stack(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    resolver = TemplateResolver(qakit_dir)
    stack = resolver.resolve_stack("strategy.md")
    winners = [wins for _, _, wins in stack]
    assert sum(winners) == 1, "Exactly one layer should be marked as winner"
    assert winners[0] is True, "First entry should be the winner"


def test_resolver_resolves_all_manifest_templates(project_dir) -> None:
    qakit_dir = ensure_project_layout(project_dir)
    resolver = TemplateResolver(qakit_dir)
    missing = [spec.template_name for spec in COMMAND_MANIFEST if resolver.resolve(spec.template_name) is None]
    assert not missing, f"Could not resolve templates: {missing}"
