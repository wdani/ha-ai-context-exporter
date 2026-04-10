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



def _build_environment(access_preview: dict) -> dict:
    return {
        "container": access_preview.get("container_running"),
        "data_path": access_preview.get("has_data_path"),
        "config_path": access_preview.get("has_config_path"),
        "api_available": access_preview.get("api_based_analysis_possible"),
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

    payload = {
        "tool": {
            "name": info.get("name"),
            "version": info.get("version"),
            "addon_slug": providers["addon_slug"],
        },
        "environment": _build_environment(access_preview),
        "export_format": "ha-ai-context",
        "export_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if "system" in active_categories:
        payload["system"] = build_system_preview(ai_context)
    if "entities" in active_categories:
        payload["entities"] = build_entities_preview(structure_preview, domain_preview)
    if "areas_devices" in active_categories:
        payload["areas_devices"] = {
            "areas": structure_preview.get("areas_count"),
            "devices": structure_preview.get("devices_count"),
        }
    if "logic" in active_categories:
        payload["logic"] = build_logic_preview(logic_preview)
    if "dashboard" in active_categories:
        payload["dashboard"] = build_dashboard_preview(dashboard_preview)
    if "integrations" in active_categories:
        payload["integrations"] = build_integrations_preview()

    payload["meta"] = {
        "mode": normalized_mode,
        "variant": normalized_variant,
        "categories": active_categories,
    }

    return payload
