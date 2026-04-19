"""Entities export helpers."""

from __future__ import annotations

ENTITY_ITEMS_LIMIT = 50
IMPORTANT_ATTRIBUTE_KEYS = (
    "device_class",
    "entity_category",
    "state_class",
    "unit_of_measurement",
)


def _extract_important_attributes(attributes: object) -> dict:
    if not isinstance(attributes, dict):
        return {}

    important_attributes: dict[str, str] = {}
    for key in IMPORTANT_ATTRIBUTE_KEYS:
        value = attributes.get(key)
        if isinstance(value, str):
            important_attributes[key] = value
    return important_attributes


def build_compact_entity_items(states_payload: list) -> list[dict]:
    """Build a small, deterministic entity context slice from /states data."""
    items: list[dict] = []

    for entry in states_payload:
        if not isinstance(entry, dict):
            continue

        entity_id = entry.get("entity_id")
        if not isinstance(entity_id, str) or "." not in entity_id:
            continue

        domain = entity_id.split(".", 1)[0]
        if not domain:
            continue

        state = entry.get("state")
        if not isinstance(state, str):
            continue

        attributes = entry.get("attributes")
        friendly_name = None
        if isinstance(attributes, dict):
            raw_friendly_name = attributes.get("friendly_name")
            if isinstance(raw_friendly_name, str):
                friendly_name = raw_friendly_name

        item = {
            "entity_id": entity_id,
            "domain": domain,
            "state": state,
            "friendly_name": friendly_name,
        }
        important_attributes = _extract_important_attributes(attributes)
        if important_attributes:
            item["important_attributes"] = important_attributes

        items.append(item)

    return sorted(items, key=lambda item: item["entity_id"])[:ENTITY_ITEMS_LIMIT]


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
        reason = "core proxy unauthorized"
    elif reachable:
        status = "unavailable"
        reason = "states endpoint reachable but returned no readable data"
    else:
        status = "unavailable"
        reason = "states endpoint not reachable"

    result = {
        "status": status,
        "reason": reason,
        "reachability": reachable,
        "readability": readable,
        "count": entities_count,
        "top_domains": top_domains,
    }

    entity_items = domain_preview.get("entity_items")
    if readable and states_http_status == 200 and isinstance(entity_items, list):
        result["items"] = entity_items

    return result
