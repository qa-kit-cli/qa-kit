"""Tests for HOOK_EVENTS naming conventions and extension manifest hook validation."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from qa_kit_cli._assets import get_bundled_extensions_dir
from qa_kit_cli.extensions import HOOK_EVENTS, ExtensionManifest

# ---------------------------------------------------------------------------
# HOOK_EVENTS structure
# ---------------------------------------------------------------------------


def test_all_hook_events_follow_before_after_naming_convention() -> None:
    pattern = re.compile(r"^(before|after)_[a-z][a-z0-9_]*$")
    bad = [e for e in HOOK_EVENTS if not pattern.match(e)]
    assert not bad, f"Hook events with invalid names: {bad}"


def test_hook_events_are_paired_before_and_after() -> None:
    befores = {e[len("before_"):] for e in HOOK_EVENTS if e.startswith("before_")}
    afters = {e[len("after_"):] for e in HOOK_EVENTS if e.startswith("after_")}
    assert befores == afters, (
        f"Unpaired hook events — before-only: {befores - afters}, after-only: {afters - befores}"
    )


def test_hook_events_has_no_duplicates() -> None:
    assert len(HOOK_EVENTS) == len(set(HOOK_EVENTS)), "HOOK_EVENTS contains duplicates"


def test_hook_events_count_is_even() -> None:
    assert len(HOOK_EVENTS) % 2 == 0, "HOOK_EVENTS count should be even (before/after pairs)"


def test_hook_events_includes_core_qa_lifecycle() -> None:
    expected = {
        "before_strategy", "after_strategy",
        "before_testplan", "after_testplan",
        "before_write_playwright", "after_write_playwright",
        "before_ci_github_actions", "after_ci_github_actions",
        "before_review_pr", "after_review_pr",
    }
    missing = expected - set(HOOK_EVENTS)
    assert not missing, f"Core lifecycle hook events missing: {missing}"


# ---------------------------------------------------------------------------
# ExtensionManifest hook validation
# ---------------------------------------------------------------------------


def test_extension_manifest_rejects_unlisted_hook_via_load(tmp_path: Path) -> None:
    ext_dir = tmp_path / "bad"
    ext_dir.mkdir()
    (ext_dir / "extension.yml").write_text(
        "id: bad\nhooks:\n  - on_completely_unknown_event\ncommands: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="on_completely_unknown_event"):
        ExtensionManifest.load_from_dir(ext_dir)


def test_extension_manifest_reports_all_invalid_hooks(tmp_path: Path) -> None:
    ext_dir = tmp_path / "multi-bad"
    ext_dir.mkdir()
    (ext_dir / "extension.yml").write_text(
        "id: bad\nhooks:\n  - invalid_one\n  - invalid_two\ncommands: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError) as exc_info:
        ExtensionManifest.load_from_dir(ext_dir)
    msg = str(exc_info.value)
    assert "invalid_one" in msg
    assert "invalid_two" in msg


# ---------------------------------------------------------------------------
# Bundled extensions use only valid hooks
# ---------------------------------------------------------------------------


def test_all_bundled_extensions_use_valid_hook_events() -> None:
    bundled_dir = get_bundled_extensions_dir()
    assert bundled_dir.exists(), "Bundled extensions directory not found"
    errors: list[str] = []
    for ext_dir in bundled_dir.iterdir():
        if not ext_dir.is_dir():
            continue
        manifest_file = ext_dir / "extension.yml"
        if not manifest_file.exists():
            continue
        try:
            ExtensionManifest.load_from_dir(ext_dir)
        except ValueError as e:
            errors.append(f"{ext_dir.name}: {e}")
    assert not errors, "Bundled extensions contain invalid hooks:\n" + "\n".join(errors)


def test_bundled_git_extension_uses_after_hooks() -> None:
    bundled_dir = get_bundled_extensions_dir()
    git_manifest = ExtensionManifest.load_from_dir(bundled_dir / "git")
    assert all(h.startswith("after_") for h in git_manifest.hooks)
