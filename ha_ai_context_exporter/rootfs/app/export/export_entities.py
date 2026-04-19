"""Entities export helpers."""

from __future__ import annotations

import re

IMPORTANT_ATTRIBUTE_KEYS = (
    "device_class",
    "entity_category",
    "state_class",
    "unit_of_measurement",
)

_IPV4_ADDRESS_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|1?\d?\d)"
    r"(?!\d)"
)
_IPV4_UNDERSCORE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)_){3}"
    r"(?:25[0-5]|2[0-4]\d|1?\d?\d)"
    r"(?!\d)"
)
_IPV4_HYPHEN_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)-){3}"
    r"(?:25[0-5]|2[0-4]\d|1?\d?\d)"
    r"(?!\d)"
)
_MAC_ADDRESS_PATTERN = re.compile(
    r"(?i)\b[0-9a-f]{2}([:-])[0-9a-f]{2}(?:\1[0-9a-f]{2}){4}\b"
)
_MAC_UNDERSCORE_PATTERN = re.compile(
    r"(?i)(?<![0-9a-f])(?:[0-9a-f]{2}_){5}[0-9a-f]{2}(?![0-9a-f])"
)
_PLAIN_MAC_PATTERN = re.compile(r"(?i)\b[0-9a-f]{12}\b")
_NUMERIC_STATE_PATTERN = re.compile(
    r"(?i)^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$"
)
_COORDINATE_PAIR_PATTERN = re.compile(
    r"(?<!\d)-?\d{1,2}\.\d{4,}\s*,\s*-?\d{1,3}\.\d{4,}(?!\d)"
)

_PERSON_TOKEN_BLOCKLIST = {
    "address",
    "device",
    "geocoded",
    "home",
    "location",
    "media",
    "mobile",
    "person",
    "phone",
    "player",
    "sensor",
    "switch",
    "tracker",
    "wifi",
    "work",
}
_UNKNOWN_STATE_VALUES = {"unknown", "unavailable", "none", ""}
_NETWORK_CONTEXT_TERMS = ("ssid", "bssid", "wifi", "wi_fi", "wi-fi")
_LOCATION_CONTEXT_TERMS = ("geocoded", "address", "latitude", "longitude")


def _iter_person_tokens(value: str) -> list[str]:
    tokens: list[str] = []
    for token in re.split(r"[\W_]+", value.lower()):
        if len(token) < 3 or token.isdigit() or token in _PERSON_TOKEN_BLOCKLIST:
            continue
        tokens.append(token)
    return tokens


def _person_phrase_patterns(value: str, label: str) -> list[tuple[re.Pattern, str]]:
    patterns: list[tuple[re.Pattern, str]] = []
    stripped = value.strip()
    if len(stripped) >= 3:
        patterns.append(
            (
                re.compile(rf"(?i)(?<![a-z0-9]){re.escape(stripped)}(?![a-z0-9])"),
                label,
            )
        )

    slug = "_".join(_iter_person_tokens(value))
    if len(slug) >= 3 and slug != stripped.lower():
        patterns.append(
            (
                re.compile(rf"(?i)(?<![a-z0-9]){re.escape(slug)}(?![a-z0-9])"),
                label,
            )
        )

    return patterns


def _build_person_mask_context(states_payload: list) -> dict:
    people: list[dict[str, str | None]] = []
    for entry in states_payload:
        if not isinstance(entry, dict):
            continue

        entity_id = entry.get("entity_id")
        if not isinstance(entity_id, str) or not entity_id.startswith("person."):
            continue

        friendly_name = None
        attributes = entry.get("attributes")
        if isinstance(attributes, dict):
            raw_friendly_name = attributes.get("friendly_name")
            if isinstance(raw_friendly_name, str):
                friendly_name = raw_friendly_name

        people.append({"entity_id": entity_id, "friendly_name": friendly_name})

    entity_labels: dict[str, str] = {}
    token_labels: dict[str, str] = {}
    phrase_patterns: list[tuple[re.Pattern, str]] = []
    for index, person in enumerate(
        sorted(people, key=lambda item: str(item["entity_id"])), start=1
    ):
        entity_id = str(person["entity_id"])
        label = f"redacted_person_{index}"
        entity_labels[entity_id] = label

        suffix = entity_id.split(".", 1)[1]
        phrase_patterns.extend(_person_phrase_patterns(suffix, label))
        for token in _iter_person_tokens(suffix):
            token_labels.setdefault(token, label)

        friendly_name = person.get("friendly_name")
        if isinstance(friendly_name, str):
            phrase_patterns.extend(_person_phrase_patterns(friendly_name, label))
            for token in _iter_person_tokens(friendly_name):
                token_labels.setdefault(token, label)

    token_patterns = [
        (re.compile(rf"(?i)(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])"), label)
        for token, label in sorted(
            token_labels.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )
    ]
    phrase_patterns = sorted(
        phrase_patterns,
        key=lambda item: len(item[0].pattern),
        reverse=True,
    )
    return {
        "entity_labels": entity_labels,
        "phrase_patterns": phrase_patterns,
        "token_patterns": token_patterns,
    }


def _mask_person_tokens(
    value: str,
    person_mask_context: dict,
    *,
    entity_id_safe: bool,
) -> str:
    masked = value
    for pattern, label in person_mask_context["phrase_patterns"]:
        replacement = label if entity_id_safe else f"[{label}]"
        masked = pattern.sub(replacement, masked)
    for pattern, label in person_mask_context["token_patterns"]:
        replacement = label if entity_id_safe else f"[{label}]"
        masked = pattern.sub(replacement, masked)
    return masked


def _contains_any(value: str, terms: tuple[str, ...]) -> bool:
    normalized = value.lower()
    return any(term in normalized for term in terms)


def _state_can_be_context_masked(value: str) -> bool:
    return value.strip().lower() not in _UNKNOWN_STATE_VALUES


def _state_looks_like_numeric_measurement(value: str, item: dict) -> bool:
    important_attributes = item.get("important_attributes")
    has_measurement_hint = isinstance(important_attributes, dict) and any(
        isinstance(important_attributes.get(key), str)
        for key in ("device_class", "state_class", "unit_of_measurement")
    )
    return has_measurement_hint and bool(_NUMERIC_STATE_PATTERN.fullmatch(value.strip()))


def _mask_compact_sensitive_value(
    value: str,
    *,
    field: str,
    item: dict,
    person_mask_context: dict,
) -> str:
    entity_id = item.get("entity_id") if isinstance(item.get("entity_id"), str) else ""
    friendly_name = (
        item.get("friendly_name") if isinstance(item.get("friendly_name"), str) else ""
    )
    context = f"{entity_id} {friendly_name}"
    entity_id_safe = field == "entity_id"
    ipv4_replacement = "redacted_ipv4" if entity_id_safe else "[redacted_ipv4]"
    mac_replacement = "redacted_mac" if entity_id_safe else "[redacted_mac]"
    location_replacement = (
        "redacted_location" if entity_id_safe else "[redacted_location]"
    )

    masked = _IPV4_ADDRESS_PATTERN.sub(ipv4_replacement, value)
    masked = _IPV4_UNDERSCORE_PATTERN.sub(ipv4_replacement, masked)
    masked = _IPV4_HYPHEN_PATTERN.sub(ipv4_replacement, masked)
    masked = _MAC_ADDRESS_PATTERN.sub(mac_replacement, masked)
    masked = _MAC_UNDERSCORE_PATTERN.sub(mac_replacement, masked)
    if not (
        field == "state" and _state_looks_like_numeric_measurement(value, item)
    ):
        masked = _PLAIN_MAC_PATTERN.sub(mac_replacement, masked)
    masked = _COORDINATE_PAIR_PATTERN.sub(location_replacement, masked)

    if field == "entity_id" and entity_id.startswith("person."):
        label = person_mask_context["entity_labels"].get(entity_id)
        if label:
            return f"person.{label}"

    if field == "friendly_name" and entity_id.startswith("person."):
        label = person_mask_context["entity_labels"].get(entity_id)
        if label:
            return f"[{label}]"

    if field == "state" and _state_can_be_context_masked(masked):
        if _contains_any(context, _NETWORK_CONTEXT_TERMS):
            return "[redacted_network_name]"
        if _contains_any(context, _LOCATION_CONTEXT_TERMS):
            return "[redacted_location]"

    return _mask_person_tokens(
        masked,
        person_mask_context,
        entity_id_safe=entity_id_safe,
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


def _mask_compact_entity_item(item: dict, person_mask_context: dict) -> dict:
    masked_item = dict(item)

    for field in ("entity_id", "state", "friendly_name"):
        value = masked_item.get(field)
        if isinstance(value, str):
            masked_item[field] = _mask_compact_sensitive_value(
                value,
                field=field,
                item=item,
                person_mask_context=person_mask_context,
            )

    important_attributes = masked_item.get("important_attributes")
    if isinstance(important_attributes, dict):
        masked_item["important_attributes"] = {
            key: _mask_compact_sensitive_value(
                value,
                field=f"important_attributes.{key}",
                item=item,
                person_mask_context=person_mask_context,
            )
            if isinstance(value, str)
            else value
            for key, value in important_attributes.items()
        }

    return masked_item


def build_compact_entity_items(
    states_payload: list,
    *,
    allow_sensitive_values: bool = False,
) -> list[dict]:
    """Build a small, deterministic entity context slice from /states data."""
    items: list[dict] = []
    person_mask_context = _build_person_mask_context(states_payload)

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

    sorted_items = sorted(items, key=lambda item: item["entity_id"])
    if allow_sensitive_values:
        return sorted_items

    return [
        _mask_compact_entity_item(item, person_mask_context) for item in sorted_items
    ]


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
