"""Dashboard export helpers."""

from __future__ import annotations


def build_dashboard_preview(dashboard_preview: dict) -> dict:
    """Build the `dashboard` category payload from existing dashboard preview data."""
    return {
        "dashboards": dashboard_preview.get("dashboards_count"),
        "views": dashboard_preview.get("total_views_count"),
        "cards": dashboard_preview.get("total_cards_count"),
    }
