"""Per-protocol-version wire-format profiles (2.0.0, 2.1.0, 3.0.0).

The emulator runs one behavior core; everything that differs between VDA 5050
generations is captured here as data, derived from the official schemas and
documents vendored from github.com/VDA5050/VDA5050:

- 2.x speaks "AGV" (``agvPosition``, ``batteryState``, ``eStop``,
  ``CONNECTIONBROKEN``, ``TEACHIN``), edges carry ``startNodeId``/``endNodeId``,
  errors are camelCase and only WARNING/FATAL, instant action states live in
  the shared ``actionStates`` array, and the customary interface name is
  ``uagv``.
- 3.0 speaks "mobile robot" (``mobileRobotPosition``, ``powerSupply``,
  ``activeEmergencyStop``, ``CONNECTION_BROKEN``, ``TEACH_IN``), adds zones,
  request/response, hibernation, RETRIABLE, the SINGLE blocking type and
  SCREAMING_SNAKE error types, and uses interface name ``vda5050``.
"""

from __future__ import annotations

from dataclasses import dataclass

# Semantic error keys used by the core -> wire errorType per version family.
_ERRORS_V3 = {
    "validation": "VALIDATION_FAILURE",
    "unsupported_parameter": "UNSUPPORTED_PARAMETER",
    "invalid_order_action": "INVALID_ORDER_ACTION",
    "invalid_instant_action": "INVALID_INSTANT_ACTION",
    "outdated_order_update": "OUTDATED_ORDER_UPDATE",
    "same_order_update": "SAME_ORDER_UPDATE_ID",
    "update_following_cancel": "ORDER_UPDATE_FOLLOWING_CANCEL",
    "other_order_active": "OTHER_ORDER_ACTIVE",
    "start_node_out_of_range": "START_NODE_OUT_OF_RANGE",
    "no_route_to_target": "NO_ROUTE_TO_TARGET",
    "not_available": "MOBILE_ROBOT_NOT_AVAILABLE",
    "unknown_map": "UNKNOWN_MAP_ID",
    "no_order_to_cancel": "NO_ORDER_TO_CANCEL",
    "duplicate_map": "DUPLICATE_MAP",
    "duplicate_zone_set": "DUPLICATE_ZONE_SET",
    "localization": "LOCALIZATION_ERROR",
    "blocked_zone": "BLOCKED_ZONE_VIOLATION",
    "release_lost": "RELEASE_LOST",
    "node_unreachable": "NODE_UNREACHABLE",
}

# 2.x has no normative error-type table; the spec text names "validationError",
# "orderError", "orderUpdateError" and "noOrderToCancel", which master controls
# in the field match on. Everything order-content-shaped maps to orderError,
# everything update-id-shaped to orderUpdateError.
_ERRORS_V2 = {
    "validation": "validationError",
    "unsupported_parameter": "validationError",
    "invalid_order_action": "orderError",
    "invalid_instant_action": "instantActionError",
    "outdated_order_update": "orderUpdateError",
    "same_order_update": "orderUpdateError",
    "update_following_cancel": "orderUpdateError",
    "other_order_active": "orderUpdateError",
    "start_node_out_of_range": "orderError",
    "no_route_to_target": "orderError",
    "not_available": "orderError",
    "unknown_map": "orderError",
    "no_order_to_cancel": "noOrderToCancel",
    "duplicate_map": "mapError",
    "localization": "localizationError",
}

_ACTIONS_V2_0 = {
    "startPause",
    "stopPause",
    "startCharging",
    "stopCharging",
    "initPosition",
    "stateRequest",
    "logReport",
    "pick",
    "drop",
    "detectObject",
    "finePositioning",
    "waitForTrigger",
    "cancelOrder",
}
_ACTIONS_V2_1 = _ACTIONS_V2_0 | {"enableMap", "downloadMap", "deleteMap", "factsheetRequest"}
_ACTIONS_V3 = (_ACTIONS_V2_1 - {"initPosition"}) | {
    "initializePosition",
    "startHibernation",
    "stopHibernation",
    "shutdown",
    "downloadZoneSet",
    "enableZoneSet",
    "deleteZoneSet",
    "clearInstantActions",
    "clearZoneActions",
    "trigger",
    "retry",
    "skipRetry",
    "updateCertificate",
}


@dataclass(frozen=True)
class Profile:
    version: str  # exact protocol version stamped into every message
    interface_name: str  # customary default topic root
    position_field: str
    localized_field: str
    battery_field: str
    charge_field: str
    estop_field: str
    connection_broken: str
    teach_in_mode: str
    init_position_action: str
    error_names: dict[str, str]
    supported_actions: frozenset[str]
    blocking_types: tuple[str, ...]
    action_statuses: tuple[str, ...]
    error_levels: tuple[str, ...]
    subscribed_topics: tuple[str, ...]
    edges_carry_node_ids: bool  # order edges have startNodeId/endNodeId
    has_maps: bool
    has_zones: bool  # zoneSet/responses topics, zone/edge requests
    has_hibernation: bool
    has_instant_action_states: bool  # separate state array (3.0)
    optional_parameter_prefix: str = ""  # extra optionalParameters naming quirks
    critical_level: str = "FATAL"  # level used where 3.0 says CRITICAL
    urgent_level: str = "WARNING"  # level used where 3.0 says URGENT

    @property
    def major(self) -> str:
        return "v" + self.version.split(".")[0]

    def error_type(self, key: str) -> str:
        return self.error_names[key]


def _v2_profile(version: str, *, has_maps: bool, actions: set[str]) -> Profile:
    return Profile(
        version=version,
        interface_name="uagv",
        position_field="agvPosition",
        localized_field="positionInitialized",
        battery_field="batteryState",
        charge_field="batteryCharge",
        estop_field="eStop",
        connection_broken="CONNECTIONBROKEN",
        teach_in_mode="TEACHIN",
        init_position_action="initPosition",
        error_names=_ERRORS_V2,
        supported_actions=frozenset(actions),
        blocking_types=("NONE", "SOFT", "HARD"),
        action_statuses=("WAITING", "INITIALIZING", "RUNNING", "PAUSED", "FINISHED", "FAILED"),
        error_levels=("WARNING", "FATAL"),
        subscribed_topics=("order", "instantActions"),
        edges_carry_node_ids=True,
        has_maps=has_maps,
        has_zones=False,
        has_hibernation=False,
        has_instant_action_states=False,
    )


PROFILES: dict[str, Profile] = {
    "2.0.0": _v2_profile("2.0.0", has_maps=False, actions=_ACTIONS_V2_0),
    "2.1.0": _v2_profile("2.1.0", has_maps=True, actions=_ACTIONS_V2_1),
    "3.0.0": Profile(
        version="3.0.0",
        interface_name="vda5050",
        position_field="mobileRobotPosition",
        localized_field="localized",
        battery_field="powerSupply",
        charge_field="stateOfCharge",
        estop_field="activeEmergencyStop",
        connection_broken="CONNECTION_BROKEN",
        teach_in_mode="TEACH_IN",
        init_position_action="initializePosition",
        error_names=_ERRORS_V3,
        supported_actions=frozenset(_ACTIONS_V3),
        blocking_types=("NONE", "SINGLE", "SOFT", "HARD"),
        action_statuses=(
            "WAITING",
            "INITIALIZING",
            "RUNNING",
            "PAUSED",
            "RETRIABLE",
            "FINISHED",
            "FAILED",
        ),
        error_levels=("WARNING", "URGENT", "CRITICAL", "FATAL"),
        subscribed_topics=("order", "instantActions", "zoneSet", "responses"),
        edges_carry_node_ids=False,
        has_maps=True,
        has_zones=True,
        has_hibernation=True,
        has_instant_action_states=True,
        critical_level="CRITICAL",
        urgent_level="URGENT",
    ),
}


def supported_versions() -> tuple[str, ...]:
    return tuple(sorted(PROFILES))


def profile(version: str) -> Profile:
    try:
        return PROFILES[version]
    except KeyError:
        raise ValueError(
            f"unsupported VDA 5050 version {version!r}; supported: {supported_versions()}"
        ) from None
