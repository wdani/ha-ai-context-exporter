"""Dashboard export helpers."""

from __future__ import annotations


def build_dashboard_preview(dashboard_preview: dict) -> dict:
    """Build the `dashboard` category payload from existing dashboard preview data."""
    dashboards = dashboard_preview.get("dashboards_count")
    views = dashboard_preview.get("total_views_count")
    cards = dashboard_preview.get("total_cards_count")

    reachable = bool(dashboard_preview.get("dashboards_available"))
    readable = any(isinstance(value, int) for value in (dashboards, views, cards))
    token_configured = bool(dashboard_preview.get("token_configured"))
    dashboards_http_status = dashboard_preview.get("dashboards_http_status")
    lovelace_http_status = dashboard_preview.get("lovelace_config_http_status")

    if readable:
        status = "available"
        reason = "dashboard metadata readable"
    elif dashboards_http_status in (401, 403) or lovelace_http_status in (401, 403):
        status = "unavailable"
        reason = "token configured but unauthorized" if token_configured else "no token configured"
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
