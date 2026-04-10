"""Logic export helpers."""

from __future__ import annotations


def build_logic_preview(logic_preview: dict) -> dict:
    """Build the `logic` category payload from existing logic preview data."""
    return {
        "automations": logic_preview.get("automations_count"),
        "scripts": logic_preview.get("scripts_count"),
        "scenes": logic_preview.get("scenes_count"),
    }
