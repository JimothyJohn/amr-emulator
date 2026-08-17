"""Programmable VDA 5050 master control.

The three layers, bottom-up:

- :class:`FleetMaster` — one broker connection, wildcard discovery, a
  :class:`RobotHandle` per robot (validated publishing + awaitable state);
- :class:`Mission` / :class:`Waypoint` — routes with work, compiled to
  spec-correct orders and stitched order updates for any supported version;
- :class:`MissionController` — per-robot queues and the full order
  lifecycle: dispatch, acceptance/rejection, base extension, completion,
  cancellation, retries.
"""

from ._version import __version__
from .controller import FINAL_STATUSES, MissionController, MissionRun, MissionStatus
from .fleet import FleetMaster, RobotHandle, errors_referencing, find_action
from .missions import Mission, Waypoint, action

__all__ = [
    "FINAL_STATUSES",
    "FleetMaster",
    "Mission",
    "MissionController",
    "MissionRun",
    "MissionStatus",
    "RobotHandle",
    "Waypoint",
    "__version__",
    "action",
    "errors_referencing",
    "find_action",
]
