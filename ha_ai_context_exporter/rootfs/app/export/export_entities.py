"""Entities export helpers."""

from __future__ import annotations


def build_entities_preview(structure_preview: dict, domain_preview: dict) -> dict:
    """Build the `entities` category payload from existing structure/domain previews."""
    entities_count = structure_preview.get("entities_count")
    top_domains = domain_preview.get("top_domains", [])
    states_http_status = domain_preview.get("states_http_status")

    reachable = bool(structure_preview.get("entities_available")) or bool(
        domain_preview.get("states_endpoint_reachable")
    )
    readable = isinstance(entities_count, int)

    if readable:
        status = "available"
        reason = "states data readable"
    elif states_http_status in (401, 403):
        status = "unavailable"
        reason = "states endpoint not readable (authorization required)"
    elif reachable:
        status = "unavailable"
        reason = "states endpoint reachable but returned no readable data"
    else:
        status = "unavailable"
        reason = "states endpoint not reachable"

    return {
        "status": status,
        "reason": reason,
        "reachability": reachable,
        "readability": readable,
        "count": entities_count,
        "top_domains": top_domains,
    }
