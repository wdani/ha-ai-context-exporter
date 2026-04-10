"""Render export payloads to downloadable formats."""

from __future__ import annotations

import json
from typing import Any

from .export_controller import ExportValidationError

ALLOWED_DOWNLOAD_FORMATS = ("json", "markdown")



def validate_download_format(fmt: str) -> str:
    """Validate requested download format."""
    if fmt not in ALLOWED_DOWNLOAD_FORMATS:
        allowed = ", ".join(ALLOWED_DOWNLOAD_FORMATS)
        raise ExportValidationError(
            f"Invalid format '{fmt}'. Allowed values: {allowed}."
        )
    return fmt



def _safe_timestamp(generated_at: str) -> str:
    ts = generated_at.replace(":", "-")
    ts = ts.replace("+00:00", "Z")
    return ts



def build_download_filename(payload: dict, mode: str, variant: str, fmt: str) -> str:
    """Build a stable download filename from payload metadata and query context."""
    generated_at = str(payload.get("generated_at", "unknown-time"))
    timestamp = _safe_timestamp(generated_at)
    extension = "json" if fmt == "json" else "md"
    return f"ha-ai-context-export_{mode}_{variant}_{timestamp}.{extension}"



def render_export_json_bytes(payload: dict) -> bytes:
    """Render payload as pretty UTF-8 JSON bytes."""
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")



def _append_markdown_lines(lines: list[str], value: Any, level: int = 0) -> None:
    indent = "  " * level

    if isinstance(value, dict):
        if not value:
            lines.append(f"{indent}- (empty)")
            return
        for key, nested in value.items():
            if isinstance(nested, (dict, list)):
                lines.append(f"{indent}- **{key}**:")
                _append_markdown_lines(lines, nested, level + 1)
            else:
                lines.append(f"{indent}- **{key}**: {nested}")
        return

    if isinstance(value, list):
        if not value:
            lines.append(f"{indent}- (empty list)")
            return
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{indent}-")
                _append_markdown_lines(lines, item, level + 1)
            else:
                lines.append(f"{indent}- {item}")
        return

    lines.append(f"{indent}- {value}")



def render_export_markdown_bytes(payload: dict) -> bytes:
    """Render payload as a readable Markdown document."""
    lines: list[str] = []
    lines.append("# HA AI Context Export")
    lines.append("")
    lines.append(f"- Export format: {payload.get('export_format')}")
    lines.append(f"- Export version: {payload.get('export_version')}")
    lines.append(f"- Generated at: {payload.get('generated_at')}")

    meta = payload.get("meta", {})
    lines.append(f"- Mode: {meta.get('mode')}")
    lines.append(f"- Variant: {meta.get('variant')}")
    lines.append("")

    section_order = [
        ("tool", "Tool"),
        ("environment", "Environment"),
        ("system", "System"),
        ("entities", "Entities"),
        ("areas_devices", "Areas & Devices"),
        ("logic", "Logic"),
        ("dashboard", "Dashboard"),
        ("integrations", "Integrations"),
        ("meta", "Meta"),
    ]

    for key, title in section_order:
        if key not in payload:
            continue
        lines.append(f"## {title}")
        _append_markdown_lines(lines, payload[key], level=0)
        lines.append("")

    return "\n".join(lines).encode("utf-8")
