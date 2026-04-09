#!/usr/bin/env python3
"""Minimal backend scaffold for the HA AI Context Exporter add-on."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

APP_NAME = "HA AI Context Exporter"
APP_VERSION = "0.1.0"
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


class RequestHandler(BaseHTTPRequestHandler):
    """Handle basic scaffold endpoints."""

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

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler convention)
        if self.path == "/health":
            self._send_json({"status": "ok"})
            return

        if self.path == "/api/info":
            self._send_json(APP_INFO)
            return

        if self.path == "/api/system":
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

        if self.path in ("/", "/index.html"):
            self._send_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
            return

        if self.path == "/styles.css":
            self._send_file(WEB_DIR / "styles.css", "text/css; charset=utf-8")
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        """Keep container logs concise."""
        return


def run() -> None:
    server = HTTPServer((HOST, PORT), RequestHandler)
    print(f"Starting HA AI Context Exporter scaffold on {HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
