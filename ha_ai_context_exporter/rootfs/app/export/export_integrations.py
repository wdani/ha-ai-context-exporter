"""Integrations export helpers."""

from __future__ import annotations

CORE_COMPONENTS = {
    "api",
    "auth",
    "automation",
    "config",
    "frontend",
    "persistent_notification",
    "scene",
    "script",
    "system_log",
}

SOURCE_PRIORITY = {
    "config.components": 0,
    "services": 1,
    "states": 2,
}


def _clean_names(values: list[str]) -> list[str]:
    return [item.strip() for item in values if isinstance(item, str) and item.strip()]


def _normalize_integration_name(name: str) -> str:
    """Reduce platform-style names (e.g. mqtt.sensor) to main integration (mqtt)."""
    return name.split(".", 1)[0].strip()


def _kind_for_name(name: str) -> str:
    if name in CORE_COMPONENTS:
        return "core_component"
    return "user_integration"


def _upsert_item(items_by_name: dict[str, dict], *, name: str, source: str, derived: bool) -> None:
    if not name:
        return

    existing = items_by_name.get(name)
    if existing is None:
        items_by_name[name] = {
            "name": name,
            "source": source,
            "derived": derived,
            "kind": _kind_for_name(name),
        }
        return

    current_priority = SOURCE_PRIORITY.get(existing["source"], 99)
    new_priority = SOURCE_PRIORITY.get(source, 99)
    if new_priority < current_priority:
        existing["source"] = source
        existing["derived"] = derived


def build_integrations_preview(metadata_preview: dict, domain_preview: dict) -> dict:
    """Build integrations view from config.components with cautious fallback reduction."""
    direct_components = _clean_names(metadata_preview.get("components", []))
    service_domains = _clean_names(metadata_preview.get("services_domains", []))
    states_domains = _clean_names(list((domain_preview.get("domain_counts") or {}).keys()))

    items_by_name: dict[str, dict] = {}

    for raw_name in sorted(direct_components):
        normalized_name = _normalize_integration_name(raw_name)
        _upsert_item(
            items_by_name,
            name=normalized_name,
            source="config.components",
            derived=False,
        )

    for raw_name in sorted(service_domains):
        normalized_name = _normalize_integration_name(raw_name)
        _upsert_item(
            items_by_name,
            name=normalized_name,
            source="services",
            derived=True,
        )

    for raw_name in sorted(states_domains):
        normalized_name = _normalize_integration_name(raw_name)
        _upsert_item(
            items_by_name,
            name=normalized_name,
            source="states",
            derived=True,
        )

    items = sorted(items_by_name.values(), key=lambda item: item["name"])
    top_items = sorted(
        items,
        key=lambda item: (
            0 if item["kind"] == "user_integration" else 1,
            item["name"],
        ),
    )[:10]

    reachability = bool(
        metadata_preview.get("config_available")
        or metadata_preview.get("services_endpoint_reachable")
        or domain_preview.get("states_endpoint_reachable")
    )

    if any(item["source"] == "config.components" for item in items):
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
