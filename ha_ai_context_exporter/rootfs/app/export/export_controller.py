"""Central export controller for /api/export."""

from __future__ import annotations

from datetime import datetime, timezone

from .export_dashboard import build_dashboard_preview
from .export_entities import build_entities_preview
from .export_integrations import build_integrations_preview
from .export_logic import build_logic_preview
from .export_system import build_system_preview

ALLOWED_MODES = ("quick", "standard", "full")
ALLOWED_VARIANTS = ("A", "B")
ALLOWED_CATEGORIES = (
    "system",
    "entities",
    "areas_devices",
    "logic",
    "dashboard",
    "integrations",
)

DEFAULT_CATEGORIES_BY_VARIANT = {
    "A": list(ALLOWED_CATEGORIES),
    "B": list(ALLOWED_CATEGORIES),
}


class ExportValidationError(ValueError):
    """Validation error used for query parameter handling."""



def _validate_mode(mode: str) -> str:
    if mode not in ALLOWED_MODES:
        allowed = ", ".join(ALLOWED_MODES)
        raise ExportValidationError(
            f"Invalid mode '{mode}'. Allowed values: {allowed}."
        )
    return mode



def _validate_variant(variant: str) -> str:
    if variant not in ALLOWED_VARIANTS:
        allowed = ", ".join(ALLOWED_VARIANTS)
        raise ExportValidationError(
            f"Invalid variant '{variant}'. Allowed values: {allowed}."
        )
    return variant



def _parse_categories(categories_raw: str | None, variant: str) -> list[str]:
    if categories_raw is None:
        return list(DEFAULT_CATEGORIES_BY_VARIANT[variant])

    parsed = [item.strip() for item in categories_raw.split(",")]
    if any(not item for item in parsed):
        raise ExportValidationError(
            "Invalid categories list. Use a comma-separated list without empty values."
        )

    invalid = [item for item in parsed if item not in ALLOWED_CATEGORIES]
    if invalid:
        allowed = ", ".join(ALLOWED_CATEGORIES)
        invalid_list = ", ".join(invalid)
        raise ExportValidationError(
            f"Invalid categories '{invalid_list}'. Allowed values: {allowed}."
        )

    deduped: list[str] = []
    for item in parsed:
        if item not in deduped:
            deduped.append(item)
    return deduped



def _build_environment(access_preview: dict, section_readability: bool) -> dict:
    reachability = bool(access_preview.get("core_root_reachable"))
    if section_readability:
        reason = "at least one export category is readable"
    elif reachability:
        reason = "core reachable but export categories not readable"
    else:
        reason = "core endpoint not reachable"

    return {
        "container": access_preview.get("container_running"),
        "data_path": access_preview.get("has_data_path"),
        "config_path": access_preview.get("has_config_path"),
        "api_available": access_preview.get("api_based_analysis_possible"),
        "reachability": reachability,
        "readability": section_readability,
        "reason": reason,
    }



def _evaluate_completeness(active_sections: dict) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if not active_sections:
        return "none", warnings

    available = 0
    partial = 0
    for name, section in active_sections.items():
        status = section.get("status")
        if status == "available":
            available += 1
            continue
        if status == "partial":
            partial += 1
            reason = section.get("reason") or "partially readable"
            warnings.append(f"{name}: {reason}")
            continue
        reason = section.get("reason") or "unknown reason"
        warnings.append(f"{name}: {reason}")

    if available == len(active_sections):
        return "complete", warnings
    if available == 0 and partial == 0:
        return "none", warnings
    return "partial", warnings



def _build_areas_devices_section(structure_preview: dict) -> dict:
    areas = structure_preview.get("areas_count")
    devices = structure_preview.get("devices_count")
    values = [areas, devices]
    readable_values = [value for value in values if isinstance(value, int)]
    readable = len(readable_values) > 0
    full_readable = len(readable_values) == len(values)
    reachable = bool(structure_preview.get("areas_available") or structure_preview.get("devices_available"))
    areas_http_status = structure_preview.get("areas_http_status")
    devices_http_status = structure_preview.get("devices_http_status")

    if full_readable:
        status = "available"
        reason = "areas and devices readable from structure preview"
    elif readable:
        status = "partial"
        reason = "areas/devices data partially readable"
    elif areas_http_status in (401, 403) or devices_http_status in (401, 403):
        status = "unavailable"
        reason = "core proxy unauthorized"
    elif reachable:
        status = "unavailable"
        reason = "areas/devices endpoints reachable but not readable"
    else:
        status = "unavailable"
        reason = "areas/devices endpoints not reachable"

    return {
        "status": status,
        "reason": reason,
        "reachability": reachable,
        "readability": readable,
        "areas": areas,
        "devices": devices,
    }





def build_export_payload(
    *,
    mode: str,
    variant: str,
    categories_raw: str | None,
    providers: dict,
) -> dict:
    """Build validated export payload for /api/export."""
    normalized_mode = _validate_mode(mode)
    normalized_variant = _validate_variant(variant)
    active_categories = _parse_categories(categories_raw, normalized_variant)

    info = providers["get_info"]()
    access_preview = providers["get_access_preview"]()
    ai_context = providers["get_ai_context_preview"]()
    structure_preview = providers["get_structure_preview"]()
    logic_preview = providers["get_logic_preview"]()
    dashboard_preview = providers["get_dashboard_preview"]()
    domain_preview = providers["get_domain_preview"]()
    metadata_preview = providers["get_metadata_preview"]()

    payload = {
        "tool": {
            "name": info.get("name"),
            "version": info.get("version"),
            "addon_slug": providers["addon_slug"],
        },
        "export_format": "ha-ai-context",
        "export_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    active_sections: dict[str, dict] = {}

    if "system" in active_categories:
        section = build_system_preview(ai_context, structure_preview)
        payload["system"] = section
        active_sections["system"] = section

    if "entities" in active_categories:
        section = build_entities_preview(structure_preview, domain_preview)
        payload["entities"] = section
        active_sections["entities"] = section

    if "areas_devices" in active_categories:
        section = _build_areas_devices_section(structure_preview)
        payload["areas_devices"] = section
        active_sections["areas_devices"] = section

    if "logic" in active_categories:
        section = build_logic_preview(logic_preview)
        payload["logic"] = section
        active_sections["logic"] = section

    if "dashboard" in active_categories:
        section = build_dashboard_preview(dashboard_preview)
        payload["dashboard"] = section
        active_sections["dashboard"] = section

    if "integrations" in active_categories:
        section = build_integrations_preview(metadata_preview, domain_preview)
        payload["integrations"] = section
        active_sections["integrations"] = section

    data_completeness, warnings = _evaluate_completeness(active_sections)
    any_readable = any(section.get("readability") for section in active_sections.values())
    payload["environment"] = _build_environment(access_preview, any_readable)

    if data_completeness == "complete":
        discovery_status = "read_only_full_access"
    elif data_completeness == "partial":
        discovery_status = "read_only_partial_access"
    elif payload["environment"].get("reachability"):
        discovery_status = "reachable_not_readable"
    else:
        discovery_status = "limited_access"

    payload["data_completeness"] = data_completeness
    payload["discovery_status"] = discovery_status
    payload["warnings"] = warnings

    payload["meta"] = {
        "mode": normalized_mode,
        "variant": normalized_variant,
        "categories": active_categories,
    }

    return payload
