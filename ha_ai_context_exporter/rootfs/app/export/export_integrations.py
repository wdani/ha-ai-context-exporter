"""Integrations export helpers."""

from __future__ import annotations


def build_integrations_preview() -> dict:
    """Return a stable read-only placeholder until integrations discovery exists."""
    return {
        "status": "not_available_yet",
        "note": "No dedicated integrations preview source is available in this step.",
    }
