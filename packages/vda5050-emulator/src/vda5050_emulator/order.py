"""Order graph validation and the acceptance decision of Figure 8.

Pure logic, no I/O: given the incoming order message and a snapshot of the
robot's situation, decide accept / ignore / reject and, for rejections, which
predefined error to report. The robot (robot.py) applies the decision.

Every structural rule from section 6.1 is enforced:
- sequenceIds are continuous, nodes even / edges odd, shared numbering;
- ``len(edges) == len(nodes) - 1`` and at least one node;
- released base is a prefix (an edge is released only if both its nodes are,
  nothing released may follow anything unreleased);
- the first node must be trivially reachable (standing on it or inside its
  deviation range);
- order updates must stitch onto the decision point (same nodeId and
  sequenceId), horizon may be replaced freely, the base never changes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Situation:
    """Snapshot of everything Figure 8 needs to know about the robot."""

    order_id: str = ""
    order_update_id: int = 0
    has_order: bool = False  # an order was ever accepted (ids are meaningful)
    idle: bool = True
    cancelled: bool = False  # the current orderId was cancelled
    waiting_for_update: bool = False  # horizon present or base not finished
    decision_point: tuple[str, int] | None = None  # nodeId, sequenceId of last base node
    position: tuple[float, float] | None = None
    theta: float = 0.0
    last_node_id: str = ""
    map_id: str = ""
    known_maps: frozenset[str] = frozenset()
    supported_actions: frozenset[str] = frozenset()
    supported_node_actions: frozenset[str] = frozenset()
    supported_edge_actions: frozenset[str] = frozenset()
    accepts_orders: bool = True  # operating mode allows orders
    edges_carry_node_ids: bool = False


@dataclass
class Decision:
    verdict: str  # "accept" | "ignore" | "reject"
    error_key: str = ""  # semantic error key (profiles.Profile.error_type)
    references: dict[str, str] = field(default_factory=dict)
    detail: str = ""
    # For accepts: sequenceId from which nodes/edges are new to the robot
    # (0 for a fresh order, decision-point sequenceId for updates).
    append_from: int = 0
    is_update: bool = False


def _reject(key: str, order: dict, detail: str = "", **extra: str) -> Decision:
    references = {
        "orderId": str(order.get("orderId", "")),
        "orderUpdateId": str(order.get("orderUpdateId", "")),
        "topic": "order",
    }
    references.update(extra)
    return Decision("reject", error_key=key, references=references, detail=detail)


def _structural_problems(order: dict, situation: Situation) -> str | None:
    nodes: list[dict] = order["nodes"]
    edges: list[dict] = order["edges"]
    if not nodes:
        return "an order needs at least one node"
    if len(edges) != len(nodes) - 1:
        return f"{len(nodes)} nodes require {len(nodes) - 1} edges, got {len(edges)}"
    start = nodes[0]["sequenceId"]
    if start % 2 != 0:
        return f"first node sequenceId must be even, got {start}"
    for i, node in enumerate(nodes):
        if node["sequenceId"] != start + 2 * i:
            return f"node sequenceIds must increase by 2 (node index {i})"
    for i, edge in enumerate(edges):
        if edge["sequenceId"] != start + 2 * i + 1:
            return f"edge sequenceIds must interleave nodes (edge index {i})"
        if situation.edges_carry_node_ids:
            if edge.get("startNodeId") != nodes[i]["nodeId"]:
                return f"edge {edge['edgeId']} startNodeId does not match node sequence"
            if edge.get("endNodeId") != nodes[i + 1]["nodeId"]:
                return f"edge {edge['edgeId']} endNodeId does not match node sequence"
    released_nodes = [bool(n["released"]) for n in nodes]
    released_edges = [bool(e["released"]) for e in edges]
    if not released_nodes[0]:
        return "the first node must be released"
    base_nodes = _prefix_length(released_nodes)
    base_edges = _prefix_length(released_edges)
    if any(released_nodes[base_nodes:]) or any(released_edges[base_edges:]):
        return "released elements must form a contiguous prefix"
    if base_edges != max(0, base_nodes - 1) and not (
        base_nodes == len(nodes) and base_edges == len(edges)
    ):
        return "an edge may only be released when both adjacent nodes are released"
    return None


def _prefix_length(flags: list[bool]) -> int:
    for i, value in enumerate(flags):
        if not value:
            return i
    return len(flags)


def _unsupported_actions(order: dict, situation: Situation) -> list[str]:
    bad: list[str] = []
    for kind, elements, supported in (
        ("node", order["nodes"], situation.supported_node_actions),
        ("edge", order["edges"], situation.supported_edge_actions),
    ):
        for element in elements:
            for action in element.get("actions", ()):
                action_type = action.get("actionType", "")
                if action_type not in supported:
                    bad.append(f"{kind}:{action_type or '<missing>'}")
    return bad


def _unknown_maps(order: dict, situation: Situation) -> list[str]:
    wanted = {
        node["nodePosition"]["mapId"]
        for node in order["nodes"]
        if isinstance(node.get("nodePosition"), dict) and "mapId" in node["nodePosition"]
    }
    return sorted(wanted - set(situation.known_maps))


def _first_node_reachable(order: dict, situation: Situation) -> bool:
    node = order["nodes"][0]
    position = node.get("nodePosition")
    if not isinstance(position, dict) or situation.position is None:
        # Line-guided case: no geometry to check — reachable iff the robot is
        # standing on that node (or has never localized on a node yet).
        return not situation.last_node_id or situation.last_node_id == node["nodeId"]
    deviation = position.get("allowedDeviationXY")
    if isinstance(deviation, dict):
        a = max(float(deviation.get("a", 0.0)), 1e-6)
        b = max(float(deviation.get("b", 0.0)), 1e-6)
        rotation = float(deviation.get("theta", 0.0))
    else:
        a = b = max(float(deviation or 0.0), 1e-6) if deviation is not None else 0.5
        rotation = 0.0
    dx = situation.position[0] - float(position["x"])
    dy = situation.position[1] - float(position["y"])
    cos_r, sin_r = math.cos(-rotation), math.sin(-rotation)
    u = dx * cos_r - dy * sin_r
    v = dx * sin_r + dy * cos_r
    if (u / a) ** 2 + (v / b) ** 2 > 1.0:
        return False
    theta = position.get("theta")
    if theta is not None:
        allowed = position.get("allowedDeviationTheta")
        allowed = math.pi if allowed is None else float(allowed)
        delta = abs(_angle_diff(float(theta), situation.theta))
        if delta > allowed + 1e-9:
            return False
    return True


def _angle_diff(a: float, b: float) -> float:
    return math.atan2(math.sin(a - b), math.cos(a - b))


def evaluate(order: dict[str, Any], situation: Situation) -> Decision:
    """Run the acceptance process of Figure 8 on a schema-valid order."""
    problem = _structural_problems(order, situation)
    if problem:
        return _reject("validation", order, problem)

    unsupported = _unsupported_actions(order, situation)
    if unsupported:
        return _reject(
            "invalid_order_action", order, "unsupported actions", actions=",".join(unsupported)
        )

    if not situation.accepts_orders:
        return _reject("not_available", order, "operating mode does not allow orders")

    unknown_maps = _unknown_maps(order, situation)
    if unknown_maps:
        return _reject("unknown_map", order, "unknown mapId", mapId=",".join(unknown_maps))

    is_new = order["orderId"] != situation.order_id or not situation.has_order
    if is_new:
        if not situation.idle:
            return _reject("other_order_active", order, "another order is active")
        if order["orderUpdateId"] != 0:
            return _reject("validation", order, "a new order must start with orderUpdateId 0")
        if not _first_node_reachable(order, situation):
            return _reject("start_node_out_of_range", order, "first node not reachable")
        return Decision("accept", append_from=order["nodes"][0]["sequenceId"])

    incoming_update = order["orderUpdateId"]
    if incoming_update < situation.order_update_id:
        return _reject("outdated_order_update", order, "orderUpdateId is outdated")
    if incoming_update == situation.order_update_id:
        # Digest comparison happens in the robot (it still holds the previous
        # message); "ignore" means resend of the identical message.
        return Decision("ignore")
    if situation.cancelled:
        return _reject("update_following_cancel", order, "order was cancelled")

    stitch = order["nodes"][0]
    if situation.decision_point is None:
        # Order was cleared (e.g. MANUAL) — updates cannot stitch anymore.
        return _reject("validation", order, "no decision point to stitch onto")
    node_id, sequence_id = situation.decision_point
    if stitch["nodeId"] != node_id or stitch["sequenceId"] != sequence_id:
        return _reject(
            "validation",
            order,
            "order update must start at the decision point "
            f"({node_id!r}, seq {sequence_id}), got ({stitch['nodeId']!r}, "
            f"seq {stitch['sequenceId']})",
        )
    return Decision("accept", append_from=sequence_id, is_update=True)
