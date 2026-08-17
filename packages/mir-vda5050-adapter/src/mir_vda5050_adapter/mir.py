"""Async client for the slice of the MiR robot REST API the adapter drives.

Endpoints and shapes come from the official MiR 3.8.1 swagger bundled with
``mir-emulator`` (positions/missions/mission actions/mission_queue/status).
MiR speaks degrees for orientation; VDA 5050 speaks radians — conversion
happens at this boundary and nowhere else.
"""

from __future__ import annotations

import base64
import hashlib
import math
import uuid
from typing import Any

import httpx

API_PREFIX = "/api/v2.0.0"


def basic_auth(username: str, password: str) -> str:
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return "Basic " + base64.b64encode(f"{username}:{hashed}".encode()).decode()


class MiRClient:
    def __init__(
        self,
        base_url: str,
        *,
        username: str = "distributor",
        password: str = "distributor",  # noqa: S107 — MiR factory default
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": basic_auth(username, password)},
            transport=transport,
            timeout=10.0,
        )
        self._mission_group_id: str | None = None

    async def close(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str) -> Any:
        response = await self._client.get(f"{API_PREFIX}{path}")
        response.raise_for_status()
        return response.json()

    async def _post(self, path: str, body: dict) -> Any:
        response = await self._client.post(f"{API_PREFIX}{path}", json=body)
        response.raise_for_status()
        return response.json()

    async def status(self) -> dict:
        return await self._get("/status")

    async def set_state(self, state_id: int) -> None:
        response = await self._client.put(f"{API_PREFIX}/status", json={"state_id": state_id})
        response.raise_for_status()

    async def clear_mission_queue(self) -> None:
        response = await self._client.delete(f"{API_PREFIX}/mission_queue")
        response.raise_for_status()

    async def queue_entry(self, entry_id: int) -> dict:
        return await self._get(f"/mission_queue/{entry_id}")

    async def mission_group_id(self) -> str:
        if self._mission_group_id is None:
            groups = await self._get("/mission_groups")
            self._mission_group_id = groups[0]["guid"] if groups else f"vda-{uuid.uuid4().hex[:12]}"
        return self._mission_group_id

    async def enqueue_route(self, name: str, waypoints: list[dict], map_id: str) -> int:
        """Create positions + a mission of move actions, enqueue it.

        ``waypoints``: dicts with x, y and optional theta (radians).
        Returns the mission queue entry id.
        """
        mission = await self._post(
            "/missions", {"name": name, "group_id": await self.mission_group_id()}
        )
        for index, waypoint in enumerate(waypoints):
            orientation_deg = math.degrees(float(waypoint.get("theta") or 0.0))
            position = await self._post(
                "/positions",
                {
                    "name": f"{name}-wp{index}",
                    "pos_x": float(waypoint["x"]),
                    "pos_y": float(waypoint["y"]),
                    "orientation": orientation_deg,
                    "type_id": 0,
                    "map_id": map_id,
                },
            )
            await self._post(
                f"/missions/{mission['guid']}/actions",
                {
                    "action_type": "move",
                    "mission_id": mission["guid"],
                    "priority": index + 1,
                    "parameters": [{"id": "position", "value": position["guid"]}],
                },
            )
        entry = await self._post("/mission_queue", {"mission_id": mission["guid"]})
        return int(entry["id"])
