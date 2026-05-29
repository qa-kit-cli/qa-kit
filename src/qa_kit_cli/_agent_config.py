"""Derive AGENT_CONFIGS mapping from the integration registry."""

from __future__ import annotations

from qa_kit_cli.integrations import list_integrations


def get_agent_configs() -> dict[str, dict]:  # type: ignore[type-arg]
    """Return {key: config_dict} for all registered integrations."""
    return {i.key: i.config for i in list_integrations()}
