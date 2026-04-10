"""Logic export helpers."""

from __future__ import annotations


def build_logic_preview(logic_preview: dict) -> dict:
    """Build the `logic` category payload from existing logic preview data."""
    states_http_status = logic_preview.get("states_http_status")
    reachable = bool(logic_preview.get("states_endpoint_reachable"))
    readable = states_http_status == 200

    token_configured = bool(logic_preview.get("token_configured"))

    if readable:
        status = "available"
        reason = "logic entities readable from states endpoint"
    elif states_http_status in (401, 403):
        status = "unavailable"
        reason = "token configured but unauthorized" if token_configured else "no token configured"
    elif reachable:
        status = "unavailable"
        reason = "states endpoint reachable but not readable"
    else:
        status = "unavailable"
        reason = "states endpoint not reachable"

    return {
        "status": status,
        "reason": reason,
        "reachability": reachable,
        "readability": readable,
        "automations": logic_preview.get("automations_count") if readable else None,
        "scripts": logic_preview.get("scripts_count") if readable else None,
        "scenes": logic_preview.get("scenes_count") if readable else None,
    }
