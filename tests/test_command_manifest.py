from __future__ import annotations

from qa_kit_cli.agents import COMMAND_MANIFEST


def test_command_manifest_includes_tasks_to_issues() -> None:
    ids = {spec.command_id for spec in COMMAND_MANIFEST}
    templates = {spec.template_name for spec in COMMAND_MANIFEST}
    assert "qakit.tasks.to-issues" in ids
    assert "tasks.to-issues.md" in templates


def test_command_manifest_count_is_30() -> None:
    # v0.3.0 must include at least the 30-command baseline plus added QA commands.
    assert len(COMMAND_MANIFEST) >= 30
