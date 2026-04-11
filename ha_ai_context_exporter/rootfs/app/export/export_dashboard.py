"""Dashboard export helpers."""

from __future__ import annotations


def build_dashboard_preview(dashboard_preview: dict) -> dict:
    """Build the `dashboard` category payload from existing dashboard preview data."""
    dashboards = dashboard_preview.get("dashboards_count")
    views = dashboard_preview.get("total_views_count")
    cards = dashboard_preview.get("total_cards_count")

    values = [dashboards, views, cards]
    readable_values = [value for value in values if isinstance(value, int)]
    readable = len(readable_values) > 0
    full_readable = len(readable_values) == len(values)
    reachable = bool(dashboard_preview.get("dashboards_available"))
    dashboards_http_status = dashboard_preview.get("dashboards_http_status")
    lovelace_http_status = dashboard_preview.get("lovelace_config_http_status")

    if full_readable:
        status = "available"
        reason = "dashboard metadata fully readable"
    elif readable:
        status = "partial"
        reason = "dashboard metadata partially readable"
    elif dashboards_http_status in (401, 403) or lovelace_http_status in (401, 403):
        status = "unavailable"
        reason = "core proxy unauthorized"
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
