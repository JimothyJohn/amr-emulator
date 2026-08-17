"""Factsheet (section 7.10) for the emulated mobile robot.

The factsheet is the robot's capability contract: fleet control reads it to
learn which optional parameters, actions and zones the robot supports. The
emulator therefore generates it from the same tables the rest of the code
enforces (SUPPORTED_ACTIONS, SUPPORTED_OPTIONAL_PARAMETERS, SUPPORTED_ZONES)
so the advertised and the implemented capability set cannot drift apart.
"""

from __future__ import annotations

from typing import Any

# Zone types the simulation actually enforces (see zones.py). Everything else
# is rejected as unsupported when it arrives in a zone set.
SUPPORTED_ZONES = ("BLOCKED", "RELEASE", "SPEED_LIMIT", "ACTION")

# Advertised protocolLimits are enforced limits: orders beyond them are
# rejected with INSUFFICIENT_MEMORY (spec 7.1.2), so the factsheet can never
# promise more than the robot accepts.
MAX_ORDER_NODES = 1000
MAX_ORDER_EDGES = 999

# Optional order/instantAction parameters the emulator acts on. Optional
# fields not listed here are rejected with UNSUPPORTED_PARAMETER (7.1.1).
SUPPORTED_OPTIONAL_PARAMETERS = (
    "order.nodes.nodePosition",
    "order.nodes.nodePosition.theta",
    "order.nodes.nodePosition.allowedDeviationXY",
    "order.nodes.nodePosition.allowedDeviationTheta",
    "order.edges.maximumSpeed",
    "order.edges.orientation",
    "order.edges.orientationType",
    "order.edges.length",
    "order.edges.trajectory",
    "order.edges.corridor",
    "order.edges.maximumRotationSpeed",
    "order.edges.reachOrientationBeforeEntering",
)

# actionType -> (scopes, parameters, description, blocking types, pause, cancel)
# Durations and side effects live in actions.py; this table is what the
# factsheet advertises and what order/instantAction validation checks against.
SUPPORTED_ACTIONS: dict[str, dict[str, Any]] = {
    "startPause": {"scopes": ["INSTANT"], "params": []},
    "stopPause": {"scopes": ["INSTANT"], "params": []},
    "startHibernation": {"scopes": ["INSTANT"], "params": [("wakeUpTime", "STRING", True)]},
    "stopHibernation": {"scopes": ["INSTANT"], "params": []},
    "shutdown": {"scopes": ["INSTANT"], "params": []},
    "startCharging": {"scopes": ["INSTANT", "NODE"], "params": []},
    "stopCharging": {"scopes": ["INSTANT", "NODE"], "params": []},
    "initializePosition": {
        "scopes": ["INSTANT", "NODE"],
        "params": [
            ("x", "NUMBER", False),
            ("y", "NUMBER", False),
            ("theta", "NUMBER", False),
            ("mapId", "STRING", False),
            ("lastNodeId", "STRING", False),
        ],
    },
    "enableMap": {
        "scopes": ["INSTANT", "NODE"],
        "params": [("mapId", "STRING", False), ("mapVersion", "STRING", False)],
    },
    "downloadMap": {
        "scopes": ["INSTANT"],
        "params": [
            ("mapId", "STRING", False),
            ("mapVersion", "STRING", False),
            ("mapDownloadLink", "STRING", False),
            ("mapHash", "STRING", True),
        ],
    },
    "deleteMap": {
        "scopes": ["INSTANT"],
        "params": [("mapId", "STRING", False), ("mapVersion", "STRING", False)],
    },
    "downloadZoneSet": {
        "scopes": ["INSTANT"],
        "params": [
            ("zoneSetId", "STRING", False),
            ("zoneSetDownloadLink", "STRING", False),
            ("zoneSetHash", "STRING", True),
        ],
    },
    "enableZoneSet": {"scopes": ["INSTANT", "NODE"], "params": [("zoneSetId", "STRING", False)]},
    "deleteZoneSet": {"scopes": ["INSTANT"], "params": [("zoneSetId", "STRING", False)]},
    "clearInstantActions": {"scopes": ["INSTANT", "NODE"], "params": []},
    "clearZoneActions": {"scopes": ["INSTANT", "NODE"], "params": []},
    "stateRequest": {"scopes": ["INSTANT"], "params": []},
    "logReport": {"scopes": ["INSTANT"], "params": [("reason", "STRING", True)]},
    "pick": {
        "scopes": ["NODE", "EDGE"],
        "pause_allowed": True,
        "params": [
            ("lhd", "STRING", True),
            ("stationType", "STRING", True),
            ("stationName", "STRING", True),
            ("loadType", "STRING", True),
            ("loadId", "STRING", True),
            ("height", "NUMBER", True),
            ("depth", "NUMBER", True),
            ("side", "STRING", True),
        ],
    },
    "drop": {
        "scopes": ["NODE", "EDGE"],
        "pause_allowed": True,
        "params": [
            ("lhd", "STRING", True),
            ("stationType", "STRING", True),
            ("stationName", "STRING", True),
            ("loadType", "STRING", True),
            ("loadId", "STRING", True),
            ("height", "NUMBER", True),
            ("depth", "NUMBER", True),
        ],
    },
    "detectObject": {
        "scopes": ["NODE", "EDGE", "ZONE"],
        "params": [("objectType", "STRING", True)],
    },
    "finePositioning": {
        "scopes": ["NODE", "EDGE", "ZONE"],
        "pause_allowed": True,
        "params": [("stationType", "STRING", True), ("stationName", "STRING", True)],
    },
    "waitForTrigger": {
        "scopes": ["NODE", "ZONE"],
        "params": [("triggerType", "ARRAY", False)],
    },
    "trigger": {"scopes": ["INSTANT"], "params": []},
    "retry": {"scopes": ["INSTANT"], "params": [("actionId", "STRING", False)]},
    "skipRetry": {"scopes": ["INSTANT"], "params": [("actionId", "STRING", False)]},
    "cancelOrder": {"scopes": ["INSTANT"], "params": [("orderId", "STRING", True)]},
    "factsheetRequest": {"scopes": ["INSTANT"], "params": []},
    "updateCertificate": {
        "scopes": ["INSTANT"],
        "params": [
            ("service", "STRING", False),
            ("keyDownloadLink", "STRING", False),
            ("certificateDownloadLink", "STRING", False),
            ("certificateAuthorityDownloadLink", "STRING", True),
        ],
    },
}


# 2.x names an action differently than 3.0; capability lookups go through here.
_ACTION_ALIASES = {"initPosition": "initializePosition"}


def action_scopes(action_type: str) -> tuple[str, ...]:
    canonical = _ACTION_ALIASES.get(action_type, action_type)
    return tuple(SUPPORTED_ACTIONS.get(canonical, {}).get("scopes", ()))


def _action_entries(profile) -> list[dict]:
    v2 = profile.version.startswith("2.")
    v2_names = {"initializePosition": "initPosition"}
    entries = []
    for action_type, info in sorted(SUPPORTED_ACTIONS.items()):
        wire_name = v2_names.get(action_type, action_type) if v2 else action_type
        if wire_name not in profile.supported_actions:
            continue
        entry: dict[str, Any] = {
            "actionType": wire_name,
            "actionScopes": [s for s in info["scopes"] if not (v2 and s == "ZONE")],
        }
        if not v2:
            # Omitted for 2.x: the official 2.1.0 schema puts a scalar `enum`
            # on the (optional) blockingTypes array, which no array can ever
            # satisfy — publishing it would make the factsheet invalid.
            entry["blockingTypes"] = list(profile.blocking_types)
            # The official 3.0.0 schema types these two as strings, not
            # booleans (the PDF says boolean) — we follow the schema.
            entry["pauseAllowed"] = "true" if info.get("pause_allowed") else "false"
            entry["cancelAllowed"] = (
                "false" if action_type in ("cancelOrder", "shutdown") else "true"
            )
        if info["params"]:
            entry["actionParameters"] = [
                {"key": key, "valueDataType": data_type, "isOptional": optional}
                for key, data_type, optional in info["params"]
            ]
        entries.append(entry)
    return entries


def build_factsheet(config, profile) -> dict:
    """The factsheet body (header fields are added by the robot on publish)."""
    if profile.version.startswith("2."):
        return _build_factsheet_v2(config, profile)
    actions = _action_entries(profile)
    return {
        "typeSpecification": {
            "seriesName": config.series_name,
            "seriesDescription": "Emulated VDA 5050 mobile robot (amr-emulator)",
            # Upstream schema bug at tag 3.0.0: `required` lists
            # `mobileRobotKinematic` while the defined property (and the PDF
            # table) is `mobileRobotKinematics`. Both keys are published so
            # the factsheet validates against the schema as released.
            "mobileRobotKinematics": "DIFFERENTIAL",
            "mobileRobotKinematic": "DIFFERENTIAL",
            "mobileRobotClass": "CARRIER",
            "maximumLoadMass": 250.0,
            "localizationTypes": ["NATURAL"],
            "navigationTypes": ["VIRTUAL_LINE_GUIDED"],
            "supportedZones": list(SUPPORTED_ZONES),
        },
        "physicalParameters": {
            "minimumSpeed": 0.05,
            "maximumSpeed": config.max_speed,
            "minimumAngularSpeed": 0.05,
            "maximumAngularSpeed": 1.5,
            "maximumAcceleration": 0.8,
            "maximumDeceleration": 1.2,
            "minimumHeight": 0.3,
            "maximumHeight": 0.3,
            "width": 0.6,
            "length": 0.9,
        },
        "protocolLimits": {
            "maximumStringLengths": {
                "maximumMessageLength": 1_000_000,
                "maximumIdLength": 255,
                "idNumericalOnly": False,
                "maximumLoadIdLength": 255,
            },
            "maximumArrayLengths": {
                "order.nodes": MAX_ORDER_NODES,
                "order.edges": MAX_ORDER_EDGES,
            },
            "timing": {
                "minimumOrderInterval": 0.1,
                "minimumStateInterval": config.min_state_interval,
                "defaultStateInterval": config.default_state_interval,
                "visualizationInterval": config.visualization_interval or 1.0,
            },
        },
        "protocolFeatures": {
            "optionalParameters": [
                {"parameter": parameter, "support": "SUPPORTED"}
                for parameter in SUPPORTED_OPTIONAL_PARAMETERS
            ],
            "mobileRobotActions": actions,
        },
        "mobileRobotGeometry": {
            "wheelDefinitions": [
                {
                    "type": "DRIVE",
                    "isActiveDriven": True,
                    "isActiveSteered": False,
                    "position": {"x": 0.0, "y": side * 0.25, "theta": 0.0},
                    "diameter": 0.15,
                    "width": 0.05,
                }
                for side in (-1, 1)
            ],
            "envelopes2d": [
                {
                    "envelope2dId": "contour",
                    "vertices": [
                        {"x": 0.45, "y": 0.3},
                        {"x": -0.45, "y": 0.3},
                        {"x": -0.45, "y": -0.3},
                        {"x": 0.45, "y": -0.3},
                    ],
                    "description": "Mechanical outline, unloaded",
                }
            ],
        },
        "loadSpecification": {
            "loadPositions": ["deck"],
            "loadSets": [
                {
                    "setName": "DEFAULT",
                    "loadType": "EPAL",
                    "loadPositions": ["deck"],
                    "maximumWeight": 250.0,
                    "pickTime": 4.0,
                    "dropTime": 3.0,
                }
            ],
        },
        "mobileRobotConfiguration": {
            "versions": [
                {"key": "softwareVersion", "value": config.software_version},
                {"key": "emulator", "value": "amr-emulator/vda5050-emulator"},
            ],
        },
    }


_CONTOUR = [
    {"x": 0.45, "y": 0.3},
    {"x": -0.45, "y": 0.3},
    {"x": -0.45, "y": -0.3},
    {"x": 0.45, "y": -0.3},
]


def _wheels() -> list[dict]:
    return [
        {
            "type": "DRIVE",
            "isActiveDriven": True,
            "isActiveSteered": False,
            "position": {"x": 0.0, "y": side * 0.25, "theta": 0.0},
            "diameter": 0.15,
            "width": 0.05,
        }
        for side in (-1, 1)
    ]


def _geometry_v2() -> dict:
    # 2.x names the envelope fields `set`/`polygonPoints`.
    return {
        "wheelDefinitions": _wheels(),
        "envelopes2d": [
            {
                "set": "contour",
                "polygonPoints": list(_CONTOUR),
                "description": "Mechanical outline, unloaded",
            }
        ],
    }


def _build_factsheet_v2(config, profile) -> dict:
    """The 2.x factsheet shape ("AGV" vocabulary, abbreviated field names)."""
    return {
        "typeSpecification": {
            "seriesName": config.series_name,
            "seriesDescription": "Emulated VDA 5050 AGV (amr-emulator)",
            "agvKinematic": "DIFF",
            "agvClass": "CARRIER",
            "maxLoadMass": 250.0,
            "localizationTypes": ["NATURAL"],
            "navigationTypes": ["VIRTUAL_LINE_GUIDED"],
        },
        "physicalParameters": {
            "speedMin": 0.05,
            "speedMax": config.max_speed,
            "accelerationMax": 0.8,
            "decelerationMax": 1.2,
            "heightMin": 0.3,
            "heightMax": 0.3,
            "width": 0.6,
            "length": 0.9,
        },
        "protocolLimits": {
            "maxStringLens": {"idLen": 255, "idNumericalOnly": False, "loadIdLen": 255},
            "maxArrayLens": {"order.nodes": MAX_ORDER_NODES, "order.edges": MAX_ORDER_EDGES},
            "timing": {
                "minOrderInterval": 0.1,
                "minStateInterval": config.min_state_interval,
                "defaultStateInterval": config.default_state_interval,
                "visualizationInterval": config.visualization_interval or 1.0,
            },
        },
        "protocolFeatures": {
            "optionalParameters": [
                {"parameter": parameter, "support": "SUPPORTED"}
                for parameter in SUPPORTED_OPTIONAL_PARAMETERS
            ],
            "agvActions": _action_entries(profile),
        },
        "agvGeometry": _geometry_v2(),
        "loadSpecification": {
            "loadPositions": ["deck"],
            "loadSets": [
                {
                    "setName": "DEFAULT",
                    "loadType": "EPAL",
                    "loadPositions": ["deck"],
                    "maxWeight": 250.0,
                    "pickTime": 4.0,
                    "dropTime": 3.0,
                }
            ],
        },
    }
