"""Entities export helpers."""

from __future__ import annotations


def build_entities_preview(structure_preview: dict, domain_preview: dict) -> dict:
    """Build the `entities` category payload from existing structure/domain previews."""
    return {
        "entities_count": structure_preview.get("entities_count"),
        "top_domains": domain_preview.get("top_domains", []),
    }
