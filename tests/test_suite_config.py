"""Tests for suite_config module."""

from __future__ import annotations

from pathlib import Path

import pytest

from qa_kit_cli.shared_infra import ensure_project_layout
from qa_kit_cli.suite_config import (
    SUITE_MEMORY_FILES,
    SuiteIndex,
    create_suite,
    get_active_suite,
    list_suites,
    slugify,
)


def test_slugify_lowercase_and_hyphens() -> None:
    """slugify converts spaces to hyphens and lowercases."""
    assert slugify("Login Flow") == "login-flow"


def test_slugify_strips_special_chars() -> None:
    """slugify removes non-alphanumeric characters."""
    assert slugify("Auth & 2FA!") == "auth-2fa"


def test_slugify_handles_underscores() -> None:
    """slugify converts underscores to hyphens."""
    assert slugify("login_flow") == "login-flow"


def test_create_suite_sequential_numbering(tmp_path: Path) -> None:
    """First suite gets 001 prefix with sequential numbering."""
    qakit_dir = ensure_project_layout(tmp_path)
    entry = create_suite(qakit_dir, "Login Flow", branch_numbering="sequential")
    assert entry.id.startswith("001-")


def test_create_suite_timestamp_numbering(tmp_path: Path) -> None:
    """Timestamp numbering produces longer ID than sequential."""
    qakit_dir = ensure_project_layout(tmp_path)
    entry = create_suite(qakit_dir, "Checkout", branch_numbering="timestamp")
    assert len(entry.id) > 4  # timestamp is longer than 001


def test_create_suite_creates_all_memory_files(tmp_path: Path) -> None:
    """All SUITE_MEMORY_FILES are created in the suite directory."""
    qakit_dir = ensure_project_layout(tmp_path)
    entry = create_suite(qakit_dir, "Login Flow")
    suite_path = tmp_path / entry.path
    for filename in SUITE_MEMORY_FILES:
        assert (suite_path / filename).exists(), f"Missing: {filename}"


def test_create_suite_updates_index(tmp_path: Path) -> None:
    """Suite creation adds an entry to index.json."""
    qakit_dir = ensure_project_layout(tmp_path)
    entry = create_suite(qakit_dir, "Login Flow")
    index = SuiteIndex.load(qakit_dir)
    assert any(s.id == entry.id for s in index.suites)


def test_create_two_suites_increments_number(tmp_path: Path) -> None:
    """Sequential numbering increments correctly for multiple suites."""
    qakit_dir = ensure_project_layout(tmp_path)
    e1 = create_suite(qakit_dir, "Login", branch_numbering="sequential")
    e2 = create_suite(qakit_dir, "Checkout", branch_numbering="sequential")
    assert e1.id.startswith("001-")
    assert e2.id.startswith("002-")


def test_list_suites_empty(tmp_path: Path) -> None:
    """list_suites returns empty list when no suites exist."""
    qakit_dir = ensure_project_layout(tmp_path)
    assert list_suites(qakit_dir) == []


def test_list_suites_returns_all_entries(tmp_path: Path) -> None:
    """list_suites returns all created suites."""
    qakit_dir = ensure_project_layout(tmp_path)
    create_suite(qakit_dir, "Login")
    create_suite(qakit_dir, "Checkout")
    suites = list_suites(qakit_dir)
    assert len(suites) == 2


def test_get_active_suite_no_config(tmp_path: Path) -> None:
    """get_active_suite returns None when no active suite is configured."""
    qakit_dir = ensure_project_layout(tmp_path)
    assert get_active_suite(qakit_dir) is None


def test_get_active_suite_reads_config(tmp_path: Path) -> None:
    """get_active_suite returns the entry matching active_suite in config."""
    qakit_dir = ensure_project_layout(tmp_path)
    entry = create_suite(qakit_dir, "Login")
    from qa_kit_cli.project_config import ProjectConfig
    cfg = ProjectConfig.load(qakit_dir)
    cfg.active_suite = entry.id
    cfg.save(qakit_dir)
    active = get_active_suite(qakit_dir)
    assert active is not None
    assert active.id == entry.id


def test_suite_index_get_returns_none_for_unknown(tmp_path: Path) -> None:
    """SuiteIndex.get returns None for an unknown suite ID."""
    qakit_dir = ensure_project_layout(tmp_path)
    index = SuiteIndex.load(qakit_dir)
    assert index.get("nonexistent-suite") is None


def test_suite_path_is_relative_to_project_root(tmp_path: Path) -> None:
    """Suite path is stored relative to the project root (qakit_dir.parent)."""
    qakit_dir = ensure_project_layout(tmp_path)
    entry = create_suite(qakit_dir, "Login")
    # Path should start with .qakit/suites/
    assert entry.path.startswith(".qakit")
