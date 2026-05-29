"""Tiny expression resolver for workflow inputs."""

from __future__ import annotations

import re
from typing import Any

_INPUT_EXPR = re.compile(r"\{\{\s*inputs\.([a-zA-Z0-9_]+)\s*\}\}")


def resolve_expressions(value: Any, inputs: dict[str, Any]) -> Any:
    """Resolve {{ inputs.<name> }} expressions in strings recursively."""
    if isinstance(value, str):
        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            return str(inputs.get(key, ""))

        return _INPUT_EXPR.sub(replace, value)
    if isinstance(value, list):
        return [resolve_expressions(item, inputs) for item in value]
    if isinstance(value, dict):
        return {k: resolve_expressions(v, inputs) for k, v in value.items()}
    return value

