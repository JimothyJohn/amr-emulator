"""Env-gated MQTT debug logging for chasing delivery races.

Set VDA5050_MQTT_DEBUG=/path/to/log to capture broker/client lifecycle and
routing decisions for every test in this package.
"""

from __future__ import annotations

import logging
import os


def pytest_configure(config):
    target = os.environ.get("VDA5050_MQTT_DEBUG")
    if not target:
        return
    handler = logging.FileHandler(target, mode="a")
    handler.setFormatter(
        logging.Formatter("%(asctime)s.%(msecs)03d %(name)s %(message)s", "%H:%M:%S")
    )
    for name in (
        "vda5050_emulator.mqtt.broker",
        "vda5050_emulator.mqtt.client",
        "mir_vda5050_adapter.adapter",
    ):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
