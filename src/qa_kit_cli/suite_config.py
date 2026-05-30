"""
Suite configuration — manages per-suite QA artifact directories.

Each suite scopes its own test-plan, strategy, traceability matrix,
regression suite, tasks, and release-gate to .qakit/suites/<NNN>-<slug>/.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

SUITE_MEMORY_FILES: list[str] = [
    "qa-strategy.md",
    "test-plan.md",
    "test-tasks.md",
    "traceability-matrix.md",
    "regression-suite.md",
    "release-gate.md",
]


def slugify(name: str) -> str:
    """Convert a suite name to a filesystem-safe slug (lowercase, hyphens only)."""
    s = name.lower()
    # Convert underscores and spaces to hyphens first
    s = re.sub(r"[\s_]+", "-", s)
    # Remove remaining non-alphanumeric characters (except hyphens)
    s = re.sub(r"[^a-z0-9-]", "", s)
    # Collapse multiple hyphens into one
    s = re.sub(r"-{2,}", "-", s)
    s = s.strip("-")
    return s


def _next_suite_number(suites_dir: Path, scheme: str) -> str:
    """Return the next zero-padded 3-digit suite number or timestamp string."""
    if scheme == "timestamp":
        return datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    existing: list[int] = []
    if suites_dir.exists():
        for p in suites_dir.iterdir():
            m = re.match(r"^(\d{3})-", p.name)
            if m:
                existing.append(int(m.group(1)))
    return f"{(max(existing, default=0) + 1):03d}"


@dataclass
class SuiteEntry:
    """Metadata for a single QA suite."""

    id: str
    name: str
    path: str


@dataclass
class SuiteIndex:
    """Index of all suites in .qakit/suites/index.json."""

    suites: list[SuiteEntry] = field(default_factory=list)

    @classmethod
    def load(cls, qakit_dir: Path) -> SuiteIndex:
        """Load the suite index from .qakit/suites/index.json."""
        index_file = qakit_dir / "suites" / "index.json"
        if not index_file.exists():
            return cls()
        raw = json.loads(index_file.read_text(encoding="utf-8"))
        entries = [SuiteEntry(**e) for e in raw.get("suites", [])]
        return cls(suites=entries)

    def save(self, qakit_dir: Path) -> None:
        """Persist the suite index to .qakit/suites/index.json."""
        suites_dir = qakit_dir / "suites"
        suites_dir.mkdir(parents=True, exist_ok=True)
        index_file = suites_dir / "index.json"
        index_file.write_text(
            json.dumps(
                {"suites": [{"id": s.id, "name": s.name, "path": s.path} for s in self.suites]},
                indent=2,
            ),
            encoding="utf-8",
        )

    def get(self, suite_id: str) -> SuiteEntry | None:
        """Return the SuiteEntry with the given ID, or None."""
        return next((s for s in self.suites if s.id == suite_id), None)


def create_suite(
    qakit_dir: Path,
    name: str,
    branch_numbering: str = "sequential",
) -> SuiteEntry:
    """
    Create .qakit/suites/<NNN>-<slug>/ with all SUITE_MEMORY_FILES.

    Updates .qakit/suites/index.json. Returns the new SuiteEntry.
    """
    suites_dir = qakit_dir / "suites"
    suites_dir.mkdir(parents=True, exist_ok=True)

    number = _next_suite_number(suites_dir, branch_numbering)
    slug = slugify(name)
    suite_id = f"{number}-{slug}"
    suite_path = suites_dir / suite_id
    suite_path.mkdir(parents=True, exist_ok=True)

    for filename in SUITE_MEMORY_FILES:
        f = suite_path / filename
        if not f.exists():
            f.write_text(f"# {filename}\n\n", encoding="utf-8")

    index = SuiteIndex.load(qakit_dir)
    entry = SuiteEntry(
        id=suite_id,
        name=name,
        path=str(suite_path.relative_to(qakit_dir.parent)),
    )
    index.suites.append(entry)
    index.save(qakit_dir)

    return entry


def list_suites(qakit_dir: Path) -> list[SuiteEntry]:
    """Return all suites from the index."""
    return SuiteIndex.load(qakit_dir).suites


def get_active_suite(qakit_dir: Path) -> SuiteEntry | None:
    """Read active_suite from config.json and return the matching SuiteEntry."""
    from qa_kit_cli.project_config import ProjectConfig

    cfg = ProjectConfig.load(qakit_dir)
    if not cfg.active_suite:
        return None
    return SuiteIndex.load(qakit_dir).get(cfg.active_suite)
