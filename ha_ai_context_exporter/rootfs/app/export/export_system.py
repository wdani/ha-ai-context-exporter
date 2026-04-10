"""System and environment export helpers."""

from __future__ import annotations


def build_system_preview(ai_context_preview: dict) -> dict:
    """Build the `system` category payload from existing AI context preview data."""
    return {
        "system_size": ai_context_preview.get("system_size"),
        "entities": ai_context_preview.get("entities_count"),
        "devices": ai_context_preview.get("devices_count"),
        "areas": ai_context_preview.get("areas_count"),
    }
