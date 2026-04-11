"""Integrations export helpers."""

from __future__ import annotations


def _normalize_names(values: list[str]) -> list[str]:
    return sorted({item.strip() for item in values if isinstance(item, str) and item.strip()})


def build_integrations_preview(metadata_preview: dict, domain_preview: dict) -> dict:
    """Build first-pass integrations view from config.components with safe fallbacks."""
    direct_components = _normalize_names(metadata_preview.get("components", []))
    service_domains = _normalize_names(metadata_preview.get("services_domains", []))
    states_domains = _normalize_names(list((domain_preview.get("domain_counts") or {}).keys()))

    items: list[dict] = []
    seen: set[str] = set()

    for name in direct_components:
        seen.add(name)
        items.append({"name": name, "source": "config.components", "derived": False})

    for name in service_domains:
        if name in seen:
            continue
        seen.add(name)
        items.append({"name": name, "source": "services", "derived": True})

    for name in states_domains:
        if name in seen:
            continue
        seen.add(name)
        items.append({"name": name, "source": "states", "derived": True})

    items.sort(key=lambda item: item["name"])
    top_items = items[:10]

    reachability = bool(
        metadata_preview.get("config_available")
        or metadata_preview.get("services_endpoint_reachable")
        or domain_preview.get("states_endpoint_reachable")
    )

    if direct_components:
        status = "available"
        reason = "derived from config.components"
        readability = True
    elif items:
        status = "partial"
        reason = "derived from services/states/config"
        readability = True
    elif metadata_preview.get("config_http_status") in (401, 403):
        status = "unavailable"
        reason = "core proxy unauthorized"
        readability = False
    elif reachability:
        status = "unavailable"
        reason = "no readable payload"
        readability = False
    else:
        status = "unavailable"
        reason = "core proxy unreachable"
        readability = False

    return {
        "status": status,
        "reason": reason,
        "reachability": reachability,
        "readability": readability,
        "count": len(items) if readability else None,
        "items": items,
        "top_items": top_items,
    }
