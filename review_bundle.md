# Review Bundle

## Zusammenfassung

- Erste echte Integrations-Discovery implementiert: primär `config.components`, ergänzt durch vorsichtige Ableitung aus `services` und `states`.
- Integrationsausgabe enthält jetzt strukturierte Felder (`count`, `items`, `top_items`) plus konsistente Semantik (`available`/`partial`/`unavailable`).
- Export-Controller nutzt nun echte Integrationsdaten statt Platzhalter.
- Version auf `0.0.6` erhöht und in zentraler Version + config konsistent nachgezogen.
- AI-Statusdokumente und Changelog auf den neuen Stand aktualisiert.

## Vollständige Inhalte aller geänderten Dateien

### `ha_ai_context_exporter/rootfs/app/version.py`
```python
"""Single source of truth for application version."""

VERSION = "0.0.6"

```

### `ha_ai_context_exporter/config.yaml`
```yaml
name: "HA AI Context Exporter"
version: "0.0.6"
slug: "ha_ai_context_exporter"
description: "Minimal scaffold for future Home Assistant AI context export features"
arch:
  - amd64
  - aarch64
  - armv7
startup: services
boot: manual
ingress: true
homeassistant_api: true
ingress_port: 8099
panel_icon: mdi:robot-outline
init: false
options: {}
schema: {}

```

### `ha_ai_context_exporter/rootfs/app/main.py`
```python
#!/usr/bin/env python3
"""Minimal backend scaffold for the HA AI Context Exporter add-on."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from export.export_controller import ExportValidationError, build_export_payload
from version import VERSION
from export.export_renderers import (
    build_download_filename,
    render_export_json_bytes,
    render_export_markdown_bytes,
    validate_download_format,
)

APP_NAME = "HA AI Context Exporter"
APP_VERSION = VERSION
APP_SLUG = "ha_ai_context_exporter"
CORE_API_BASE_CANDIDATES = (
    "http://supervisor/core/api",
    "http://homeassistant:8123/api",
    "http://127.0.0.1:8123/api",
)
REQUEST_TIMEOUT_SECONDS = 5.0
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "8099"))
WEB_DIR = Path(__file__).resolve().parent / "web"
APP_INFO = {
    "name": APP_NAME,
    "version": APP_VERSION,
    "status": "scaffold-ready",
}


def get_app_info() -> dict:
    """Return basic app metadata for reuse in other endpoints."""
    return dict(APP_INFO)




def get_supervisor_token() -> str | None:
    """Return supervisor token from environment, if available."""
    value = os.getenv("SUPERVISOR_TOKEN", "")
    token = value.strip()
    return token if token else None


def should_attach_supervisor_token(url: str) -> bool:
    """Allow supervisor token only for Home Assistant core proxy URL."""
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme == "http" and parsed.netloc == "supervisor" and parsed.path.startswith("/core/")


def build_local_get_headers(url: str) -> dict[str, str]:
    """Build headers for local GET requests without leaking tokens to disallowed targets."""
    token = get_supervisor_token()
    if token and should_attach_supervisor_token(url):
        return {"Authorization": f"Bearer {token}"}
    return {}

def is_running_in_container() -> bool:
    """Best-effort container detection without external dependencies."""
    if Path("/.dockerenv").exists():
        return True

    cgroup_path = Path("/proc/1/cgroup")
    if cgroup_path.exists():
        content = cgroup_path.read_text(encoding="utf-8", errors="ignore")
        markers = ("docker", "containerd", "kubepods", "podman")
        return any(marker in content for marker in markers)

    return False


# system discovery

def get_ha_base_info() -> dict:
    """Return only harmless HA-near base diagnostics."""
    path_checks = ["/data", "/config", "/etc/hosts", "/app"]
    path_status = [{"path": p, "exists": Path(p).exists()} for p in path_checks]

    looks_like_ha_addon = is_running_in_container() and any(
        item["exists"] for item in path_status if item["path"] in ("/data", "/config", "/app")
    )

    return {
        "addon_slug": APP_SLUG,
        "version": APP_VERSION,
        "looks_like_ha_addon_environment": looks_like_ha_addon,
        "paths": path_status,
    }


def get_ha_detect_info() -> dict:
    """Return minimal read-only Home Assistant add-on readiness hints."""
    data_exists = Path("/data").exists()
    config_exists = Path("/config").exists()
    app_exists = Path("/app").exists()

    options_candidates = (
        "/data/options.json",
        "/data/options.yaml",
        "/data/options.yml",
    )
    options_file_exists = any(Path(path).exists() for path in options_candidates)

    looks_ready_for_next_ha_step = (
        is_running_in_container() and data_exists and config_exists and app_exists
    )

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "addon_slug": APP_SLUG,
        "data_exists": data_exists,
        "config_exists": config_exists,
        "app_exists": app_exists,
        "options_file_exists": options_file_exists,
        "looks_ready_for_next_ha_step": looks_ready_for_next_ha_step,
    }


# connectivity

def probe_local_url(url: str, path: str) -> dict:
    """Short unauthenticated local probe request (GET only)."""
    request_url = f"{url.rstrip('/')}{path}"
    request = urllib.request.Request(request_url, method="GET", headers=build_local_get_headers(request_url))

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            status = response.getcode()
            return {"reachable": status in (200, 401, 403), "http_status": status}
    except urllib.error.HTTPError as error:
        return {
            "reachable": error.code in (401, 403),
            "http_status": error.code,
        }
    except (urllib.error.URLError, TimeoutError):
        return {"reachable": False, "http_status": None}


def fetch_json_on_200(url: str, path: str) -> object | None:
    """Fetch JSON payload only when endpoint returns HTTP 200."""
    request_url = f"{url.rstrip('/')}{path}"
    request = urllib.request.Request(request_url, method="GET", headers=build_local_get_headers(request_url))

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            if response.getcode() != 200:
                return None
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def probe_core_root(url: str) -> dict:
    return probe_local_url(url, "/")


def probe_config_endpoint(url: str) -> dict:
    return probe_local_url(url, "/config")


def probe_states_endpoint(url: str) -> dict:
    return probe_local_url(url, "/states")


def probe_services_endpoint(url: str) -> dict:
    return probe_local_url(url, "/services")


def probe_areas_endpoint(url: str) -> dict:
    return probe_local_url(url, "/areas")


def probe_devices_endpoint(url: str) -> dict:
    return probe_local_url(url, "/devices")


def probe_dashboards_endpoint(url: str) -> dict:
    return probe_local_url(url, "/lovelace/dashboards")


def probe_lovelace_config_endpoint(url: str) -> dict:
    return probe_local_url(url, "/lovelace/config")


def check_local_core_candidate(url: str) -> dict:
    result = probe_core_root(url)
    return {"url": url, "reachable": result["reachable"], "http_status": result["http_status"]}


def load_states_snapshot_if_200(url: str, states_probe: dict | None = None) -> list | None:
    """Load /api/states payload only when probe confirms HTTP 200."""
    probe = states_probe if states_probe is not None else probe_states_endpoint(url)
    if probe.get("http_status") != 200:
        return None

    payload = fetch_json_on_200(url, "/states")
    return payload if isinstance(payload, list) else None


def get_ha_core_check_info() -> dict:
    data_exists = Path("/data").exists()
    config_exists = Path("/config").exists()
    app_exists = Path("/app").exists()

    prerequisites_look_ok = is_running_in_container() and data_exists and config_exists and app_exists

    checked_candidate = {"url": None, "reachable": False, "http_status": None}
    for candidate in CORE_API_BASE_CANDIDATES:
        result = check_local_core_candidate(candidate)
        checked_candidate = result
        if result["reachable"]:
            break

    next_safe_core_step_possible = prerequisites_look_ok and checked_candidate["reachable"]

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "addon_slug": APP_SLUG,
        "prerequisites_look_ok": prerequisites_look_ok,
        "local_core_url_candidate_checked": checked_candidate["url"],
        "local_core_candidate_reachable": checked_candidate["reachable"],
        "local_core_candidate_http_status": checked_candidate["http_status"],
        "next_safe_core_step_possible": next_safe_core_step_possible,
    }


def get_ha_capabilities_info() -> dict:
    best_candidate = CORE_API_BASE_CANDIDATES[0]
    api_root_reachable = False
    states_endpoint_reachable = False
    services_endpoint_reachable = False

    for candidate in CORE_API_BASE_CANDIDATES:
        api_root = probe_core_root(candidate)
        if not api_root["reachable"]:
            continue

        best_candidate = candidate
        api_root_reachable = True
        states_endpoint_reachable = probe_states_endpoint(candidate)["reachable"]
        services_endpoint_reachable = probe_services_endpoint(candidate)["reachable"]
        break

    safe_to_attempt_metadata_step = api_root_reachable and (
        states_endpoint_reachable or services_endpoint_reachable
    )

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "addon_slug": APP_SLUG,
        "core_host_candidate": best_candidate,
        "api_root_reachable": api_root_reachable,
        "states_endpoint_reachable": states_endpoint_reachable,
        "services_endpoint_reachable": services_endpoint_reachable,
        "safe_to_attempt_metadata_step": safe_to_attempt_metadata_step,
    }


# metadata

def get_ha_metadata_preview() -> dict:
    core_host_candidate = CORE_API_BASE_CANDIDATES[0]
    config_available = False
    states_endpoint_reachable = False
    services_endpoint_reachable = False
    states_count = None
    services_domain_count = None
    home_assistant_version = None
    config_http_status = None
    services_http_status = None
    components: list[str] = []
    services_domains: list[str] = []

    for candidate in CORE_API_BASE_CANDIDATES:
        if not probe_core_root(candidate)["reachable"]:
            continue

        core_host_candidate = candidate
        config_probe = probe_config_endpoint(candidate)
        states_probe = probe_states_endpoint(candidate)
        services_probe = probe_services_endpoint(candidate)

        config_http_status = config_probe["http_status"]
        services_http_status = services_probe["http_status"]
        config_available = config_probe["reachable"]
        states_endpoint_reachable = states_probe["reachable"]
        services_endpoint_reachable = services_probe["reachable"]

        if config_probe["http_status"] == 200:
            config_payload = fetch_json_on_200(candidate, "/config")
            if isinstance(config_payload, dict):
                version_value = config_payload.get("version")
                if isinstance(version_value, str):
                    home_assistant_version = version_value
                components_value = config_payload.get("components")
                if isinstance(components_value, list):
                    components = sorted({item.strip() for item in components_value if isinstance(item, str) and item.strip()})

        if states_probe["http_status"] == 200:
            states_payload = fetch_json_on_200(candidate, "/states")
            if isinstance(states_payload, list):
                states_count = len(states_payload)

        if services_probe["http_status"] == 200:
            services_payload = fetch_json_on_200(candidate, "/services")
            if isinstance(services_payload, list):
                services_domain_count = len(services_payload)
                services_domains = sorted({item.get("domain").strip() for item in services_payload if isinstance(item, dict) and isinstance(item.get("domain"), str) and item.get("domain").strip()})

        break

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "addon_slug": APP_SLUG,
        "core_host_candidate": core_host_candidate,
        "config_available": config_available,
        "states_endpoint_reachable": states_endpoint_reachable,
        "services_endpoint_reachable": services_endpoint_reachable,
        "states_count": states_count,
        "services_domain_count": services_domain_count,
        "home_assistant_version": home_assistant_version,
        "config_http_status": config_http_status,
        "services_http_status": services_http_status,
        "components": components,
        "services_domains": services_domains,
    }


def get_ha_domain_preview() -> dict:
    core_host_candidate = CORE_API_BASE_CANDIDATES[0]
    states_endpoint_reachable = False
    states_http_status = None
    domain_counts: dict[str, int] = {}

    for candidate in CORE_API_BASE_CANDIDATES:
        if not probe_core_root(candidate)["reachable"]:
            continue

        core_host_candidate = candidate
        states_probe = probe_states_endpoint(candidate)
        states_endpoint_reachable = states_probe["reachable"]
        states_http_status = states_probe["http_status"]

        states_payload = load_states_snapshot_if_200(candidate, states_probe)
        if states_payload is not None:
            for entry in states_payload:
                if not isinstance(entry, dict):
                    continue
                entity_id = entry.get("entity_id")
                if not isinstance(entity_id, str) or "." not in entity_id:
                    continue
                domain = entity_id.split(".", 1)[0]
                if domain:
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
        break

    top_domains = sorted(domain_counts.items(), key=lambda item: item[1], reverse=True)[:10]

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "addon_slug": APP_SLUG,
        "core_host_candidate": core_host_candidate,
        "states_endpoint_reachable": states_endpoint_reachable,
        "states_http_status": states_http_status,
        "domain_counts": domain_counts,
        "top_domains": [{"domain": domain, "count": count} for domain, count in top_domains],
    }


# structure

def get_ha_structure_preview() -> dict:
    core_host_candidate = CORE_API_BASE_CANDIDATES[0]

    areas_available = False
    devices_available = False
    entities_available = False

    areas_count = None
    devices_count = None
    entities_count = None

    for candidate in CORE_API_BASE_CANDIDATES:
        if not probe_core_root(candidate)["reachable"]:
            continue

        core_host_candidate = candidate
        areas_probe = probe_areas_endpoint(candidate)
        devices_probe = probe_devices_endpoint(candidate)
        entities_probe = probe_states_endpoint(candidate)

        areas_available = areas_probe["reachable"]
        devices_available = devices_probe["reachable"]
        entities_available = entities_probe["reachable"]

        if areas_probe["http_status"] == 200:
            areas_payload = fetch_json_on_200(candidate, "/areas")
            if isinstance(areas_payload, list):
                areas_count = len(areas_payload)

        if devices_probe["http_status"] == 200:
            devices_payload = fetch_json_on_200(candidate, "/devices")
            if isinstance(devices_payload, list):
                devices_count = len(devices_payload)

        entities_payload = load_states_snapshot_if_200(candidate, entities_probe)
        if entities_payload is not None:
            entities_count = len(entities_payload)

        break

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "addon_slug": APP_SLUG,
        "core_host_candidate": core_host_candidate,
        "areas_available": areas_available,
        "devices_available": devices_available,
        "entities_available": entities_available,
        "areas_count": areas_count,
        "devices_count": devices_count,
        "entities_count": entities_count,
        "areas_http_status": areas_probe["http_status"] if "areas_probe" in locals() else None,
        "devices_http_status": devices_probe["http_status"] if "devices_probe" in locals() else None,
        "entities_http_status": entities_probe["http_status"] if "entities_probe" in locals() else None,
    }


# logic

def get_ha_logic_preview() -> dict:
    """Return read-only logic area statistics derived from /api/states."""
    core_host_candidate = CORE_API_BASE_CANDIDATES[0]
    states_endpoint_reachable = False
    states_http_status = None

    automations_count = 0
    scripts_count = 0
    scenes_count = 0

    for candidate in CORE_API_BASE_CANDIDATES:
        if not probe_core_root(candidate)["reachable"]:
            continue

        core_host_candidate = candidate
        states_probe = probe_states_endpoint(candidate)
        states_endpoint_reachable = states_probe["reachable"]
        states_http_status = states_probe["http_status"]

        states_payload = load_states_snapshot_if_200(candidate, states_probe)
        if states_payload is not None:
            for entry in states_payload:
                if not isinstance(entry, dict):
                    continue
                entity_id = entry.get("entity_id")
                if not isinstance(entity_id, str):
                    continue
                if entity_id.startswith("automation."):
                    automations_count += 1
                elif entity_id.startswith("script."):
                    scripts_count += 1
                elif entity_id.startswith("scene."):
                    scenes_count += 1
        break

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "addon_slug": APP_SLUG,
        "core_host_candidate": core_host_candidate,
        "states_endpoint_reachable": states_endpoint_reachable,
        "states_http_status": states_http_status,
        "automations_count": automations_count,
        "scripts_count": scripts_count,
        "scenes_count": scenes_count,
    }


# ui

def get_ha_dashboard_preview() -> dict:
    """Return cautious dashboard structure preview without exporting configurations."""
    core_host_candidate = CORE_API_BASE_CANDIDATES[0]

    dashboards_available = False
    dashboards_count = None
    total_views_count = None
    total_cards_count = None
    detected_view_types: list[str] = []

    for candidate in CORE_API_BASE_CANDIDATES:
        if not probe_core_root(candidate)["reachable"]:
            continue

        core_host_candidate = candidate

        dashboards_probe = probe_dashboards_endpoint(candidate)
        lovelace_config_probe = probe_lovelace_config_endpoint(candidate)

        dashboards_available = dashboards_probe["reachable"] or lovelace_config_probe["reachable"]

        if dashboards_probe["http_status"] == 200:
            dashboards_payload = fetch_json_on_200(candidate, "/lovelace/dashboards")
            if isinstance(dashboards_payload, list):
                dashboards_count = len(dashboards_payload)

        if lovelace_config_probe["http_status"] == 200:
            config_payload = fetch_json_on_200(candidate, "/lovelace/config")
            if isinstance(config_payload, dict):
                views = config_payload.get("views")
                if isinstance(views, list):
                    total_views_count = len(views)
                    cards_total = 0
                    view_types: set[str] = set()

                    for view in views:
                        if not isinstance(view, dict):
                            continue
                        cards = view.get("cards")
                        if isinstance(cards, list):
                            cards_total += len(cards)
                        view_type = view.get("type")
                        if isinstance(view_type, str) and view_type:
                            view_types.add(view_type)

                    total_cards_count = cards_total
                    detected_view_types = sorted(view_types)

                    if dashboards_count is None:
                        dashboards_count = 1

        break

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "addon_slug": APP_SLUG,
        "core_host_candidate": core_host_candidate,
        "dashboards_available": dashboards_available,
        "dashboards_count": dashboards_count,
        "total_views_count": total_views_count,
        "total_cards_count": total_cards_count,
        "detected_view_types": detected_view_types,
        "dashboards_http_status": dashboards_probe["http_status"] if "dashboards_probe" in locals() else None,
        "lovelace_config_http_status": lovelace_config_probe["http_status"] if "lovelace_config_probe" in locals() else None,
    }


def get_ha_ai_context_preview() -> dict:
    """Combine existing discovery previews into a compact AI-facing summary."""
    structure = get_ha_structure_preview()
    logic = get_ha_logic_preview()
    dashboard = get_ha_dashboard_preview()
    domain = get_ha_domain_preview()

    entities_count = structure.get("entities_count")

    if isinstance(entities_count, int):
        if entities_count < 100:
            system_size = "small"
        elif entities_count < 500:
            system_size = "medium"
        else:
            system_size = "large"
    else:
        system_size = "unknown"

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "addon_slug": APP_SLUG,
        "system_size": system_size,
        "entities_count": entities_count,
        "devices_count": structure.get("devices_count"),
        "areas_count": structure.get("areas_count"),
        "automations_count": logic.get("automations_count"),
        "scripts_count": logic.get("scripts_count"),
        "scenes_count": logic.get("scenes_count"),
        "dashboards_count": dashboard.get("dashboards_count"),
        "views_count": dashboard.get("total_views_count"),
        "cards_count": dashboard.get("total_cards_count"),
        "top_domains": domain.get("top_domains", []),
    }



def get_ai_export_preview() -> dict:
    """Return a structured preview payload for a future AI export."""
    structure = get_ha_structure_preview()
    logic = get_ha_logic_preview()
    dashboard = get_ha_dashboard_preview()
    domain = get_ha_domain_preview()

    entities_count = structure.get("entities_count")
    if isinstance(entities_count, int):
        if entities_count < 100:
            system_size = "small"
        elif entities_count < 500:
            system_size = "medium"
        else:
            system_size = "large"
    else:
        system_size = "unknown"

    return {
        "tool": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "addon_slug": APP_SLUG,
        },
        "environment": {
            "container": is_running_in_container(),
            "data_path": Path("/data").exists(),
            "config_path": Path("/config").exists(),
            "api_available": bool(
                structure.get("entities_available")
                or domain.get("states_endpoint_reachable")
            ),
        },
        "system_summary": {
            "system_size": system_size,
            "entities": structure.get("entities_count"),
            "devices": structure.get("devices_count"),
            "areas": structure.get("areas_count"),
        },
        "logic_summary": {
            "automations": logic.get("automations_count"),
            "scripts": logic.get("scripts_count"),
            "scenes": logic.get("scenes_count"),
        },
        "dashboard_summary": {
            "dashboards": dashboard.get("dashboards_count"),
            "views": dashboard.get("total_views_count"),
            "cards": dashboard.get("total_cards_count"),
        },
        "top_domains": domain.get("top_domains", []),
    }


def get_ha_access_preview() -> dict:
    """Return a compact, read-only preview of currently accessible HA data sources."""
    container_running = is_running_in_container()
    has_data_path = Path("/data").exists()
    has_app_path = Path("/app").exists()
    has_config_path = Path("/config").exists()

    core_host_candidate = None
    core_root_reachable = False
    states_endpoint_reachable = False
    services_endpoint_reachable = False
    dashboards_endpoint_reachable = False
    lovelace_config_endpoint_reachable = False

    for candidate in CORE_API_BASE_CANDIDATES:
        root_probe = probe_core_root(candidate)
        if not root_probe["reachable"]:
            continue

        core_host_candidate = candidate
        core_root_reachable = True
        states_endpoint_reachable = probe_states_endpoint(candidate)["reachable"]
        services_endpoint_reachable = probe_services_endpoint(candidate)["reachable"]
        dashboards_endpoint_reachable = probe_dashboards_endpoint(candidate)["reachable"]
        lovelace_config_endpoint_reachable = probe_lovelace_config_endpoint(candidate)["reachable"]
        break

    file_config_access_possible = has_config_path
    api_based_analysis_possible = core_root_reachable and (
        states_endpoint_reachable or services_endpoint_reachable
    )
    dashboard_analysis_possible = dashboards_endpoint_reachable or lovelace_config_endpoint_reachable

    if file_config_access_possible and api_based_analysis_possible and dashboard_analysis_possible:
        export_prerequisites_summary = "file+api+dashboard-ready"
    elif api_based_analysis_possible and dashboard_analysis_possible:
        export_prerequisites_summary = "api+dashboard-ready (no /config)"
    elif api_based_analysis_possible:
        export_prerequisites_summary = "api-only-ready"
    elif file_config_access_possible:
        export_prerequisites_summary = "file-only-ready"
    else:
        export_prerequisites_summary = "limited-access"

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "addon_slug": APP_SLUG,
        "container_running": container_running,
        "has_data_path": has_data_path,
        "has_app_path": has_app_path,
        "has_config_path": has_config_path,
        "core_host_candidate": core_host_candidate,
        "core_root_reachable": core_root_reachable,
        "states_endpoint_reachable": states_endpoint_reachable,
        "services_endpoint_reachable": services_endpoint_reachable,
        "dashboards_endpoint_reachable": dashboards_endpoint_reachable,
        "lovelace_config_endpoint_reachable": lovelace_config_endpoint_reachable,
        "file_config_access_possible": file_config_access_possible,
        "api_based_analysis_possible": api_based_analysis_possible,
        "dashboard_analysis_possible": dashboard_analysis_possible,
        "export_prerequisites_summary": export_prerequisites_summary,
    }




def get_ha_auth_debug_info() -> dict:
    """Return token-safe diagnostics for core proxy auth/readability."""
    core_url = CORE_API_BASE_CANDIDATES[0]

    def status_reason(http_status: int | None, reachable: bool, readable: bool) -> str:
        if readable:
            return "endpoint readable"
        if http_status in (401, 403):
            return "core proxy unauthorized"
        if reachable:
            return "endpoint reachable but not readable"
        return "core proxy unreachable"

    core_probe = probe_core_root(core_url)
    states_probe = probe_states_endpoint(core_url)
    config_probe = probe_config_endpoint(core_url)

    return {
        "core_proxy": {
            "reachability": core_probe["reachable"],
            "readability": core_probe.get("http_status") == 200,
            "http_status": core_probe.get("http_status"),
            "reason": status_reason(core_probe.get("http_status"), core_probe["reachable"], core_probe.get("http_status") == 200),
        },
        "states": {
            "reachability": states_probe["reachable"],
            "readability": states_probe.get("http_status") == 200,
            "http_status": states_probe.get("http_status"),
            "reason": status_reason(states_probe.get("http_status"), states_probe["reachable"], states_probe.get("http_status") == 200),
        },
        "config": {
            "reachability": config_probe["reachable"],
            "readability": config_probe.get("http_status") == 200,
            "http_status": config_probe.get("http_status"),
            "reason": status_reason(config_probe.get("http_status"), config_probe["reachable"], config_probe.get("http_status") == 200),
        },
    }

class RequestHandler(BaseHTTPRequestHandler):
    def _normalize_request_path(self, path: str) -> str:
        """Best-effort normalization for ingress-prefixed paths."""
        clean_path = path.split("?", 1)[0]

        ingress_prefix = "/api/hassio_ingress/"
        if clean_path.startswith(ingress_prefix):
            remainder = clean_path[len(ingress_prefix) :]
            # Expected: <token>/<target-path>
            parts = remainder.split("/", 1)
            if len(parts) == 2:
                target = "/" + parts[1]
                return target if target != "//" else "/"

        return clean_path

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_query_error(self, message: str) -> None:
        self._send_json(
            {
                "error": "invalid_query_parameter",
                "message": message,
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    def _send_download_bytes(self, content: bytes, content_type: str, filename: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(content)

    def _get_single_query_value(self, query: dict[str, list[str]], name: str) -> str | None:
        values = query.get(name)
        if values is None:
            return None
        if len(values) != 1:
            raise ExportValidationError(
                f"Query parameter '{name}' must be provided once."
            )
        return values[0]

    def _build_export_payload_from_query(self, query: dict[str, list[str]]) -> dict:
        mode = self._get_single_query_value(query, "mode") or "standard"
        variant = self._get_single_query_value(query, "variant") or "A"
        categories_raw = self._get_single_query_value(query, "categories")

        return build_export_payload(
            mode=mode,
            variant=variant,
            categories_raw=categories_raw,
            providers={
                "get_info": get_app_info,
                "get_access_preview": get_ha_access_preview,
                "get_ai_context_preview": get_ha_ai_context_preview,
                "get_structure_preview": get_ha_structure_preview,
                "get_logic_preview": get_ha_logic_preview,
                "get_dashboard_preview": get_ha_dashboard_preview,
                "get_domain_preview": get_ha_domain_preview,
                "get_metadata_preview": get_ha_metadata_preview,
                "addon_slug": APP_SLUG,
            },
        )

    def do_GET(self) -> None:  # noqa: N802
        normalized_path = self._normalize_request_path(self.path)
        print(f"GET {self.path} -> {normalized_path}")

        if normalized_path == "/health":
            self._send_json({"status": "ok"})
            return
        if normalized_path == "/api/info":
            self._send_json(get_app_info())
            return
        if normalized_path == "/api/system":
            self._send_json(
                {
                    "name": APP_NAME,
                    "version": APP_VERSION,
                    "port": PORT,
                    "in_container": is_running_in_container(),
                    "working_directory": os.getcwd(),
                }
            )
            return
        if normalized_path == "/api/ha-base":
            self._send_json(get_ha_base_info())
            return
        if normalized_path == "/api/ha-detect":
            self._send_json(get_ha_detect_info())
            return
        if normalized_path == "/api/ha-core-check":
            self._send_json(get_ha_core_check_info())
            return
        if normalized_path == "/api/ha-capabilities":
            self._send_json(get_ha_capabilities_info())
            return
        if normalized_path == "/api/ha-metadata-preview":
            self._send_json(get_ha_metadata_preview())
            return
        if normalized_path == "/api/ha-domain-preview":
            self._send_json(get_ha_domain_preview())
            return
        if normalized_path == "/api/ha-structure-preview":
            self._send_json(get_ha_structure_preview())
            return

        if normalized_path == "/api/ha-logic-preview":
            self._send_json(get_ha_logic_preview())
            return
        if normalized_path == "/api/ha-dashboard-preview":
            self._send_json(get_ha_dashboard_preview())
            return
        if normalized_path == "/api/ha-ai-context-preview":
            self._send_json(get_ha_ai_context_preview())
            return
        if normalized_path == "/api/ha-access-preview":
            self._send_json(get_ha_access_preview())
            return
        if normalized_path == "/api/ha-auth-debug":
            self._send_json(get_ha_auth_debug_info())
            return
        if normalized_path == "/api/ai-export-preview":
            self._send_json(get_ai_export_preview())
            return
        if normalized_path == "/api/export":
            parsed_url = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
            try:
                payload = self._build_export_payload_from_query(query)
            except ExportValidationError as error:
                self._send_query_error(str(error))
                return

            self._send_json(payload)
            return
        if normalized_path == "/api/export/download":
            parsed_url = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
            try:
                payload = self._build_export_payload_from_query(query)
                requested_format = self._get_single_query_value(query, "format") or "json"
                download_format = validate_download_format(requested_format)
                mode = payload.get("meta", {}).get("mode", "standard")
                variant = payload.get("meta", {}).get("variant", "A")
                filename = build_download_filename(payload, mode=mode, variant=variant, fmt=download_format)
            except ExportValidationError as error:
                self._send_query_error(str(error))
                return

            if download_format == "json":
                content = render_export_json_bytes(payload)
                self._send_download_bytes(content, "application/json", filename)
                return

            content = render_export_markdown_bytes(payload)
            self._send_download_bytes(content, "text/markdown; charset=utf-8", filename)
            return
        if normalized_path in ("/", "/index.html"):
            self._send_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
            return
        if normalized_path == "/styles.css":
            self._send_file(WEB_DIR / "styles.css", "text/css; charset=utf-8")
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def run() -> None:
    server = HTTPServer((HOST, PORT), RequestHandler)
    print(f"Starting HA AI Context Exporter scaffold on {HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()

```

### `ha_ai_context_exporter/rootfs/app/export/export_controller.py`
```python
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

```

### `ha_ai_context_exporter/rootfs/app/export/export_integrations.py`
```python
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

```

### `docs/ai/AI_CURRENT_STATE.md`
```md
# AI Current State

## Current version
`0.0.6`

## Export status currently observed
- `system = partial`
- `entities = available`
- `logic = available`

## Known limitations
- Integrations discovery now uses a first read-only implementation based on `config.components` with cautious fallbacks from services/states.
- Areas/devices discovery can be incomplete depending on proxy readability and environment.
- Dashboard metadata can be limited depending on endpoint readability.

```

### `docs/ai/AI_CHANGE_HISTORY.md`
```md
## Version 0.0.6
- Goal: replace integrations placeholder with first useful read-only integrations discovery.
- Key changes: direct integrations from `config.components`, cautious derived fallbacks from services/states, compact `items`/`top_items`, and semantic status (`available`/`partial`/`unavailable`).
- Result: `integrations` category can now return real discovered items when readable.
- Next focus: improve coverage quality while keeping compact semantics.

# AI Change History

## Version 0.0.3
- Goal: fix add-on store schema/options parsing issue.
- Key changes: optional token schema retained, default removed (`options: {}`).
- Result: add-on config parse/build compatibility restored.
- Next focus: core-proxy-based authenticated read path.

## Version 0.0.4
- Goal: switch to official Core Proxy auth path.
- Key changes: `homeassistant_api: true`, core-proxy token-safe headers, `/api/ha-auth-debug`.
- Result: stable read-only proxy diagnostics and export flow.
- Next focus: semantics and discovery coverage improvements.

## Version 0.0.5
- Goal: improve discovery semantics and robustness.
- Key changes: explicit proxy API base, longer timeout, partial semantics for key categories.
- Result: more consistent export status evaluation and diagnostics.
- Next focus: ongoing discovery coverage and quality improvements.

```

### `CHANGELOG.md`
```md
# Changelog

All notable changes to this project will be documented in this file.

## 0.0.6 - 2026-04-11

### Changed
- Implement first real read-only integrations discovery using `config.components` as primary source and cautious fallbacks from `services`/`states`.
- Add compact integrations fields: `count`, `items`, `top_items` with consistent semantic status.
- Bump development version from `0.0.5` to `0.0.6`.

## 0.0.5 - 2026-04-11

### Changed
### Docs
- Add persistent AI project documentation set under `docs/ai/`.
- Add AI development workflow doc under `docs/development/AI_WORKFLOW.md`.
- Add contribution guideline under `.github/CONTRIBUTING.md`.
- Archive technical review bundle at `docs/review_bundles/2026-04-11_0.0.5_ai-project-docs.md`.

- Improve discovery semantics and coverage for export categories (`system`, `areas_devices`, `dashboard`) with consistent partial/available/unavailable status handling.
- Make core proxy base explicit (`http://supervisor/core/api`) and avoid path-duplication risks.
- Increase central request timeout to 5 seconds for more robust local proxy reads.

## 0.0.4 - 2026-04-11

### Changed
- Switch primary Home Assistant read access to the official Core Proxy (`homeassistant_api: true`) using `http://supervisor/core/api/...` with `SUPERVISOR_TOKEN` for read-only GET requests.
- Add `/api/ha-auth-debug` endpoint for token-safe proxy/readability diagnostics.
- Bump development version from `0.0.3` to `0.0.4`.

## 0.0.3 - 2026-04-10

### Fixed
- Fix Home Assistant add-on schema/options compatibility by removing the default value for optional `ha_token` (`options: {}` with `schema: ha_token: "password?"`).
- Bump development version from `0.0.2` to `0.0.3`.


```

## Annahmen / Einschränkungen

- In der aktuellen Umgebung liefert der Core Proxy weiterhin HTTP 403; dadurch bleiben Integrationsdaten hier ehrlich als nicht lesbar markiert.
- Die Integrations-Discovery ist bewusst kompakt und vorsichtig: direkte Quelle aus `config.components`, ergänzende Ableitung aus `services`/`states` nur als `derived=true` markiert.
- Keine UI-Änderungen in diesem Schritt.
