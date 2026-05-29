"""Parse --integration-options string into a structured dict."""

from __future__ import annotations

import shlex
from typing import Any


def parse_integration_options(raw: str | None) -> dict[str, Any]:
    """Parse a shell-style options string into a dict.

    '--skills --commands-dir .myagent/cmds' → {'skills': True, 'commands_dir': '.myagent/cmds'}
    """
    if not raw:
        return {}
    try:
        parts = shlex.split(raw)
    except ValueError:
        parts = raw.split()

    result: dict[str, Any] = {}
    i = 0
    while i < len(parts):
        part = parts[i]
        if part.startswith("--"):
            key = part[2:].replace("-", "_")
            if i + 1 < len(parts) and not parts[i + 1].startswith("--"):
                result[key] = parts[i + 1]
                i += 2
            else:
                result[key] = True
                i += 1
        else:
            i += 1
    return result
