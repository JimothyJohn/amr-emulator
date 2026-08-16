"""Asyncio MQTT 3.1.1 client.

Speaks plain MQTT over TCP, so it works against the embedded broker and
against external brokers (mosquitto, EMQX, cloud endpoints without TLS).
QoS 0/1 only, always clean-session — exactly what VDA5050 requires.
Inbound PUBLISHes are acknowledged (QoS 1) and queued on ``messages``.
"""

from __future__ import annotations

import asyncio
import itertools
import logging
from contextlib import suppress

from vda5050_emulator.mqtt import codec
from vda5050_emulator.mqtt.codec import Message, MQTTError

log = logging.getLogger(__name__)

_ACK_TIMEOUT_S = 10.0


class MQTTClient:
    def __init__(
        self,
        client_id: str,
        host: str,
        port: int,
        *,
        username: str | None = None,
        password: str | None = None,
        will: Message | None = None,
        keepalive: int = 60,
        max_packet_size: int = 1_048_576,
    ) -> None:
        self.client_id = client_id
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._will = will
        self._keepalive = keepalive
        self._max_packet_size = max_packet_size
        self.messages: asyncio.Queue[Message] = asyncio.Queue()
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._reader_task: asyncio.Task | None = None
        self._ping_task: asyncio.Task | None = None
        self._packet_ids = itertools.cycle(range(1, 0x10000))
        self._pending: dict[tuple[str, int], asyncio.Future] = {}
        self._write_lock = asyncio.Lock()
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
        connect = codec.Connect(
            client_id=self.client_id,
            keepalive=self._keepalive,
            clean_session=True,
            will_topic=self._will.topic if self._will else None,
            will_payload=self._will.payload if self._will else b"",
            will_qos=self._will.qos if self._will else 0,
            will_retain=self._will.retain if self._will else False,
            username=self._username,
            password=self._password.encode() if self._password is not None else None,
        )
        await self._send(connect)
        try:
            async with asyncio.timeout(_ACK_TIMEOUT_S):
                packet = await codec.read_packet(self._reader.readexactly, self._max_packet_size)
        except (asyncio.IncompleteReadError, TimeoutError) as exc:
            self._teardown()
            raise MQTTError("no CONNACK from broker") from exc
        if not isinstance(packet, codec.ConnAck):
            self._teardown()
            raise MQTTError(f"expected CONNACK, got {type(packet).__name__}")
        if packet.return_code != codec.CONNACK_ACCEPTED:
            self._teardown()
            raise MQTTError(f"connection refused (return code {packet.return_code})")
        self._connected = True
        self._reader_task = asyncio.create_task(self._read_loop())
        if self._keepalive:
            self._ping_task = asyncio.create_task(self._ping_loop())

    async def disconnect(self) -> None:
        """Graceful shutdown: DISCONNECT is sent, the broker discards the will."""
        if self._connected:
            with suppress(MQTTError, ConnectionError):
                await self._send(codec.Disconnect())
        await self._shutdown()

    async def drop(self) -> None:
        """Abrupt shutdown without DISCONNECT — the broker fires the last will."""
        await self._shutdown()

    async def publish(self, topic: str, payload: bytes, qos: int = 0, retain: bool = False) -> None:
        codec.validate_topic(topic)
        if qos not in (0, 1):
            raise MQTTError("qos must be 0 or 1")
        packet_id = next(self._packet_ids) if qos else None
        publish = codec.Publish(
            topic=topic, payload=payload, qos=qos, retain=retain, packet_id=packet_id
        )
        if qos and packet_id is not None:
            await self._request(("puback", packet_id), publish)
        else:
            await self._send(publish)

    async def subscribe(self, topic_filter: str, qos: int = 0) -> None:
        codec.validate_filter(topic_filter)
        packet_id = next(self._packet_ids)
        suback = await self._request(
            ("suback", packet_id),
            codec.Subscribe(packet_id=packet_id, topics=((topic_filter, qos),)),
        )
        assert isinstance(suback, codec.SubAck)
        if any(code == codec.SUBACK_FAILURE for code in suback.return_codes):
            raise MQTTError(f"subscription refused for {topic_filter!r}")

    async def unsubscribe(self, topic_filter: str) -> None:
        packet_id = next(self._packet_ids)
        await self._request(
            ("unsuback", packet_id), codec.Unsubscribe(packet_id=packet_id, topics=(topic_filter,))
        )

    async def _request(self, key: tuple[str, int], packet: codec.Packet) -> codec.Packet | None:
        future: asyncio.Future = asyncio.get_running_loop().create_future()
        self._pending[key] = future
        try:
            await self._send(packet)
            async with asyncio.timeout(_ACK_TIMEOUT_S):
                return await future
        except TimeoutError as exc:
            raise MQTTError(f"timed out waiting for {key[0]}") from exc
        finally:
            self._pending.pop(key, None)

    async def _send(self, packet: codec.Packet) -> None:
        if self._writer is None:
            raise MQTTError("not connected")
        data = codec.encode(packet)
        try:
            async with self._write_lock:
                self._writer.write(data)
                await self._writer.drain()
        except ConnectionError as exc:
            raise MQTTError("connection lost") from exc

    async def _read_loop(self) -> None:
        assert self._reader is not None
        try:
            while True:
                packet = await codec.read_packet(self._reader.readexactly, self._max_packet_size)
                match packet:
                    case codec.Publish():
                        log.debug("client %r received PUBLISH %r", self.client_id, packet.topic)
                        if packet.qos and packet.packet_id is not None:
                            await self._send(codec.PubAck(packet_id=packet.packet_id))
                        await self.messages.put(
                            Message(
                                topic=packet.topic,
                                payload=packet.payload,
                                qos=packet.qos,
                                retain=packet.retain,
                            )
                        )
                    case codec.PubAck():
                        self._resolve(("puback", packet.packet_id), packet)
                    case codec.SubAck():
                        self._resolve(("suback", packet.packet_id), packet)
                    case codec.UnsubAck():
                        self._resolve(("unsuback", packet.packet_id), packet)
                    case codec.PingResp():
                        pass
                    case _:
                        raise MQTTError(f"unexpected {type(packet).__name__} from broker")
        except (MQTTError, asyncio.IncompleteReadError, ConnectionError) as exc:
            log.debug("client %r read loop ended: %r", self.client_id, exc)
            self._teardown()
        except Exception:
            log.exception("client %r read loop died unexpectedly", self.client_id)
            self._teardown()
            raise

    async def _ping_loop(self) -> None:
        interval = max(1.0, self._keepalive / 2)
        with suppress(MQTTError, ConnectionError):
            while True:
                await asyncio.sleep(interval)
                await self._send(codec.PingReq())

    def _resolve(self, key: tuple[str, int], packet: codec.Packet) -> None:
        future = self._pending.get(key)
        if future is not None and not future.done():
            future.set_result(packet)

    async def _shutdown(self) -> None:
        self._teardown()
        for task in (self._reader_task, self._ping_task):
            if task is not None and task is not asyncio.current_task():
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
        self._reader_task = None
        self._ping_task = None

    def _teardown(self) -> None:
        self._connected = False
        if self._writer is not None:
            with suppress(ConnectionError, RuntimeError):
                self._writer.close()
            self._writer = None
        for future in self._pending.values():
            if not future.done():
                future.set_exception(MQTTError("connection closed"))
        self._pending.clear()
