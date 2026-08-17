"""Embedded MQTT 3.1.1 stack (broker + client), stdlib-only.

VDA5050 rides on MQTT; bundling a small spec-faithful broker means the
emulator runs with zero external services — point any fleet control at it.
"""

from vda5050_emulator.mqtt.broker import Broker
from vda5050_emulator.mqtt.client import MQTTClient
from vda5050_emulator.mqtt.codec import Message, MQTTError

__all__ = ["Broker", "MQTTClient", "MQTTError", "Message"]
