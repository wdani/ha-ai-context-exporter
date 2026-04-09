# Review Bundle

## Kurz-Zusammenfassung
- Frontend-URL-Erzeugung auf robuste Add-on-Basis umgestellt (`getAddonBaseUrl`, `buildAddonUrl`, `fetchAddonJson`).
- CSS-Laden ebenfalls auf dieselbe robuste Basislogik umgestellt (`applyStylesheet`).
- Backend behält GET-Logging und normalisiert ingress-präfixierte Pfade best effort (`_normalize_request_path`).
- Keine neuen Features/Endpoints; Response-Formate unverändert.

## Geänderte Datei: `ha_ai_context_exporter/rootfs/app/main.py` (vollständiger Inhalt)
```python
#!/usr/bin/env python3
"""Minimal backend scaffold for the HA AI Context Exporter add-on."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

APP_NAME = "HA AI Context Exporter"
APP_VERSION = "0.1.0"
APP_SLUG = "ha_ai_context_exporter"
CORE_URL_CANDIDATES = (
    "http://supervisor/core",
    "http://homeassistant:8123",
    "http://127.0.0.1:8123",
)
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "8099"))
WEB_DIR = Path(__file__).resolve().parent / "web"
APP_INFO = {
    "name": APP_NAME,
    "version": APP_VERSION,
    "status": "scaffold-ready",
}


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
    request = urllib.request.Request(request_url, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=1.5) as response:
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
    request = urllib.request.Request(request_url, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=1.5) as response:
            if response.getcode() != 200:
                return None
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def probe_core_root(url: str) -> dict:
    return probe_local_url(url, "/api/")


def probe_config_endpoint(url: str) -> dict:
    return probe_local_url(url, "/api/config")


def probe_states_endpoint(url: str) -> dict:
    return probe_local_url(url, "/api/states")


def probe_services_endpoint(url: str) -> dict:
    return probe_local_url(url, "/api/services")


def probe_areas_endpoint(url: str) -> dict:
    return probe_local_url(url, "/api/areas")


def probe_devices_endpoint(url: str) -> dict:
    return probe_local_url(url, "/api/devices")


def probe_dashboards_endpoint(url: str) -> dict:
    return probe_local_url(url, "/api/lovelace/dashboards")


def probe_lovelace_config_endpoint(url: str) -> dict:
    return probe_local_url(url, "/api/lovelace/config")


def check_local_core_candidate(url: str) -> dict:
    result = probe_core_root(url)
    return {"url": url, "reachable": result["reachable"], "http_status": result["http_status"]}


def load_states_snapshot_if_200(url: str, states_probe: dict | None = None) -> list | None:
    """Load /api/states payload only when probe confirms HTTP 200."""
    probe = states_probe if states_probe is not None else probe_states_endpoint(url)
    if probe.get("http_status") != 200:
        return None

    payload = fetch_json_on_200(url, "/api/states")
    return payload if isinstance(payload, list) else None


def get_ha_core_check_info() -> dict:
    data_exists = Path("/data").exists()
    config_exists = Path("/config").exists()
    app_exists = Path("/app").exists()

    prerequisites_look_ok = is_running_in_container() and data_exists and config_exists and app_exists

    checked_candidate = {"url": None, "reachable": False, "http_status": None}
    for candidate in CORE_URL_CANDIDATES:
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
    best_candidate = CORE_URL_CANDIDATES[0]
    api_root_reachable = False
    states_endpoint_reachable = False
    services_endpoint_reachable = False

    for candidate in CORE_URL_CANDIDATES:
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
    core_host_candidate = CORE_URL_CANDIDATES[0]
    config_available = False
    states_endpoint_reachable = False
    services_endpoint_reachable = False
    states_count = None
    services_domain_count = None
    home_assistant_version = None

    for candidate in CORE_URL_CANDIDATES:
        if not probe_core_root(candidate)["reachable"]:
            continue

        core_host_candidate = candidate
        config_probe = probe_config_endpoint(candidate)
        states_probe = probe_states_endpoint(candidate)
        services_probe = probe_services_endpoint(candidate)

        config_available = config_probe["reachable"]
        states_endpoint_reachable = states_probe["reachable"]
        services_endpoint_reachable = services_probe["reachable"]

        if config_probe["http_status"] == 200:
            config_payload = fetch_json_on_200(candidate, "/api/config")
            if isinstance(config_payload, dict):
                version_value = config_payload.get("version")
                if isinstance(version_value, str):
                    home_assistant_version = version_value

        if states_probe["http_status"] == 200:
            states_payload = fetch_json_on_200(candidate, "/api/states")
            if isinstance(states_payload, list):
                states_count = len(states_payload)

        if services_probe["http_status"] == 200:
            services_payload = fetch_json_on_200(candidate, "/api/services")
            if isinstance(services_payload, list):
                services_domain_count = len(services_payload)

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
    }


def get_ha_domain_preview() -> dict:
    core_host_candidate = CORE_URL_CANDIDATES[0]
    states_endpoint_reachable = False
    states_http_status = None
    domain_counts: dict[str, int] = {}

    for candidate in CORE_URL_CANDIDATES:
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
    core_host_candidate = CORE_URL_CANDIDATES[0]

    areas_available = False
    devices_available = False
    entities_available = False

    areas_count = None
    devices_count = None
    entities_count = None

    for candidate in CORE_URL_CANDIDATES:
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
            areas_payload = fetch_json_on_200(candidate, "/api/areas")
            if isinstance(areas_payload, list):
                areas_count = len(areas_payload)

        if devices_probe["http_status"] == 200:
            devices_payload = fetch_json_on_200(candidate, "/api/devices")
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
    }


# logic

def get_ha_logic_preview() -> dict:
    """Return read-only logic area statistics derived from /api/states."""
    core_host_candidate = CORE_URL_CANDIDATES[0]
    states_endpoint_reachable = False
    states_http_status = None

    automations_count = 0
    scripts_count = 0
    scenes_count = 0

    for candidate in CORE_URL_CANDIDATES:
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
    core_host_candidate = CORE_URL_CANDIDATES[0]

    dashboards_available = False
    dashboards_count = None
    total_views_count = None
    total_cards_count = None
    detected_view_types: list[str] = []

    for candidate in CORE_URL_CANDIDATES:
        if not probe_core_root(candidate)["reachable"]:
            continue

        core_host_candidate = candidate

        dashboards_probe = probe_dashboards_endpoint(candidate)
        lovelace_config_probe = probe_lovelace_config_endpoint(candidate)

        dashboards_available = dashboards_probe["reachable"] or lovelace_config_probe["reachable"]

        if dashboards_probe["http_status"] == 200:
            dashboards_payload = fetch_json_on_200(candidate, "/api/lovelace/dashboards")
            if isinstance(dashboards_payload, list):
                dashboards_count = len(dashboards_payload)

        if lovelace_config_probe["http_status"] == 200:
            config_payload = fetch_json_on_200(candidate, "/api/lovelace/config")
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

    def do_GET(self) -> None:  # noqa: N802
        normalized_path = self._normalize_request_path(self.path)
        print(f"GET {self.path} -> {normalized_path}")

        if normalized_path == "/health":
            self._send_json({"status": "ok"})
            return
        if normalized_path == "/api/info":
            self._send_json(APP_INFO)
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

## Geänderte Datei: `ha_ai_context_exporter/rootfs/app/web/index.html` (vollständiger Inhalt)
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>HA AI Context Exporter</title>
    <link id="app-stylesheet" rel="stylesheet" href="" />
  </head>
  <body>
    <main class="container">
      <h1>HA AI Context Exporter</h1>
      <p>Initial scaffold for future Home Assistant AI export features.</p>
      <button type="button" disabled>Start export (coming soon)</button>

      <section aria-live="polite"><h2>App info</h2><p id="app-info">Loading app info...</p></section>
      <section aria-live="polite"><h2>System info</h2><p id="system-info">Loading system info...</p></section>
      <section aria-live="polite"><h2>Home Assistant base info</h2><p id="ha-base-info">Loading Home Assistant base info...</p></section>
      <section aria-live="polite"><h2>Home Assistant detection</h2><p id="ha-detect-info">Loading Home Assistant detection...</p></section>
      <section aria-live="polite"><h2>Home Assistant core check</h2><p id="ha-core-check-info">Loading Home Assistant core check...</p></section>
      <section aria-live="polite"><h2>Home Assistant capabilities</h2><p id="ha-capabilities-info">Loading Home Assistant capabilities...</p></section>
      <section aria-live="polite"><h2>Home Assistant metadata preview</h2><p id="ha-metadata-preview-info">Loading Home Assistant metadata preview...</p></section>
      <section aria-live="polite"><h2>Home Assistant domain preview</h2><p id="ha-domain-preview-info">Loading Home Assistant domain preview...</p></section>
      <section aria-live="polite"><h2>Home Assistant structure preview</h2><p id="ha-structure-preview-info">Loading Home Assistant structure preview...</p></section>
      <section aria-live="polite"><h2>Home Assistant logic preview</h2><p id="ha-logic-preview-info">Loading Home Assistant logic preview...</p></section>
      <section aria-live="polite"><h2>Home Assistant dashboard preview</h2><p id="ha-dashboard-preview-info">Loading Home Assistant dashboard preview...</p></section>
      <section aria-live="polite"><h2>AI context preview</h2><p id="ha-ai-context-preview-info">Loading AI context preview...</p></section>
    </main>

    <script>
      function getAddonBaseUrl() {
        const basePath = window.location.pathname.endsWith("/")
          ? window.location.pathname
          : `${window.location.pathname}/`;
        return new URL(basePath, window.location.origin);
      }

      function buildAddonUrl(relativePath) {
        return new URL(relativePath, getAddonBaseUrl());
      }

      async function fetchAddonJson(relativeApiPath) {
        const response = await fetch(buildAddonUrl(relativeApiPath));
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
      }

      function applyStylesheet() {
        document.getElementById("app-stylesheet").href = buildAddonUrl("styles.css").toString();
      }

      async function loadAppInfo() {
        const target = document.getElementById("app-info");
        try {
          const data = await fetchAddonJson("api/info");
          target.textContent = `Name: ${data.name} | Version: ${data.version} | Status: ${data.status}`;
        } catch {
          target.textContent = "Failed to load app info.";
        }
      }

      async function loadSystemInfo() {
        const target = document.getElementById("system-info");
        try {
          const data = await fetchAddonJson("api/system");
          target.textContent = `Name: ${data.name} | Version: ${data.version} | Port: ${data.port} | In container: ${data.in_container} | Working directory: ${data.working_directory}`;
        } catch {
          target.textContent = "Failed to load system info.";
        }
      }

      async function loadHaDetectInfo() {
        const target = document.getElementById("ha-detect-info");
        try {
          const data = await fetchAddonJson("api/ha-detect");
          target.textContent = `Name: ${data.name} | Version: ${data.version} | Slug: ${data.addon_slug} | /data: ${data.data_exists} | /config: ${data.config_exists} | /app: ${data.app_exists} | options file: ${data.options_file_exists} | Ready: ${data.looks_ready_for_next_ha_step}`;
        } catch {
          target.textContent = "Failed to load Home Assistant detection.";
        }
      }

      async function loadHaCoreCheckInfo() {
        const target = document.getElementById("ha-core-check-info");
        try {
          const data = await fetchAddonJson("api/ha-core-check");
          target.textContent = `Name: ${data.name} | Version: ${data.version} | Slug: ${data.addon_slug} | Prerequisites: ${data.prerequisites_look_ok} | Candidate: ${data.local_core_url_candidate_checked} | Reachable: ${data.local_core_candidate_reachable} | HTTP status: ${data.local_core_candidate_http_status} | Next safe step possible: ${data.next_safe_core_step_possible}`;
        } catch {
          target.textContent = "Failed to load Home Assistant core check.";
        }
      }

      async function loadHaCapabilitiesInfo() {
        const target = document.getElementById("ha-capabilities-info");
        try {
          const data = await fetchAddonJson("api/ha-capabilities");
          target.textContent = `Name: ${data.name} | Version: ${data.version} | Slug: ${data.addon_slug} | Core host candidate: ${data.core_host_candidate} | /api/: ${data.api_root_reachable} | /api/states: ${data.states_endpoint_reachable} | /api/services: ${data.services_endpoint_reachable} | Safe metadata step: ${data.safe_to_attempt_metadata_step}`;
        } catch {
          target.textContent = "Failed to load Home Assistant capabilities.";
        }
      }

      async function loadHaMetadataPreviewInfo() {
        const target = document.getElementById("ha-metadata-preview-info");
        try {
          const data = await fetchAddonJson("api/ha-metadata-preview");
          target.textContent = `Config available: ${data.config_available} | States reachable: ${data.states_endpoint_reachable} | Services reachable: ${data.services_endpoint_reachable} | States count: ${data.states_count} | Service domains: ${data.services_domain_count} | Home Assistant version: ${data.home_assistant_version}`;
        } catch {
          target.textContent = "Failed to load Home Assistant metadata preview.";
        }
      }

      async function loadHaDomainPreviewInfo() {
        const target = document.getElementById("ha-domain-preview-info");
        try {
          const data = await fetchAddonJson("api/ha-domain-preview");
          let top10 = [];
          if (Array.isArray(data.top_domains) && data.top_domains.length > 0) {
            top10 = data.top_domains.map((item) => [item.domain, item.count]);
          } else {
            const entries = Object.entries(data.domain_counts || {});
            entries.sort((a, b) => b[1] - a[1]);
            top10 = entries.slice(0, 10);
          }
          if (top10.length === 0) {
            target.textContent = "Domain counts (top 10): none";
            return;
          }
          target.textContent = `Domain counts (top 10): ${top10.map(([d, c]) => `${d}: ${c}`).join(" | ")}`;
        } catch {
          target.textContent = "Failed to load Home Assistant domain preview.";
        }
      }

      async function loadHaStructurePreviewInfo() {
        const target = document.getElementById("ha-structure-preview-info");
        try {
          const data = await fetchAddonJson("api/ha-structure-preview");
          target.textContent = `Areas available: ${data.areas_available} | Devices available: ${data.devices_available} | Entities available: ${data.entities_available} | Areas count: ${data.areas_count} | Devices count: ${data.devices_count} | Entities count: ${data.entities_count}`;
        } catch {
          target.textContent = "Failed to load Home Assistant structure preview.";
        }
      }

      async function loadHaLogicPreviewInfo() {
        const target = document.getElementById("ha-logic-preview-info");
        try {
          const data = await fetchAddonJson("api/ha-logic-preview");
          target.textContent = `Automations: ${data.automations_count} | Scripts: ${data.scripts_count} | Scenes: ${data.scenes_count}`;
        } catch {
          target.textContent = "Failed to load Home Assistant logic preview.";
        }
      }

      async function loadHaDashboardPreviewInfo() {
        const target = document.getElementById("ha-dashboard-preview-info");
        try {
          const data = await fetchAddonJson("api/ha-dashboard-preview");
          const viewTypes = Array.isArray(data.detected_view_types) && data.detected_view_types.length > 0
            ? data.detected_view_types.join(", ")
            : "none";
          target.textContent = `Dashboards available: ${data.dashboards_available} | Dashboards count: ${data.dashboards_count} | Total views: ${data.total_views_count} | Total cards: ${data.total_cards_count} | Detected view types: ${viewTypes}`;
        } catch {
          target.textContent = "Failed to load Home Assistant dashboard preview.";
        }
      }

      async function loadHaAiContextPreviewInfo() {
        const target = document.getElementById("ha-ai-context-preview-info");
        try {
          const data = await fetchAddonJson("api/ha-ai-context-preview");
          const topDomains = Array.isArray(data.top_domains) && data.top_domains.length > 0
            ? data.top_domains.map((item) => `${item.domain}:${item.count}`).join(", ")
            : "none";
          target.textContent = `System size: ${data.system_size} | Entities: ${data.entities_count} | Devices: ${data.devices_count} | Areas: ${data.areas_count} | Automations: ${data.automations_count} | Scripts: ${data.scripts_count} | Scenes: ${data.scenes_count} | Dashboards: ${data.dashboards_count} | Views: ${data.views_count} | Cards: ${data.cards_count} | Top domains: ${topDomains}`;
        } catch {
          target.textContent = "Failed to load AI context preview.";
        }
      }

      async function loadHaBaseInfo() {
        const target = document.getElementById("ha-base-info");
        try {
          const data = await fetchAddonJson("api/ha-base");
          const pathSummary = data.paths.map((item) => `${item.path}:${item.exists}`).join(", ");
          target.textContent = `Slug: ${data.addon_slug} | Version: ${data.version} | Looks like HA add-on env: ${data.looks_like_ha_addon_environment} | Paths: ${pathSummary}`;
        } catch {
          target.textContent = "Failed to load Home Assistant base info.";
        }
      }

      function runPreviewLoad(loader) {
        try {
          loader();
        } catch {
          // Keep other preview sections running even if one loader fails unexpectedly.
        }
      }

      applyStylesheet();
      runPreviewLoad(loadAppInfo);
      runPreviewLoad(loadSystemInfo);
      runPreviewLoad(loadHaBaseInfo);
      runPreviewLoad(loadHaDetectInfo);
      runPreviewLoad(loadHaCoreCheckInfo);
      runPreviewLoad(loadHaCapabilitiesInfo);
      runPreviewLoad(loadHaMetadataPreviewInfo);
      runPreviewLoad(loadHaDomainPreviewInfo);
      runPreviewLoad(loadHaStructurePreviewInfo);
      runPreviewLoad(loadHaLogicPreviewInfo);
      runPreviewLoad(loadHaDashboardPreviewInfo);
      runPreviewLoad(loadHaAiContextPreviewInfo);
    </script>
  </body>
</html>
```

## Annahmen / Einschränkungen
- Die URL-Basis wird aus `window.location.pathname` abgeleitet und mit trailing slash stabilisiert, damit Ingress-Pfade korrekt aufgelöst werden.
- Die Backend-Pfadnormalisierung ist bewusst best effort (Ingress-Prefix `/api/hassio_ingress/<token>/...`).
- Keine Tokens/Auth-Header, keine Supervisor-API, keine YAML-Dateien, keine Persistenz.
