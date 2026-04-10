"""System and environment export helpers."""

from __future__ import annotations


def build_system_preview(ai_context_preview: dict, structure_preview: dict) -> dict:
    """Build the `system` category payload from existing AI context/structure preview data."""
    entities_count = structure_preview.get("entities_count")
    devices_count = structure_preview.get("devices_count")
    areas_count = structure_preview.get("areas_count")

    readable = all(isinstance(value, int) for value in (entities_count, devices_count, areas_count))
    reachable = bool(structure_preview.get("entities_available"))
    token_configured = bool(structure_preview.get("token_configured"))
    entities_http_status = structure_preview.get("entities_http_status")

    if readable:
        status = "available"
        reason = "counts readable from structure preview"
    elif entities_http_status in (401, 403):
        status = "unavailable"
        reason = "token configured but unauthorized" if token_configured else "no token configured"
    elif reachable:
        status = "unavailable"
        reason = "structure endpoint reachable but not readable"
    else:
        status = "unavailable"
        reason = "structure endpoint not reachable"

    return {
        "status": status,
        "reason": reason,
        "reachability": reachable,
        "readability": readable,
        "system_size": ai_context_preview.get("system_size"),
        "entities": entities_count,
        "devices": devices_count,
        "areas": areas_count,
    }
