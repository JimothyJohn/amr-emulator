"""VDA 5050 MQTT topic construction and parsing.

The recommendation (section 4.2) suggests the topic structure
``interfaceName/majorVersion/manufacturer/serialNumber/topic`` for local
brokers and makes the trailing topic names mandatory. ``/``, MQTT wildcards
and ``$`` are forbidden inside the individual levels; serial numbers are
restricted to ``A-Z a-z 0-9 _ . : -``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PROTOCOL_VERSION = "3.0.0"

# Topics the fleet control publishes and the mobile robot subscribes to.
ROBOT_SUBSCRIBES = ("order", "instantActions", "zoneSet", "responses")
# Topics the mobile robot publishes.
ROBOT_PUBLISHES = ("state", "visualization", "connection", "factsheet")

# Emulator-only control channel (not part of VDA 5050): fault injection,
# battery override, teleport. Named with a leading underscore so it can never
# collide with a future standard topic.
EMULATOR_TOPIC = "_emulator"

_SERIAL_RE = re.compile(r"^[A-Za-z0-9_.:\-]+$")
_LEVEL_FORBIDDEN = set("/+#$")


def _check_level(name: str, value: str) -> str:
    if not value or any(ch in _LEVEL_FORBIDDEN for ch in value):
        raise ValueError(f"invalid {name} for an MQTT topic level: {value!r}")
    return value


@dataclass(frozen=True)
class TopicBase:
    """One robot's topic namespace, e.g. ``vda5050/v3/KIT/0001``."""

    manufacturer: str
    serial_number: str
    interface_name: str = "vda5050"
    major_version: str = "v" + PROTOCOL_VERSION.split(".")[0]

    def __post_init__(self) -> None:
        _check_level("interfaceName", self.interface_name)
        _check_level("majorVersion", self.major_version)
        _check_level("manufacturer", self.manufacturer)
        if not _SERIAL_RE.match(self.serial_number):
            raise ValueError(f"invalid serialNumber: {self.serial_number!r}")

    @property
    def prefix(self) -> str:
        return (
            f"{self.interface_name}/{self.major_version}/{self.manufacturer}/{self.serial_number}"
        )

    def topic(self, name: str) -> str:
        return f"{self.prefix}/{name}"

    def subscription_filters(self) -> list[str]:
        return [self.topic(name) for name in (*ROBOT_SUBSCRIBES, EMULATOR_TOPIC)]


def parse_topic(topic: str) -> tuple[TopicBase, str] | None:
    """Split a concrete topic into its robot namespace and trailing topic name."""
    parts = topic.split("/")
    if len(parts) != 5:
        return None
    interface_name, major_version, manufacturer, serial_number, name = parts
    try:
        base = TopicBase(
            manufacturer=manufacturer,
            serial_number=serial_number,
            interface_name=interface_name,
            major_version=major_version,
        )
    except ValueError:
        return None
    return base, name
