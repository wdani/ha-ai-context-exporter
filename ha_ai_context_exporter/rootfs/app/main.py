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
