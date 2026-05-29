"""Install and refresh shared .qakit scripts/templates/assets."""

from __future__ import annotations

import shutil
from pathlib import Path

from qa_kit_cli._assets import get_scripts_dir, get_templates_dir
from qa_kit_cli._utils import ensure_dir


def _copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    ensure_dir(dst)
    for item in src.rglob("*"):
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            ensure_dir(target)
            continue
        ensure_dir(target.parent)
        shutil.copy2(item, target)


def ensure_project_layout(project_root: Path) -> Path:
    """Create the baseline .qakit directory structure."""
    qakit_dir = ensure_dir(project_root / ".qakit")
    ensure_dir(qakit_dir / "memory")
    ensure_dir(qakit_dir / "scripts")
    ensure_dir(qakit_dir / "templates")
    ensure_dir(qakit_dir / "integrations")
    ensure_dir(qakit_dir / "presets")
    ensure_dir(qakit_dir / "extensions")
    ensure_dir(qakit_dir / "workflows")
    ensure_dir(qakit_dir / "auth")
    return qakit_dir


def refresh_shared_infra(project_root: Path) -> Path:
    """Copy bundled templates and scripts into .qakit for local project use."""
    qakit_dir = ensure_project_layout(project_root)
    scripts_src = get_scripts_dir()
    templates_src = get_templates_dir()
    _copy_tree(scripts_src, qakit_dir / "scripts")
    _copy_tree(templates_src, qakit_dir / "templates")
    return qakit_dir


def ensure_memory_files(project_root: Path) -> None:
    """Create memory files from templates when absent."""
    qakit_dir = ensure_project_layout(project_root)
    memory_dir = qakit_dir / "memory"
    template_dir = get_templates_dir()

    mapping = {
        "test-policy-template.md": memory_dir / "test-policy.md",
        "qa-strategy-template.md": memory_dir / "qa-strategy.md",
        "test-plan-template.md": memory_dir / "test-plan.md",
    }
    for template_name, target in mapping.items():
        if target.exists():
            continue
        source = template_dir / template_name
        if source.exists():
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

