"""Missions: a route with work at its stops, compiled to VDA 5050 orders.

A :class:`Mission` is the programmable unit a dispatcher (or, later, a UI)
deals in: an ordered list of :class:`Waypoint` stops, each optionally
carrying actions. Compiling honors every structural rule the acceptance
process (order.py's Figure 8 implementation) enforces:

- nodes get even sequenceIds (0, 2, 4…), edges the odd ones between;
- ``len(edges) == len(nodes) - 1``;
- the released base is a contiguous prefix, and an edge is released only
  when both adjacent nodes are;
- a fresh order carries ``orderUpdateId`` 0;
- an order update repeats the decision point (the last released node, same
  nodeId AND sequenceId) as its first node and re-sends everything from
  there, with a strictly increasing ``orderUpdateId``.

The base/horizon split is expressed as ``release=<n>`` (how many waypoints
the robot may execute now); :meth:`Mission.update` produces the stitched
follow-up message that extends the base.
"""

from __future__ import annotations

import itertools
import uuid
from dataclasses import dataclass
from typing import Any

from vda5050_emulator import make_action, make_edge, make_node

__all__ = ["Mission", "Waypoint", "action"]

# Re-exported so mission authors need only this module.
action = make_action


@dataclass(frozen=True)
class Waypoint:
    """One stop on a mission: a position, optionally with work to do there."""

    x: float
    y: float
    node_id: str = ""
    theta: float | None = None
    actions: tuple[dict, ...] = ()
    map_id: str = "map-0"
    deviation: float | None = None


class Mission:
    """An ordered route of waypoints, compilable to orders for any version."""

    def __init__(self, waypoints: list[Waypoint], *, name: str = "mission") -> None:
        if not waypoints:
            raise ValueError("a mission needs at least one waypoint")
        self.name = name
        self.waypoints: list[Waypoint] = []
        counter = itertools.count()
        for waypoint in waypoints:
            node_id = waypoint.node_id or f"{name}-n{next(counter)}"
            actions = tuple(dict(a) for a in waypoint.actions)
            for entry in actions:
                entry.setdefault("actionId", f"{name}-a{uuid.uuid4().hex[:12]}")
            self.waypoints.append(
                Waypoint(
                    x=waypoint.x,
                    y=waypoint.y,
                    node_id=node_id,
                    theta=waypoint.theta,
                    actions=actions,
                    map_id=waypoint.map_id,
                    deviation=waypoint.deviation,
                )
            )

    def __len__(self) -> int:
        return len(self.waypoints)

    @property
    def action_ids(self) -> list[str]:
        return [a["actionId"] for w in self.waypoints for a in w.actions]

    def new_order_id(self) -> str:
        return f"{self.name}-{uuid.uuid4().hex[:12]}"

    def _elements(
        self, version: str, indices: range, release_through: int
    ) -> tuple[list[dict], list[dict]]:
        nodes = []
        for i in indices:
            waypoint = self.waypoints[i]
            nodes.append(
                make_node(
                    waypoint.node_id,
                    2 * i,
                    released=i < release_through,
                    x=waypoint.x,
                    y=waypoint.y,
                    map_id=waypoint.map_id,
                    theta=waypoint.theta,
                    actions=[dict(a) for a in waypoint.actions],
                    deviation=waypoint.deviation,
                    version=version,
                )
            )
        edges = []
        for i in range(indices.start, indices.stop - 1):
            edges.append(
                make_edge(
                    f"{self.name}-e{i}",
                    2 * i + 1,
                    released=i < release_through - 1,
                    start_node_id=self.waypoints[i].node_id,
                    end_node_id=self.waypoints[i + 1].node_id,
                    version=version,
                )
            )
        return nodes, edges

    def order(
        self,
        *,
        version: str,
        order_id: str,
        release: int | None = None,
    ) -> dict[str, Any]:
        """The initial order message body (``orderUpdateId`` 0, per spec).

        ``release`` is how many waypoints form the released base (default:
        all of them); the rest ride along as the unreleased horizon.
        """
        release = self._checked_release(release, at_least=1)
        nodes, edges = self._elements(version, range(len(self.waypoints)), release)
        return {"orderId": order_id, "orderUpdateId": 0, "nodes": nodes, "edges": edges}

    def update(
        self,
        *,
        version: str,
        order_id: str,
        order_update_id: int,
        previous_release: int,
        release: int | None = None,
    ) -> dict[str, Any]:
        """A stitched order update extending the base to ``release`` waypoints.

        The message starts at the decision point — the last node of the
        previously released base, with its original sequenceId — and re-sends
        everything from there, as the acceptance process requires.
        """
        if order_update_id < 1:
            raise ValueError("an order update needs orderUpdateId >= 1")
        if not 1 <= previous_release <= len(self.waypoints):
            raise ValueError(f"previous_release {previous_release} out of range")
        release = self._checked_release(release, at_least=previous_release)
        stitch = previous_release - 1  # index of the decision-point node
        nodes, edges = self._elements(version, range(stitch, len(self.waypoints)), release)
        return {
            "orderId": order_id,
            "orderUpdateId": order_update_id,
            "nodes": nodes,
            "edges": edges,
        }

    def _checked_release(self, release: int | None, *, at_least: int) -> int:
        if release is None:
            return len(self.waypoints)
        if not at_least <= release <= len(self.waypoints):
            raise ValueError(
                f"release must be between {at_least} and {len(self.waypoints)}, got {release}"
            )
        return release
