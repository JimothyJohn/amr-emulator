"""Zones (section 6.4) and the request/response mechanism (6.9) — 3.0 only.

The emulator enforces the zone types it advertises in the factsheet
(``SUPPORTED_ZONES``): BLOCKED and RELEASE gate movement, SPEED_LIMIT caps
edge speed, ACTION zones trigger entry/during/exit actions. Zone membership is
evaluated at the robot's kinematic center; contour-based semantics collapse to
the same point test for a point-sized emulated contour, which keeps the
geometry honest without a collision engine.

Requests: before entering a RELEASE zone the robot files a ``zoneRequest``
(status REQUESTED) in its state and waits for the fleet control's answer on
the ``responses`` topic. GRANTED (with optional leaseExpiry) lets it drive,
QUEUED keeps it waiting, REJECTED keeps it stopped, REVOKED/lease expiry while
inside applies the zone's ``releaseLossBehavior``.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any


def point_in_polygon(x: float, y: float, vertices: list[dict]) -> bool:
    """Ray-casting test; polygon is closed implicitly (spec 7.6)."""
    inside = False
    n = len(vertices)
    for i in range(n):
        x1, y1 = float(vertices[i]["x"]), float(vertices[i]["y"])
        x2, y2 = float(vertices[(i + 1) % n]["x"]), float(vertices[(i + 1) % n]["y"])
        if (y1 > y) != (y2 > y):
            t = (y - y1) / (y2 - y1)
            if x < x1 + t * (x2 - x1):
                inside = not inside
    return inside


@dataclass
class ZoneSet:
    doc: dict[str, Any]
    status: str = "DISABLED"

    @property
    def zone_set_id(self) -> str:
        return self.doc["zoneSetId"]

    @property
    def map_id(self) -> str:
        return self.doc["mapId"]

    @property
    def zones(self) -> list[dict]:
        return self.doc.get("zones", [])


class ZoneBook:
    """Zone sets stored on the robot plus the active request bookkeeping."""

    def __init__(self) -> None:
        self.zone_sets: dict[str, ZoneSet] = {}
        self.zone_requests: list[dict] = []  # state.zoneRequests entries
        self._request_meta: dict[str, dict] = {}  # requestId -> {leaseExpiry, ...}
        self._request_ids = itertools.count(1)

    # -- zone set management (downloadZoneSet / zoneSet topic / enable / delete)

    def add(self, doc: dict[str, Any]) -> bool:
        """Store a new zone set (DISABLED). False if the id already exists."""
        if doc["zoneSetId"] in self.zone_sets:
            return False
        self.zone_sets[doc["zoneSetId"]] = ZoneSet(doc)
        return True

    def enable(self, zone_set_id: str) -> bool:
        target = self.zone_sets.get(zone_set_id)
        if target is None:
            return False
        for other in self.zone_sets.values():
            if other.map_id == target.map_id:
                other.status = "DISABLED"
        target.status = "ENABLED"
        return True

    def delete(self, zone_set_id: str) -> bool:
        return self.zone_sets.pop(zone_set_id, None) is not None

    def state_entries(self) -> list[dict]:
        return [
            {"zoneSetId": zs.zone_set_id, "mapId": zs.map_id, "zoneSetStatus": zs.status}
            for zs in self.zone_sets.values()
        ]

    # -- geometry

    def active_zones_at(self, x: float, y: float, map_id: str) -> list[tuple[ZoneSet, dict]]:
        found = []
        for zone_set in self.zone_sets.values():
            if zone_set.status != "ENABLED" or zone_set.map_id != map_id:
                continue
            for zone in zone_set.zones:
                if point_in_polygon(x, y, zone.get("vertices", [])):
                    found.append((zone_set, zone))
        return found

    def speed_limit_at(self, x: float, y: float, map_id: str) -> float | None:
        limits = [
            float(zone["maximumSpeed"])
            for _, zone in self.active_zones_at(x, y, map_id)
            if zone["zoneType"] == "SPEED_LIMIT" and "maximumSpeed" in zone
        ]
        return min(limits) if limits else None

    def blocking_zone_at(self, x: float, y: float, map_id: str) -> dict | None:
        for _, zone in self.active_zones_at(x, y, map_id):
            if zone["zoneType"] == "BLOCKED":
                return zone
        return None

    def release_zones_at(self, x: float, y: float, map_id: str) -> list[tuple[ZoneSet, dict]]:
        return [
            (zone_set, zone)
            for zone_set, zone in self.active_zones_at(x, y, map_id)
            if zone["zoneType"] == "RELEASE"
        ]

    # -- request lifecycle (6.9)

    def request_access(self, zone_set: ZoneSet, zone: dict) -> dict:
        """Ensure an ACCESS request exists for the zone; returns the entry."""
        for entry in self.zone_requests:
            if entry["zoneId"] == zone["zoneId"] and entry["zoneSetId"] == zone_set.zone_set_id:
                return entry
        entry = {
            "requestId": f"req-{next(self._request_ids)}",
            "requestType": "ACCESS",
            "zoneId": zone["zoneId"],
            "zoneSetId": zone_set.zone_set_id,
            "requestStatus": "REQUESTED",
        }
        self.zone_requests.append(entry)
        self._request_meta[entry["requestId"]] = {}
        return entry

    def apply_response(self, response: dict) -> dict | None:
        """Apply one response object; returns the affected request entry."""
        for entry in self.zone_requests:
            if entry["requestId"] != response.get("requestId"):
                continue
            grant = response.get("grantType")
            meta = self._request_meta.setdefault(entry["requestId"], {})
            if grant == "GRANTED":
                entry["requestStatus"] = "GRANTED"
                meta["leaseExpiry"] = response.get("leaseExpiry")
            elif grant == "QUEUED":
                entry["requestStatus"] = "REQUESTED"
                meta["queued"] = True
            elif grant == "REJECTED":
                entry["requestStatus"] = "REQUESTED"
                meta["rejected"] = True
            elif grant == "REVOKED":
                entry["requestStatus"] = "REVOKED"
            return entry
        return None

    def status(self, zone_set_id: str, zone_id: str) -> str | None:
        for entry in self.zone_requests:
            if entry["zoneId"] == zone_id and entry["zoneSetId"] == zone_set_id:
                return entry["requestStatus"]
        return None

    def lease_expiry(self, request_id: str) -> str | None:
        return self._request_meta.get(request_id, {}).get("leaseExpiry")

    def expire_leases(self, now_iso: str) -> list[dict]:
        """Mark GRANTED requests whose lease has passed as EXPIRED."""
        expired = []
        for entry in self.zone_requests:
            lease = self.lease_expiry(entry["requestId"])
            if entry["requestStatus"] == "GRANTED" and lease and lease <= now_iso:
                entry["requestStatus"] = "EXPIRED"
                expired.append(entry)
        return expired

    def remove_request(self, request_id: str) -> None:
        self.zone_requests = [e for e in self.zone_requests if e["requestId"] != request_id]
        self._request_meta.pop(request_id, None)

    def clear_requests(self) -> None:
        self.zone_requests.clear()
        self._request_meta.clear()


@dataclass
class ZoneMembership:
    """Tracks which ACTION zones the robot is currently inside, to fire
    entry/during/exit actions exactly on the transitions."""

    inside: set[str] = field(default_factory=set)

    def transitions(
        self, zones_here: list[tuple[ZoneSet, dict]]
    ) -> tuple[list[dict], list[str], set[str]]:
        """Returns (entered action-zones, exited zone ids, current ids)."""
        current = {zone["zoneId"] for _, zone in zones_here if zone["zoneType"] == "ACTION"}
        entered = [
            zone
            for _, zone in zones_here
            if zone["zoneType"] == "ACTION" and zone["zoneId"] not in self.inside
        ]
        exited = sorted(self.inside - current)
        self.inside = current
        return entered, exited, current
