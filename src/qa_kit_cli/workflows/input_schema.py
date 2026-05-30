"""Workflow input schema: validation, type-coercion, and defaults."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

_TYPE_COERCIONS: dict[str, Callable[[Any], Any]] = {
    "string": str,
    "number": float,
    "boolean": lambda v: v if isinstance(v, bool) else str(v).lower() in ("true", "1", "yes"),
}


def _coerce(value: Any, schema_type: str) -> Any:
    coerce = _TYPE_COERCIONS.get(schema_type)
    if coerce is None:
        return value
    try:
        return coerce(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Cannot coerce {value!r} to type '{schema_type}'") from exc


def validate_and_apply(
    inputs: dict[str, Any],
    schema: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate *inputs* against *schema*; apply defaults; return coerced dict.

    Schema entry keys:
      name (str, required)
      type: string | number | boolean | enum  (default: string)
      required: bool                          (default: false)
      default: any                            (used when input is absent)
      values: list[str]                       (for enum type)
    """
    result: dict[str, Any] = dict(inputs)
    errors: list[str] = []

    for entry in schema:
        name = str(entry.get("name", ""))
        if not name:
            continue
        schema_type = str(entry.get("type", "string"))
        required = bool(entry.get("required", False))
        default = entry.get("default")
        enum_values: list[str] = [str(v) for v in entry.get("values", [])]

        if name not in result:
            if required and default is None:
                errors.append(f"Required input '{name}' is missing.")
                continue
            if default is not None:
                result[name] = default
            else:
                continue

        value = result[name]

        if schema_type == "enum":
            if enum_values and str(value) not in enum_values:
                errors.append(
                    f"Input '{name}' must be one of {enum_values}, got {value!r}."
                )
            else:
                result[name] = str(value)
        else:
            try:
                result[name] = _coerce(value, schema_type)
            except ValueError as exc:
                errors.append(str(exc))

    if errors:
        raise ValueError("Workflow input validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    return result
