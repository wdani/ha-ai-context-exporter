"""Dashboard export helpers."""

from __future__ import annotations


def build_dashboard_preview(dashboard_preview: dict) -> dict:
    """Build the `dashboard` category payload from existing dashboard preview data."""
    dashboards = dashboard_preview.get("dashboards_count")
    views = dashboard_preview.get("total_views_count")
    cards = dashboard_preview.get("total_cards_count")

    reachable = bool(dashboard_preview.get("dashboards_available"))
    readable = any(isinstance(value, int) for value in (dashboards, views, cards))

    if readable:
        status = "available"
        reason = "dashboard metadata readable"
    elif reachable:
        status = "unavailable"
        reason = "dashboard endpoint reachable but not readable"
    else:
        status = "unavailable"
        reason = "dashboard endpoint not reachable"

    return {
        "status": status,
        "reason": reason,
        "reachability": reachable,
        "readability": readable,
        "dashboards": dashboards,
        "views": views,
        "cards": cards,
    }
