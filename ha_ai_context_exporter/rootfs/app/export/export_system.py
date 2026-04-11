"""System and environment export helpers."""

from __future__ import annotations


def build_system_preview(ai_context_preview: dict, structure_preview: dict) -> dict:
    """Build the `system` category payload from existing AI context/structure preview data."""
    entities_count = structure_preview.get("entities_count")
    devices_count = structure_preview.get("devices_count")
    areas_count = structure_preview.get("areas_count")

    values = [entities_count, devices_count, areas_count]
    readable_values = [value for value in values if isinstance(value, int)]
    readable = len(readable_values) > 0
    full_readable = len(readable_values) == len(values)
    reachable = bool(structure_preview.get("entities_available"))
    entities_http_status = structure_preview.get("entities_http_status")

    if full_readable:
        status = "available"
        reason = "all system summary counts are readable"
    elif readable:
        status = "partial"
        reason = "system summary is partially readable"
    elif entities_http_status in (401, 403):
        status = "unavailable"
        reason = "core proxy unauthorized"
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
